import logging

class Logs:
    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def get_logger(self):
        return self.logger