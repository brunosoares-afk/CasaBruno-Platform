import subprocess
from app.config.android_devices import DEVICES
from app.core.android.device import AndroidDevice


class AndroidManager:
    def __init__(self):
        self.devices = {}
        for device_id, cfg in DEVICES.items():
            self.devices[device_id] = AndroidDevice(
                device_id,
                cfg["name"],
                cfg["host"]
            )

    def host(self, device_id):
        return self.devices[device_id].host

    def adb(self, *args, timeout=3):
        try:
            return subprocess.run(
                ["/usr/local/bin/adb", *args],
                capture_output=True,
                text=True,
                timeout=timeout
            ).stdout
        except subprocess.TimeoutExpired:
            return ""

    def connect_all(self):
        for device in self.devices.values():
            self.adb("connect", device.host, timeout=2)

    def list(self):
        self.connect_all()
        out = self.adb("devices", timeout=2)
        response = []
        for device in self.devices.values():
            status = "offline"
            if device.host in out and "device" in out:
                status = "online"
            response.append({
                **device.json(),
                "status": status
            })
        return response


android = AndroidManager()
