import time

class Scheduler:

    def __init__(self):
        self.jobs=[]

    def add(self,name,interval):
        self.jobs.append({
            "name":name,
            "interval":interval
        })

    def list(self):
        return self.jobs

scheduler=Scheduler()
