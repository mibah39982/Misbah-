import typer
from rich.console import Console
from rich.table import Table
import logging

from roadman_mind.core.logger import setup_logger
from roadman_mind.core.plugins import load_plugins, get_all_routes, PLUGIN_REGISTRY

# Initialize the logger
setup_logger()
logger = logging.getLogger("roadman_mind")

# Create a Typer app and a Rich Console
app = typer.Typer(
    name="roadman-mind",
    help="A safe, educational cyber-hacker-themed AI assistant framework.",
    add_completion=False,
)
console = Console()

# --- State variable to ensure plugins are loaded only once ---
_plugins_loaded = False

def bootstrap():
    """
    Initializes the application: loads plugins. This function ensures that
    plugins are loaded only once per application run.
    """
    global _plugins_loaded
    if not _plugins_loaded:
        logger.info("Bootstrapping Roadman Mind...")
        load_plugins()
        logger.info(f"Loaded {len(PLUGIN_REGISTRY)} plugins.")
        _plugins_loaded = True

@app.callback()
def main_callback():
    """
    This callback runs before any command, ensuring the application is bootstrapped.
    """
    bootstrap()

@app.command()
def list_routes():
    """
    Lists all available commands (routes) from the loaded plugins.
    """
    console.print("\n[bold cyan]--== ROADMAN MIND ROUTE TABLE ==--[/bold cyan]\n")
    routes = get_all_routes()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Plugin", style="dim", width=12)
    table.add_column("Route", style="cyan")
    table.add_column("Description", style="green")

    # Group routes by plugin for clarity
    plugin_routes = {}
    for name, func in routes.items():
        plugin_name, route_name = name.split(":", 1)
        if plugin_name not in plugin_routes:
            plugin_routes[plugin_name] = []
        plugin_routes[plugin_name].append((name, func.__doc__ or "No description available."))

    for plugin_name in sorted(plugin_routes.keys()):
        for i, (full_route, doc) in enumerate(sorted(plugin_routes[plugin_name])):
            # Only print the plugin name for the first route in its group
            display_plugin = plugin_name if i == 0 else ""
            table.add_row(display_plugin, full_route, doc.strip())
        table.add_row() # Add a separator line between plugins

    console.print(table)
    console.print("Usage: [bold]python -m roadman_mind run <route>[/bold]\n")

@app.command()
def run(
    route_name: str = typer.Argument(..., help="The full name of the route to run, e.g., 'sys:cpu_percent'.")
):
    """
    Runs a specific command (route) from a plugin.
    """
    routes = get_all_routes()

    if route_name not in routes:
        console.print(f"[bold red]Error:[/] Route '[yellow]{route_name}[/yellow]' not found.")
        console.print("Use 'list-routes' to see all available commands.")
        raise typer.Exit(code=1)

    handler = routes[route_name]
    logger.info(f"Executing route: {route_name}")
    console.print(f"\n[bold]Running [cyan]{route_name}[/cyan]...[/bold]")

    try:
        result = handler()
        console.print("[bold green]---> Output:[/bold green]")
        console.print(result)
        console.print("\n[bold]Execution complete.[/bold]")
    except Exception as e:
        logger.error(f"Error executing route '{route_name}': {e}", exc_info=True)
        console.print(f"[bold red]Error during execution:[/] {e}")
        raise typer.Exit(code=1)

def cli():
    """The main entry point for the CLI application."""
    app()
