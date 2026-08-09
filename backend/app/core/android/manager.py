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
                cfg["host"],
                cfg.get("mac")
            )

    def host(self, device_id):
        return self.devices[device_id].host

    def mac(self, device_id):
        return self.devices[device_id].mac

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
        lines = out.splitlines()
        response = []
        for device in self.devices.values():
            status = "offline"
            for line in lines:
                parts = line.split()
                if len(parts) >= 2 and parts[0] == device.host and parts[1] == "device":
                    status = "online"
                    break
            response.append({
                **device.json(),
                "status": status
            })
        return response


android = AndroidManager()
