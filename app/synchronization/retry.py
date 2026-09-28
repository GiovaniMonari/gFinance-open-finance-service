import asyncio

from app.synchronization.exceptions import RetryableSyncError


async def execute_with_retry(
    operation,
    max_attempts: int = 3,
):
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            return await operation()

        except RetryableSyncError as error:
            last_error = error

            if attempt == max_attempts:
                raise

            delay = 2 ** attempt

            print(
                f"Synchronization attempt {attempt} failed. "
                f"Retrying in {delay}s..."
            )

            await asyncio.sleep(delay)

        except Exception:
            raise

    raise last_error