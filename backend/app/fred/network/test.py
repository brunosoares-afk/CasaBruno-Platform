from client import network

print("Gateway :",network.ping("192.168.15.1"))
print("HA      :",network.ping("192.168.15.10"))
print("Google  :",network.ping("8.8.8.8"))
