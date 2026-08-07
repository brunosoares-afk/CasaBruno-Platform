from datetime import datetime


class Logger:

    def __init__(self):

        self.logs = []

    def write(self, level, source, message):

        item = {

            "timestamp": datetime.now().isoformat(),

            "level": level.upper(),

            "source": source,

            "message": message

        }

        self.logs.append(item)

        if len(self.logs) > 5000:

            self.logs.pop(0)

        return item

    def info(self, source, message):

        return self.write("INFO", source, message)

    def warning(self, source, message):

        return self.write("WARNING", source, message)

    def error(self, source, message):

        return self.write("ERROR", source, message)

    def latest(self, limit=100):

        return self.logs[-limit:]


logger = Logger()
