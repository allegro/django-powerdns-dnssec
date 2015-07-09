import requests
import unittest


def wrap_requests_function(fun):
    def result(self, *args, **kwargs):
        kwargs['auth'] = ('dnsaas', 'dnsaas')
        return fun(*args, **kwargs)
    result.__name__ = fun.__name__

    return result


class TestBase(unittest.TestCase):
    """Base class for integration tests."""

    get = wrap_requests_function(requests.get)
    post = wrap_requests_function(requests.post)
    delete = wrap_requests_function(requests.delete)
