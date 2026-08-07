from context import context

context.set("user","Bruno")
context.set("location","Casa")
context.set("mode","automation")

print(context.get("user"))
print(context.dump())
