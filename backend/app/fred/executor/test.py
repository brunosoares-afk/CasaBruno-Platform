import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from executor.executor import executor

print(executor.execute("LightService"))
print(executor.execute("WeatherService"))
print(executor.execute("DockerService"))
print(executor.execute("NetworkService"))
print(executor.execute("HomeAssistantService"))
print(executor.execute("FallbackService"))
