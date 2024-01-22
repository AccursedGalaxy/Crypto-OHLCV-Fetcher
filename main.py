import asyncio
import os
import sys
from datetime import datetime

# Adjust the path to include the 'app' directory where your modules are located
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

# Import ccxt or any other necessary libraries
import ccxt.async_support as ccxt

from app.fetcher import fetch_ohlcv
from app.logger import logger


async def main():
    # Example usage
    exchange = ccxt.binance()  # Or any other exchange
    symbol = "BTC/USDT"
    timeframe = "1d"

    # Convert string dates to datetime objects
    start_date_str = "2021-01-01T00:00:00Z"
    end_date_str = "2021-12-31T00:00:00Z"
    start_date = datetime.fromisoformat(start_date_str[:-1])
    end_date = datetime.fromisoformat(end_date_str[:-1])

    csv_file_path = "data"  # Example CSV file path

    await fetch_ohlcv(exchange, symbol, timeframe, start_date, end_date, csv_file_path)


if __name__ == "__main__":
    asyncio.run(main())
