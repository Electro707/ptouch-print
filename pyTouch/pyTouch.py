"""
A wrapper around libptouch, allowing easy usage thru Python
"""
# import the swig generated file
from ptouchSwig import *
from enum import Enum


class PTouchConnection(Exception):
    """Raised when a connection error occured with a Ptouch device"""


class PTouch:
    def __init__(self):
        self.dev = ptouch_dev()

    def open(self):
        """
        Connects and initializes a PTouch label maker
        """
        if ptouch_open(self.dev) != 0:
            raise PTouchConnection()
        try:
            if ptouch_init(self.dev) != 0:
                raise PTouchConnection()
            # needed to get printer information, such as tape lenght, etc
            if ptouch_getstatus(self.dev) != 0:
                raise PTouchConnection()
        except PTouchConnection:
            self.close()
            raise

    def close(self):
        return ptouch_close(self.dev)

