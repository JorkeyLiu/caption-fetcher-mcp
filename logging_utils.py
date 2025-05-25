import threading
import logging

_thread_local = threading.local()

class TestMethodFilter(logging.Filter):
    """Custom filter to add test method name to log records."""
    def filter(self, record):
        record.test_method = getattr(_thread_local, 'test_method_name', 'N/A')
        return True