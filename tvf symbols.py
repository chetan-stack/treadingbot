from tvDatafeed import TvDatafeed


def search_symbols(search_query, exchange=None):
    """
    Searches for symbols in TradingView's datafeed and returns matching details.

    Args:
        search_query (str): The search keyword to look for symbols.
        exchange (str, optional): The specific exchange to filter the search results. Default is None.

    Returns:
        list of dict: A list of dictionaries containing 'symbol', 'exchange', and 'script' information.
    """
    try:
        # Initialize tvDatafeed (guest login)
        tv = TvDatafeed()

        # Fetch symbol search results
        symbols = tv.search(search_query)

        # Filter by exchange if provided
        if exchange:
            symbols = [sym for sym in symbols if sym['exchange'].lower() == exchange.lower()]

        # Extract and return relevant details
        result = [{'symbol': sym['symbol'], 'exchange': sym['exchange'], 'script': sym['full_name']} for sym in symbols]

        return result

    except Exception as e:
        print(f"Error occurred while searching symbols: {e}")
        return []


# Example usage
search_results = search_symbols('TCS', exchange='NSE')
for res in search_results:
    print(res)
