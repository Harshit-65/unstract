import importlib
import logging
from typing import Dict, Any, Set

logger = logging.getLogger(__name__)

class AuthenticationPluginRegistry:
    """Registry for authentication plugins with security controls."""
    
    # Whitelist of allowed authentication plugin modules
    ALLOWED_PLUGINS: Set[str] = {
        'account_v2.plugins.oauth_plugin',
        'account_v2.plugins.ldap_plugin', 
        'account_v2.plugins.saml_plugin',
        'account_v2.plugins.basic_auth_plugin',
        'account_v2.plugins.jwt_plugin'
    }
    
    def __init__(self):
        self._plugins: Dict[str, Any] = {}
    
    def load_plugin(self, plugin_name: str) -> Any:
        """
        Safely load an authentication plugin with whitelist validation.
        
        Args:
            plugin_name: Name of the plugin module to load
            
        Returns:
            Loaded plugin module
            
        Raises:
            ValueError: If plugin_name is not in the allowed whitelist
            ImportError: If the whitelisted plugin cannot be imported
        """
        # Validate input
        if not isinstance(plugin_name, str):
            raise ValueError("Plugin name must be a string")
        
        # Strip whitespace and validate against whitelist
        plugin_name = plugin_name.strip()
        if not plugin_name:
            raise ValueError("Plugin name cannot be empty")
            
        if plugin_name not in self.ALLOWED_PLUGINS:
            logger.warning(f"Attempted to load unauthorized plugin: {plugin_name}")
            raise ValueError(f"Plugin '{plugin_name}' is not in the allowed plugins list")
        
        # Check if already loaded
        if plugin_name in self._plugins:
            return self._plugins[plugin_name]
        
        try:
            # Safe to import since plugin_name is validated against whitelist
            logger.info(f"Loading authorized authentication plugin: {plugin_name}")
            module = importlib.import_module(plugin_name)
            self._plugins[plugin_name] = module
            return module
        except ImportError as e:
            logger.error(f"Failed to import whitelisted plugin '{plugin_name}': {e}")
            raise ImportError(f"Could not load authentication plugin '{plugin_name}': {e}")
    
    def get_available_plugins(self) -> Set[str]:
        """Return the set of available (whitelisted) plugins."""
        return self.ALLOWED_PLUGINS.copy()
    
    def is_plugin_allowed(self, plugin_name: str) -> bool:
        """Check if a plugin name is in the whitelist."""
        return plugin_name in self.ALLOWED_PLUGINS

# Global registry instance
registry = AuthenticationPluginRegistry()

def load_authentication_plugin(plugin_name: str) -> Any:
    """
    Load an authentication plugin safely.
    
    Args:
        plugin_name: Name of the plugin to load
        
    Returns:
        Loaded plugin module
    """
    return registry.load_plugin(plugin_name)
