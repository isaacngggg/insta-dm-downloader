from airportsearch import get_airport
from pricesearch import get_price
import re
import datetime

def get_preferred_date(userInputLocation, userInputDate):

    airportId = get_airport(userInputLocation)
    pricesList = get_price(airportId, "LHR", userInputDate, "USD")
    prices = []
    groups = []
    days = []

    for price in pricesList:
        days.append(price['day'])
        prices.append(price['price'])
        groups.append(price['group'])

    month_prices = {}

    for day, price, group in zip(days, prices, groups):
        if group == "low":
            month = re.search(r'\d{4}-(\d{2})', day).group(1)  # Extract month
            if month not in month_prices:
                month_prices[month] = {'total_price': 0, 'count': 0}
            month_prices[month]['total_price'] += price
            month_prices[month]['count'] += 1

    # Calculate average price for each month
    average_prices = {month: data['total_price'] / data['count'] for month, data in month_prices.items()}

    # Step 3: Identify 3 cheapest months
    cheapest_months = sorted(average_prices, key=average_prices.get)[:3]

    # Print suggestions
    for month in cheapest_months:
        print(f"Month: {month}, Average Price: {average_prices[month]:.2f}")
    
    return cheapest_months, average_prices

def main():
    userInputLocation = "New York"
    today = datetime.date.today().strftime("%Y-%m-%d")
    cheapest_months,average_prices = get_preferred_date(userInputLocation, today)
    print ('running the main function of skyscraper.py')

if __name__ == "__main__":
    main()
