# limiter.py
import asyncio
import logging

import ccxt.async_support as ccxt

logger = logging.getLogger("BitFetch")


async def rate_limit_handler(func, *args, retries=10, delay=2, max_delay=60):
    while retries > 0:
        try:
            # Check if func is a coroutine function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args)
            else:
                result = func(*args)

            return result
        except ccxt.RateLimitExceeded as e:
            wait_time = min(delay, max_delay)
            logger.error(
                f"Rate limit exceeded: {e}. Retrying in {wait_time} seconds..."
            )
            await asyncio.sleep(wait_time)
            logger.info("Retrying...")
            delay *= 2  # Exponential backoff
            logger.info(f"New delay: {delay}")
            retries -= 1
            logger.info(f"Retries left: {retries}")
    logger.error("Failed after retries.")
    return None
