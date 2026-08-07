from session import session

session.open("Bruno")
session.open("CasaBruno")

print(session.status("Bruno"))

session.close("Bruno")

print(session.status("Bruno"))
print(session.list())
