#!/usr/bin/env python3

from datetime import datetime

class Runtime:

    def __init__(self):

        self.started = datetime.now()

    def uptime(self):

        return datetime.now() - self.started
