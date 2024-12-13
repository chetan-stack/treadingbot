import requests
from bs4 import BeautifulSoup

# Fetch webpage
url = "https://dhan.co/nifty-stocks-list/nifty-50/"
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the table containing stock data
    table = soup.find("table", {"class": "table"})
    print(table)
    # Check if the table was found
    if table:
        tbody = table.find("tbody")
        print(tbody)
        # Initialize lists to store stock data
        nifty_stocks = []

        # Extract data from table rows
        for row in table.find_all("tbody"):  # Skip header row
            columns = row.find_all("td")
            stock_name = columns[0].text.strip()
            print(columns)

            weight = float(columns[1].text.strip())
            change_in_ltp = float(columns[5].text.strip())  # Assuming change in LTP is in the 6th column
            nifty_stocks.append({"stock": stock_name, "weight": weight, "change_in_ltp": change_in_ltp})

        # Calculate weighted change for each stock
        weighted_changes = [stock["weight"] * stock["change_in_ltp"] for stock in nifty_stocks]

        # Calculate overall change in Nifty 50
        overall_change = sum(weighted_changes)

        # Determine direction
        if overall_change > 0:
            direction = "upward"
        elif overall_change < 0:
            direction = "downward"
        else:
            direction = "stable"

        print("Nifty 50 direction:", direction)
    else:
        print("Table not found on the webpage.")
else:
    print(f"Failed to fetch the webpage. Status code: {response.status_code}")
