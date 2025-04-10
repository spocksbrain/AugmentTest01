"""
Service Registry for the exo Multi-Agent Framework

This module provides a centralized registry for system-wide services,
ensuring that all components have access to the same service instances.
"""

import logging
from typing import Dict, Any, Optional, Type

logger = logging.getLogger(__name__)

class ServiceRegistry:
    """
    Service Registry for the exo Multi-Agent Framework
    
    This class provides a centralized registry for system-wide services,
    ensuring that all components have access to the same service instances.
    """
    
    _instance = None
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(ServiceRegistry, cls).__new__(cls)
            cls._instance._services = {}
        return cls._instance
    
    def register(self, service_name: str, service_instance: Any) -> None:
        """
        Register a service with the registry.
        
        Args:
            service_name: Name of the service
            service_instance: Instance of the service
        """
        self._services[service_name] = service_instance
        logger.debug(f"Registered service: {service_name}")
    
    def get(self, service_name: str) -> Optional[Any]:
        """
        Get a service from the registry.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service instance, or None if not found
        """
        service = self._services.get(service_name)
        if service is None:
            logger.warning(f"Service not found: {service_name}")
        return service
    
    def has(self, service_name: str) -> bool:
        """
        Check if a service is registered.
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if the service is registered, False otherwise
        """
        return service_name in self._services
    
    def unregister(self, service_name: str) -> None:
        """
        Unregister a service from the registry.
        
        Args:
            service_name: Name of the service
        """
        if service_name in self._services:
            del self._services[service_name]
            logger.debug(f"Unregistered service: {service_name}")
    
    def clear(self) -> None:
        """Clear all services from the registry."""
        self._services.clear()
        logger.debug("Cleared service registry")
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all registered services.
        
        Returns:
            Dictionary of service names to service instances
        """
        return self._services.copy()


# Common service names
class ServiceNames:
    """Common service names used in the system."""
    MCP_MANAGER = "mcp_manager"
    LLM_MANAGER = "llm_manager"
    ONBOARDING = "onboarding"
    SYSTEM = "system"


# Helper functions for common operations
def get_service(service_name: str) -> Optional[Any]:
    """
    Get a service from the registry.
    
    Args:
        service_name: Name of the service
        
    Returns:
        Service instance, or None if not found
    """
    return ServiceRegistry().get(service_name)

def register_service(service_name: str, service_instance: Any) -> None:
    """
    Register a service with the registry.
    
    Args:
        service_name: Name of the service
        service_instance: Instance of the service
    """
    ServiceRegistry().register(service_name, service_instance)

def has_service(service_name: str) -> bool:
    """
    Check if a service is registered.
    
    Args:
        service_name: Name of the service
        
    Returns:
        True if the service is registered, False otherwise
    """
    return ServiceRegistry().has(service_name)
