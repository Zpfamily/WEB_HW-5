import aiohttp
import asyncio
from datetime import datetime, timedelta


async def fetch_exchange_rates(date):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}') as response:
            if response.status == 200:
                result = await response.json()
                return result
            else:
                return None

async def get_exchange_rates_for_last_n_days():
    today = datetime.now()
    while True:
        try:
            number_days = int(input("For how many days do you want to get results (maximum 10): "))
            if 0 < number_days <= 10:
                break
            else:
                print("Please enter a number between 1 and 10.")
        except ValueError:
            print("Please enter a valid integer.")
        
    date_list = [today - timedelta(days=x) for x in range(int(number_days))]
    
    tasks = [fetch_exchange_rates(date.strftime('%d.%m.%Y')) for date in date_list]
    
    return await asyncio.gather(*tasks)

def format_exchange_rates(rates):
    formatted_result = []
    
    for i, rate in enumerate(rates):
        date = (datetime.now() - timedelta(days=i)).strftime('%d.%m.%Y')
        if rate is not None and 'exchangeRate' in rate:
            exchange_rate = rate['exchangeRate']
            if isinstance(exchange_rate, list) and len(exchange_rate) > 0:
                eur_rate = next((c for c in exchange_rate if c['currency'] == 'EUR'), None)
                usd_rate = next((c for c in exchange_rate if c['currency'] == 'USD'), None)

                date_dict = {date: {}}

                if eur_rate is not None:
                    date_dict[date]['EUR'] = {
                        'sale': eur_rate.get('saleRate', 'N/A'),
                        'purchase': eur_rate.get('purchaseRate', 'N/A')
                    }

                if usd_rate is not None:
                    date_dict[date]['USD'] = {
                        'sale': usd_rate.get('saleRate', 'N/A'),
                        'purchase': usd_rate.get('purchaseRate', 'N/A')
                    }

                formatted_result.append(date_dict)
            else:
                print(f"Error: Unexpected data structure for date {date}")
        else:
            print(f"Error fetching data for date {date}")

    return formatted_result

def print_exchange_rates(rates):
    formatted_result = format_exchange_rates(rates)
    for i in formatted_result:
        print(i)
 

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    rates = loop.run_until_complete(get_exchange_rates_for_last_n_days())
    print_exchange_rates(rates)
