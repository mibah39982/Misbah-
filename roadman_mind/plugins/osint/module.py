import json
from pathlib import Path
from roadman_mind.core.plugins import Plugin
from typing import Dict, Callable, Any, List

class OsintPlugin(Plugin):
    """
    A plugin to simulate OSINT operations by reading from a local CVE database.
    """
    def __init__(self):
        self.cve_data = self._load_cve_data()

    @property
    def name(self) -> str:
        return "osint"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Simulates OSINT tools by providing access to a local sample CVE database."

    def _load_cve_data(self) -> Dict[str, Any]:
        """Loads sample CVE data from the accompanying JSON file."""
        cve_file = Path(__file__).parent / "sample_cves.json"
        try:
            with cve_file.open("r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"error": "Could not load or parse sample_cves.json."}

    def routes(self) -> Dict[str, Callable]:
        """
        Exposes routes to list all CVEs and get details for a specific CVE.
        It dynamically creates a 'get' route for each CVE in the data file.
        """
        routes_map = {
            "list_cves": self.list_cves,
        }

        # Create a specific route for each CVE, e.g., 'get_cve_2025_0001'
        if isinstance(self.cve_data, dict):
            for cve_id in self.cve_data:
                route_name = f"get_{cve_id.lower().replace('-', '_')}"
                # Use a lambda with a default argument to capture the correct cve_id
                routes_map[route_name] = lambda cid=cve_id: self.get_cve(cid)

        return routes_map

    def list_cves(self) -> List[str]:
        """Returns a list of all available CVE IDs from the sample data."""
        if isinstance(self.cve_data, dict) and "error" not in self.cve_data:
            return list(self.cve_data.keys())
        return []

    def get_cve(self, cve_id: str) -> Dict[str, Any]:
        """Returns information about a specific CVE by its ID."""
        return self.cve_data.get(cve_id, {"error": f"CVE '{cve_id}' not found."})
