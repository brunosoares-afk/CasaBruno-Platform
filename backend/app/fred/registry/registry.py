class DeviceRegistry:

    def __init__(self):
        self.devices={}

    def add(self,name,ip,kind):
        self.devices[name]={
            "ip":ip,
            "type":kind
        }

    def get(self,name):
        return self.devices.get(name)

    def all(self):
        return self.devices

registry=DeviceRegistry()
