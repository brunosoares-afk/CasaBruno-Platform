#!/usr/bin/env python3

from pathlib import Path

class Registry:

    def __init__(self):

        self.modules=[]
        self.plugins=[]
        self.services=[]

    def register_module(self,name):

        if name not in self.modules:
            self.modules.append(name)

    def register_plugin(self,name):

        if name not in self.plugins:
            self.plugins.append(name)

    def register_service(self,name):

        if name not in self.services:
            self.services.append(name)

    def discover_modules(self,root):

        path=Path(root)

        if not path.exists():
            return

        for item in sorted(path.iterdir()):

            if item.is_dir():

                self.register_module(item.name)
