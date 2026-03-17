import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: integration tests")
