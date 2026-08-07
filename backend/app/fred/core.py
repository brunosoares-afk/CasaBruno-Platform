class FRED:

    VERSION="1.0.0"

    NAME="Friendly Responsive Executive Device"

    def start(self):
        return {
            "status":"online",
            "ai":"FRED",
            "version":self.VERSION
        }

fred=FRED()
