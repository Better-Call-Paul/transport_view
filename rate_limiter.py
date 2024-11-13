import redis
from redis.exceptions import LockError
import sys
from datetime import timedelta

def check_allowed(self, key: str, limit: int, period: timedelta) -> bool:
    """
    Returns whether a request should be allowed

    This implementation is modified from https://dev.to/astagi/rate-limiting-using-python-and-redis-58gk

    1. uses higher precision floats instead of ints
    2. returns true for allowing instead of returning true for rejecting

    This rate limiter follows the GCRA algorithm
    """

    period_in_seconds = int(period.total_seconds())
    now = self._get_redis_time_now()

    separation = period_in_seconds / limit
    self.redis.setnx(key, 0)
    try:
        with self.redis.lock(
            "rate_limiter_lock:" + key,
            blocking_timeout=self.REDIS_RATE_LIMITER_LOCK_TIMEOUT,
        ):
            tat = max(float(self.redis.get(key) or now), now)
            if tat - now <= period_in_seconds - separation:
                new_tat = max(tat, now) + separation
                self.redis.set(name=key, value=new_tat, ex=self.DEFAULT_TTL)
                return True
            return False
    except LockError:
        return False



