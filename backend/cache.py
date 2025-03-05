import logging
import time
from threading import Lock

class CachedData:
    _logger = logging.getLogger(__name__)

    def __init__(self, cache_duration_seconds: int = 30):
        self.data = None
        self.cache_duration_seconds = cache_duration_seconds
        self.last_updated = time.monotonic() - self.cache_duration_seconds
        self.active_update_start_time = 0
        self.lock = Lock()
        self.cache_status = 'VALID'  # Add cache status field

    def __enter__(self):
        self.lock.acquire()
        return self 

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit method properly implemented with required parameters"""
        assert(self.lock.locked())
        self.lock.release()

    def is_expired(self) -> bool:
        assert(self.lock.locked())
        cache_age_seconds = time.monotonic() - self.last_updated
        if cache_age_seconds < self.cache_duration_seconds:
            CachedData._logger.debug("Cache not expired.")
            return False
        
        CachedData._logger.debug("Cache expired, managing thread-safe updates.")
        
        if self.active_update_start_time != 0:
            if time.monotonic() - self.active_update_start_time >= 2 * self.cache_duration_seconds:
                CachedData._logger.debug("Update in progress, but taking too long. Consider it expired to force refresh.")
                self.active_update_start_time = 0
                self.cache_status = 'EXPIRED'
                return True
            else:
                if self.data is None:
                    CachedData._logger.debug("Update in progress, but no existing data, so caller will just have to wait. Flag as expired.")
                    self.cache_status = 'WAITING'
                    return True
                else:
                    CachedData._logger.debug("Update in progress, but have existing data, so caller can use it. Logically not expired.")
                    self.cache_status = 'VALID'
                    return False
                
        CachedData._logger.debug("Cache expired, no update in progress, so fully expired.")
        self.cache_status = 'EXPIRED'
        return True

    def update(self, data: any):
        """Update cache data with new value"""
        try:
            assert(self.lock.locked())
            self.data = data
            self.active_update_start_time = 0
            self.last_updated = time.monotonic()
            self.cache_status = 'VALID'
        except AssertionError:
            CachedData._logger.error("Attempted to update cache without lock")
            self.lock.acquire()
            self.update(data)
            self.lock.release()


    def get_data(self) -> any:
        assert(self.lock.locked())
        return self.data

    def invalidate_cache(self):
        """ Manually invalidate cache if needed """
        self.cache_status = 'EXPIRED'
        self.data = None
        CachedData._logger.debug("Cache manually invalidated.")

    def adjust_cache_duration(self, new_duration: int):
        """ Dynamically adjust cache expiration duration """
        self.cache_duration_seconds = new_duration
        CachedData._logger.debug(f"Cache duration adjusted to {new_duration} seconds.")


class CacheUpdateManager:
    def __init__(self, cached_data: CachedData):
        self.cached_data = cached_data
        self.update_already_started = False

    def __enter__(self):
        """Ensure lock is held when entering context"""
        if not self.cached_data.lock.locked():
            self.cached_data.lock.acquire()
        self.update_already_started = self.cached_data.active_update_start_time != 0
        if self.cached_data.active_update_start_time == 0:
            self.cached_data.active_update_start_time = time.monotonic()
        self.cached_data.lock.release()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure proper lock handling on exit"""
        if not self.cached_data.lock.locked():
            self.cached_data.lock.acquire()
        self.cached_data.active_update_start_time = 0

    def update_started_elsewhere(self) -> bool:
        return self.update_already_started
    
    def spin_wait_for_update_to_complete(self):
        """ New feature: introduces a maximum wait timeout """
        max_wait_time = 5  # Seconds
        elapsed_time = 0
        assert(self.update_started_elsewhere())
        
        while True:
            update_still_in_progress = False
            self.cached_data.lock.acquire()
            update_still_in_progress = self.cached_data.active_update_start_time != 0
            self.cached_data.lock.release()
            
            if not update_still_in_progress:
                break

            if elapsed_time >= max_wait_time:
                CachedData._logger.warning("Maximum wait time exceeded while waiting for update to complete.")
                break

            time.sleep(0.1)
            elapsed_time += 0.1
