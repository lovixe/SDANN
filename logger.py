import logging
import time

class Logger(object):
    _instance = {}
    def __init__(self) -> None:
        self.logger = logging.getLogger('sdann')
        self.logger.setLevel(level=logging.DEBUG)
        fileName = time.strftime("%m-%d %H.%M.%S" + ".txt")
        self.handle = logging.FileHandler(fileName)
        self.handle.setLevel(logging.DEBUG)

        self.formatter = logging.Formatter('%(asctime)s - %(message)s')
        self.handle.setFormatter(self.formatter)

        self.logger.addHandler(self.handle)

logger = Logger()