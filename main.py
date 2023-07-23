import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
import sys

currencies_list = ['EUR', 'USD']


class APIRequester:
    def __init__(self, url):
        self.url = url

    async def request(self, session, date):
        try:
            async with session.get(f"{self.url}{date}") as response:
                if response.status == 200:
                    return await response.json()
                logging.error(f"Error status {response.status} for {self.url}")
                return None
        except aiohttp.ClientConnectionError as err:
            logging.error(f"Connection error {str(err)}")
            return None


class ExchangeRateParser:
    def __init__(self, currencies_list):
        self.currencies_list = currencies_list

    def parse_exchange(self, result):
        if result:
            exchange_date = result.get("date")
            print(f"{exchange_date}")
            print('*'*15)
            temp = result.get("exchangeRate")
            for course in temp:
                if course.get('currency') in self.currencies_list:
                    print(f"{course.get('currency')}:\nsale: {course.get('saleRate')} UAH"
                          f"\npurchase: {course.get('purchaseRate')} UAH\n")
            print('*'*15)


class ExchangeRatePrinter:
    API_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

    def print_exchange_rates(self, currencies_list):
        if len(sys.argv) <= 2:
            print("Usage: python script_name.py days_count")
            sys.exit(1)
        try:
            days_count = int(sys.argv[1])
        except ValueError:
            print("Error: days_count should be an integer.")
            sys.exit(1)

        additional_currencies = sys.argv[2:]
        currencies_list.extend(additional_currencies)

        date_list = self.get_date_list(days_count)
        asyncio.run(self.get_exchange(date_list))

    def get_date_list(self, days_count):
        if days_count > 10:
            logging.warning(f"The number of days should not exceed 10, and {days_count} were received!"
                            f"\nResults shown for 10 days.")
            days_count = 10

        now = datetime.now().date()
        result = [(now - timedelta(days=i)).strftime("%d.%m.%Y") for i in range(days_count)]
        return result

    async def get_exchange(self, date_list):
        async with aiohttp.ClientSession() as session:
            api_requester = APIRequester(self.API_URL)
            tasks = [api_requester.request(session, date) for date in date_list]
            results = await asyncio.gather(*tasks)

            exchange_rate_parser = ExchangeRateParser(currencies_list)
            for result in results:
                exchange_rate_parser.parse_exchange(result)


if __name__ == '__main__':
    exchange_rate_printer = ExchangeRatePrinter()
    exchange_rate_printer.print_exchange_rates(currencies_list)
