import psutil
from roadman_mind.core.plugins import Plugin
from typing import Dict, Callable, Any

class SystemToolsPlugin(Plugin):
    @property
    def name(self) -> str:
        return "sys"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Provides basic system monitoring tools using psutil."

    def routes(self) -> Dict[str, Callable]:
        return {
            "cpu_percent": self.get_cpu_percent,
            "memory": self.get_memory_usage,
        }

    def get_cpu_percent(self) -> str:
        """Returns the current overall CPU usage as a percentage."""
        return f"CPU Usage: {psutil.cpu_percent(interval=1)}%"

    def get_memory_usage(self) -> Dict[str, Any]:
        """Returns virtual memory statistics as a dictionary."""
        mem = psutil.virtual_memory()
        return {
            "total": f"{mem.total / (1024**3):.2f} GB",
            "available": f"{mem.available / (1024**3):.2f} GB",
            "percent_used": f"{mem.percent}%",
        }
