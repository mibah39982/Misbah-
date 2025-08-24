import unittest
import subprocess
import sys
import os

class TestSmoke(unittest.TestCase):
    """
    A simple smoke test suite to ensure the application is installable and runnable.
    """

    def test_core_imports(self):
        """
        Test that essential modules can be imported without raising errors.
        """
        try:
            from roadman_mind import main
            from roadman_mind.core import plugins, logger, config
            from roadman_mind.ui import server
        except ImportError as e:
            self.fail(f"A core module failed to import: {e}")

    def test_cli_list_routes_command_runs(self):
        """
        Test that the CLI's `list-routes` command executes and exits cleanly.
        This is a good indicator that plugins are loading correctly.
        """
        # We need to ensure the project root is in the Python path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env = os.environ.copy()
        env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

        command = [sys.executable, "-m", "roadman_mind", "list-routes"]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,  # Fail if exit code is non-zero
                env=env,
                timeout=30 # Add a timeout to prevent hangs
            )

            # Check that the output contains expected route names
            self.assertIn("sys:cpu_percent", result.stdout, "Expected 'sys:cpu_percent' route to be listed.")
            self.assertIn("osint:list_cves", result.stdout, "Expected 'osint:list_cves' route to be listed.")
            self.assertIn("lab:quiz_count", result.stdout, "Expected 'lab:quiz_count' route to be listed.")
            self.assertNotIn("Error", result.stderr, f"CLI command produced an error: {result.stderr}")

        except FileNotFoundError:
            self.fail(f"Could not find the Python executable at '{sys.executable}'.")
        except subprocess.TimeoutExpired:
            self.fail("The CLI command timed out.")
        except subprocess.CalledProcessError as e:
            self.fail(
                f"The CLI command `{' '.join(command)}` failed with exit code {e.returncode}.\n"
                f"--- STDOUT ---\n{e.stdout}\n"
                f"--- STDERR ---\n{e.stderr}"
            )

if __name__ == '__main__':
    unittest.main()
