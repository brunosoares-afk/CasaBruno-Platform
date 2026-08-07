#!/usr/bin/env python3

from core.config import Config
from core.runtime import Runtime
from core.registry import Registry

class CBOSKernel:

    def __init__(self):

        self.config=Config()
        self.runtime=Runtime()
        self.registry=Registry()

    def boot(self):

        self.registry.discover_modules("/opt/CasaBruno-Platform/modules")
        self.registry.register_service("api")
        self.registry.register_service("fred")
        self.registry.register_plugin("homeassistant")

        print()
        print("========================================")
        print("         CBOS KERNEL BOOT")
        print("========================================")
        print()

        print("Modules :",len(self.registry.modules))
        print("Services:",len(self.registry.services))
        print("Plugins :",len(self.registry.plugins))
        print()

    def info(self):

        print("Platform :",self.config.ROOT)
        print("Version  :",self.config.VERSION)
        print("AI       :",self.config.AI)
        print("Runtime  :",self.runtime.uptime())

        print()
        print("Loaded Modules")

        for module in self.registry.modules:
            print(" -",module)

        print()

    def shutdown(self):

        print("Kernel shutdown.")
