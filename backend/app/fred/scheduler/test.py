from scheduler import scheduler

scheduler.add("health-check",30)
scheduler.add("docker-scan",60)
scheduler.add("ha-sync",120)

print(scheduler.list())
