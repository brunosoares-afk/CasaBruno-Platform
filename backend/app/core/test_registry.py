from registry import registry

registry.register("teste", object())

print(registry.exists("teste"))
print(registry.list())
print(registry.get("teste") is not None)

registry.unregister("teste")

print(registry.exists("teste"))
