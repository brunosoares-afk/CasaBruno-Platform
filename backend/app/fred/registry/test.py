from registry import registry

registry.add("HomeAssistant","192.168.15.10","ha")
registry.add("Mikrotik","192.168.15.1","router")
registry.add("NAS","192.168.15.20","storage")

print(registry.get("HomeAssistant"))
print(registry.get("Mikrotik"))
print(registry.all())
