from abc import ABC, abstractmethod
import importlib
import pkgutil
from typing import Dict, Callable, List

# This will hold all discovered plugin instances
PLUGIN_REGISTRY = []

class Plugin(ABC):
    """
    Abstract base class for a plugin.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """A short, lowercase name for the plugin, e.g., 'sys'."""
        raise NotImplementedError

    @property
    @abstractmethod
    def version(self) -> str:
        """The version of the plugin."""
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        """A brief description of what the plugin does."""
        raise NotImplementedError

    @abstractmethod
    def routes(self) -> Dict[str, Callable]:
        """Returns a dictionary mapping route names to callable functions."""
        raise NotImplementedError

    def __init_subclass__(cls, **kwargs):
        """
        Automatically registers any class that inherits from this one.
        """
        super().__init_subclass__(**kwargs)
        # Instantiate and register the plugin
        plugin_instance = cls()
        PLUGIN_REGISTRY.append(plugin_instance)

def get_all_routes() -> Dict[str, Callable]:
    """
    Gathers all routes from all registered plugins into a single dictionary.
    The key is the full route name, like 'plugin_name:route_name'.
    """
    all_routes = {}
    for plugin in PLUGIN_REGISTRY:
        for route_name, handler in plugin.routes().items():
            full_route_name = f"{plugin.name}:{route_name}"
            all_routes[full_route_name] = handler
    return all_routes

def load_plugins():
    """
    Dynamically discovers and loads all plugins from the `roadman_mind.plugins` package.
    It looks for sub-packages and imports their `module.py` file.
    """
    import roadman_mind.plugins

    def iter_namespace(ns_pkg):
        return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

    for finder, name, ispkg in iter_namespace(roadman_mind.plugins):
        if ispkg:
            # This is a plugin directory, look for module.py inside it
            try:
                importlib.import_module(f"{name}.module")
            except ImportError as e:
                # This is not a fatal error, just means the plugin might be empty
                # or doesn't have a module.py, which is fine.
                # print(f"Could not load module for plugin {name}: {e}")
                pass
