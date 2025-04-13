"""
Tests for the service registry module
"""

import pytest
from exo.core.service_registry import ServiceRegistry, ServiceNames, register_service, get_service, has_service

class TestServiceRegistry:
    """Tests for the ServiceRegistry class."""
    
    def test_singleton_pattern(self):
        """Test that ServiceRegistry implements the singleton pattern."""
        registry1 = ServiceRegistry()
        registry2 = ServiceRegistry()
        assert registry1 is registry2
    
    def test_register_and_get_service(self):
        """Test registering and retrieving a service."""
        # Clear the registry singleton for testing
        ServiceRegistry._instance = None
        registry = ServiceRegistry()
        
        # Register a service
        service = "test_service_instance"
        registry.register("test_service", service)
        
        # Get the service
        retrieved_service = registry.get("test_service")
        assert retrieved_service == service
    
    def test_has_service(self):
        """Test checking if a service exists."""
        # Clear the registry singleton for testing
        ServiceRegistry._instance = None
        registry = ServiceRegistry()
        
        # Register a service
        registry.register("test_service", "test_service_instance")
        
        # Check if the service exists
        assert registry.has("test_service") is True
        assert registry.has("nonexistent_service") is False
    
    def test_unregister_service(self):
        """Test unregistering a service."""
        # Clear the registry singleton for testing
        ServiceRegistry._instance = None
        registry = ServiceRegistry()
        
        # Register a service
        registry.register("test_service", "test_service_instance")
        
        # Unregister the service
        registry.unregister("test_service")
        
        # Check that the service is gone
        assert registry.has("test_service") is False
    
    def test_clear_registry(self):
        """Test clearing the registry."""
        # Clear the registry singleton for testing
        ServiceRegistry._instance = None
        registry = ServiceRegistry()
        
        # Register some services
        registry.register("service1", "instance1")
        registry.register("service2", "instance2")
        
        # Clear the registry
        registry.clear()
        
        # Check that all services are gone
        assert registry.has("service1") is False
        assert registry.has("service2") is False
    
    def test_get_all_services(self):
        """Test getting all services."""
        # Clear the registry singleton for testing
        ServiceRegistry._instance = None
        registry = ServiceRegistry()
        
        # Register some services
        registry.register("service1", "instance1")
        registry.register("service2", "instance2")
        
        # Get all services
        services = registry.get_all()
        
        # Check that all services are returned
        assert len(services) == 2
        assert services["service1"] == "instance1"
        assert services["service2"] == "instance2"

def test_helper_functions():
    """Test the helper functions for the service registry."""
    # Clear the registry singleton for testing
    ServiceRegistry._instance = None
    
    # Register a service using the helper function
    register_service("helper_test", "helper_instance")
    
    # Check if the service exists using the helper function
    assert has_service("helper_test") is True
    
    # Get the service using the helper function
    service = get_service("helper_test")
    assert service == "helper_instance"
