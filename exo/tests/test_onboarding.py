"""
Tests for the onboarding module
"""

import os
import json
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from exo.core.onboarding import Onboarding

class TestOnboarding:
    """Tests for the Onboarding class."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary directory for config files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_init(self, temp_config_dir):
        """Test initialization of the Onboarding class."""
        onboarding = Onboarding(config_dir=temp_config_dir)
        
        # Check that the config directory was created
        assert os.path.exists(temp_config_dir)
        
        # Check that the config files were created
        assert os.path.exists(os.path.join(temp_config_dir, "config.json"))
        assert os.path.exists(os.path.join(temp_config_dir, "mcp_servers.json"))
    
    def test_get_env_var(self, temp_config_dir):
        """Test getting environment variables."""
        # Create a config file with test values
        config = {
            "TEST_VAR": "test_value",
            "EMPTY_VAR": "",
            "NONE_VAR": None
        }
        
        os.makedirs(temp_config_dir, exist_ok=True)
        with open(os.path.join(temp_config_dir, "config.json"), "w") as f:
            json.dump(config, f)
        
        onboarding = Onboarding(config_dir=temp_config_dir)
        
        # Test getting an existing variable
        assert onboarding.get_env_var("TEST_VAR") == "test_value"
        
        # Test getting a non-existent variable
        assert onboarding.get_env_var("NONEXISTENT_VAR") is None
        
        # Test getting a non-existent variable with a default value
        assert onboarding.get_env_var("NONEXISTENT_VAR", "default") == "default"
        
        # Test getting an empty variable
        assert onboarding.get_env_var("EMPTY_VAR") == ""
        
        # Test getting a None variable
        assert onboarding.get_env_var("NONE_VAR") is None
    
    def test_set_env_var(self, temp_config_dir):
        """Test setting environment variables."""
        onboarding = Onboarding(config_dir=temp_config_dir)
        
        # Set a new variable
        onboarding.set_env_var("NEW_VAR", "new_value")
        
        # Check that the variable was set in the config
        assert onboarding.get_env_var("NEW_VAR") == "new_value"
        
        # Check that the config file was updated
        with open(os.path.join(temp_config_dir, "config.json"), "r") as f:
            config = json.load(f)
            assert config["NEW_VAR"] == "new_value"
    
    def test_export_env_vars(self, temp_config_dir):
        """Test exporting environment variables."""
        # Create a config file with test values
        config = {
            "TEST_VAR": "test_value",
            "EMPTY_VAR": "",
            "NONE_VAR": None
        }
        
        os.makedirs(temp_config_dir, exist_ok=True)
        with open(os.path.join(temp_config_dir, "config.json"), "w") as f:
            json.dump(config, f)
        
        onboarding = Onboarding(config_dir=temp_config_dir)
        
        # Export the environment variables
        with patch.dict(os.environ, {}, clear=True):
            onboarding.export_env_vars()
            
            # Check that the variables were exported
            assert os.environ.get("TEST_VAR") == "test_value"
            assert os.environ.get("EMPTY_VAR") == ""
            assert os.environ.get("NONE_VAR") == ""  # None should be converted to empty string
    
    def test_check_env_vars(self, temp_config_dir):
        """Test checking environment variables."""
        onboarding = Onboarding(config_dir=temp_config_dir)
        
        # Mock the required environment variables
        required_vars = [
            {"name": "TEST_VAR", "description": "Test variable", "secret": False, "required": True},
            {"name": "OPTIONAL_VAR", "description": "Optional variable", "secret": False, "required": False}
        ]
        
        # Set the test variable
        onboarding.set_env_var("TEST_VAR", "test_value")
        
        # Check the variables
        missing_vars = onboarding.check_env_vars(required_vars)
        
        # The required variable is set, so there should be no missing variables
        assert len(missing_vars) == 0
        
        # Now check with force=True
        missing_vars = onboarding.check_env_vars(required_vars, force=True)
        
        # With force=True, all variables should be considered missing
        assert len(missing_vars) == 2
        assert missing_vars[0]["name"] == "TEST_VAR"
        assert missing_vars[1]["name"] == "OPTIONAL_VAR"
