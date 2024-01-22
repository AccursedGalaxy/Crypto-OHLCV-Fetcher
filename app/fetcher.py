# fetcher.py
import csv
import logging
import os
import sys

import ccxt.async_support as ccxt
from config import LIMIT
from limiter import rate_limit_handler

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger("BitFetch")


async def save_to_csv(data, file_path, file_name):
    """
    Saves the given data to a CSV file at the specified file path and file name.
    """
    # Construct the full file path
    full_path = os.path.join(file_path, f"{file_name}.csv")

    try:
        with open(full_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Open", "High", "Low", "Close", "Volume"])
            for row in data:
                writer.writerow(row)
        logger.info(f"Data successfully saved to {full_path}")
    except Exception as e:
        logger.error(f"Error saving data to CSV: {e}")


async def fetch_data(exchange, symbol, timeframe, since, limit=LIMIT):
    return await exchange.fetch_ohlcv(symbol, timeframe, since, limit=limit)


async def fetch_ohlcv(
    exchange, symbol, timeframe, start_date, end_date=None, csv_file_path=None
):
    try:
        if not csv_file_path:
            raise ValueError("CSV file path must be provided")

        since = exchange.parse8601(start_date.isoformat())
        end = exchange.parse8601(end_date.isoformat()) if end_date else None

        all_data = []

        while True:
            logger.info(f"Fetching {exchange.id} {symbol} {timeframe} {since}")
            new_data = await rate_limit_handler(
                fetch_data, exchange, symbol, timeframe, since
            )
            if not new_data:
                break

            all_data.extend(new_data)

            if len(new_data) < LIMIT or (end and new_data[-1][0] >= end):
                break

            since = new_data[-1][0] + 1

        logger.info(
            f"Completed fetching data for {exchange.id} {symbol} {timeframe}. Saving to CSV."
        )
        # Sort by timestamp and convert to human-readable format
        all_data.sort(key=lambda x: x[0])
        all_data = [
            [
                exchange.iso8601(timestamp),
                open_price,
                high_price,
                low_price,
                close_price,
                volume,
            ]
            for timestamp, open_price, high_price, low_price, close_price, volume in all_data
        ]
        # Save to CSV
        file_name = f"{exchange.id}_{symbol.replace('/', '')}_{timeframe}_{start_date.strftime('%Y%m%d')}"
        await save_to_csv(all_data, csv_file_path, file_name)

    except ccxt.ExchangeError as e:
        logger.error(f"Exchange error fetching OHLCV for {exchange.id} {symbol}: {e}")
    except ccxt.RequestTimeout as e:
        logger.error(f"Request timeout fetching OHLCV for {exchange.id} {symbol}: {e}")
    except ccxt.NetworkError as e:
        logger.error(f"Network error fetching OHLCV for {exchange.id} {symbol}: {e}")
    except Exception as e:
        error_message = str(e) if str(e).strip() else "Unknown error"
        logger.error(
            f"Error fetching OHLCV for {exchange.id} {symbol}: {error_message}"
        )
