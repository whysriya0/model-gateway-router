
import asyncio
import random
import time
import httpx


def is_retryable(error):
    # Network and timeout errors
    if isinstance(error, httpx.TransportError):
        return True

    # Provider returned an HTTP error
    if isinstance(error, httpx.HTTPStatusError):
        status = error.response.status_code

        return status in {408, 429, 500, 502, 503, 504}

    return False


async def retry_request(operation, max_attempts=3):

    for attempt in range(max_attempts):

        try:
            return await operation()

        except httpx.HTTPError as error:

            # Stop if this error should not be retried
            if not is_retryable(error):
                raise

            # Stop after the final attempt
            if attempt == max_attempts - 1:
                raise

            # Exponential backoff with jitter
            delay = min(8, 2 ** attempt)
            delay += random.uniform(0, 0.5)

            print(f"Retrying after {delay:.2f} seconds")

            await asyncio.sleep(delay)

class CircuitBreaker:

    def __init__(self, failure_limit=3, cooldown=30):
        self.failure_limit = failure_limit
        self.cooldown = cooldown

        self.failures = 0
        self.state = "closed"
        self.opened_at = 0

    def allow_request(self):

        if self.state == "closed":
            return True

        if self.state == "open":

            elapsed = time.monotonic() - self.opened_at

            if elapsed >= self.cooldown:
                self.state = "half-open"
                return True

            return False

        # The basic version permits a trial in half-open
        return True

    def record_success(self):
        self.failures = 0
        self.state = "closed"

    def record_failure(self):
        self.failures += 1

        if (
            self.failures >= self.failure_limit
            or self.state == "half-open"
        ):
            self.state = "open"
            self.opened_at = time.monotonic()

class TokenBucket:

    def __init__(self, rate=2, capacity=5):

        self.rate = rate
        self.capacity = capacity

        self.tokens = float(capacity)
        self.last_updated = time.monotonic()

    def allow_request(self):

        now = time.monotonic()
        elapsed = now - self.last_updated

        # Refill tokens according to elapsed time
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.rate
        )

        self.last_updated = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True

        return False

async def request_with_fallback(
    req,
    provider,
    primary_model,
    fallback_model
):
    try:
        result = await retry_request(
            lambda: provider.complete(req, primary_model)
        )

        return result, False

    except httpx.HTTPError as error:

        if not is_retryable(error):
            raise

        print("Primary failed. Trying fallback.")

        result = await retry_request(
            lambda: provider.complete(req, fallback_model)
        )

        return result, True
