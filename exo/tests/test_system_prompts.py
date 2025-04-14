"""
Tests for the system prompts
"""

import pytest
from exo.core.system_prompts import get_system_prompt

class TestSystemPrompts:
    """Tests for the system prompts."""
    
    def test_get_system_prompt_pia(self):
        """Test getting the system prompt for the PIA."""
        prompt = get_system_prompt("pia")
        
        # Check that the prompt contains the expected content
        assert "Primary Interface Agent (PIA)" in prompt
        assert "Core Responsibilities" in prompt
        assert "Available Tools and Capabilities" in prompt
        assert "MCP Servers" in prompt
        assert "Brave Search MCP Server" in prompt
        assert "Filesystem MCP Server" in prompt
        assert "How to Handle User Requests" in prompt
        assert "Behavioral Guidelines" in prompt
        
    def test_get_system_prompt_cnc(self):
        """Test getting the system prompt for the CNC agent."""
        prompt = get_system_prompt("cnc")
        
        # Check that the prompt contains the expected content
        assert "Command & Control Agent (CNC)" in prompt
        assert "Core Responsibilities" in prompt
        assert "Available Domain Agents" in prompt
        assert "Task Orchestration" in prompt
        assert "Behavioral Guidelines" in prompt
        
    def test_get_system_prompt_software_engineer(self):
        """Test getting the system prompt for the Software Engineer agent."""
        prompt = get_system_prompt("software_engineer")
        
        # Check that the prompt contains the expected content
        assert "Software Engineer Agent" in prompt
        assert "Core Capabilities" in prompt
        assert "Behavioral Guidelines" in prompt
        
    def test_get_system_prompt_mcp_server(self):
        """Test getting the system prompt for the MCP Server agent."""
        prompt = get_system_prompt("mcp_server")
        
        # Check that the prompt contains the expected content
        assert "MCP Server Agent" in prompt
        assert "Core Capabilities" in prompt
        assert "Available MCP Servers" in prompt
        assert "Brave Search MCP Server" in prompt
        assert "Filesystem MCP Server" in prompt
        assert "Behavioral Guidelines" in prompt
        
    def test_get_system_prompt_unknown(self):
        """Test getting the system prompt for an unknown agent type."""
        prompt = get_system_prompt("unknown")
        
        # Check that a default prompt is returned
        assert "helpful assistant" in prompt.lower()
        
    def test_system_prompt_consistency(self):
        """Test that the system prompts are consistent with each other."""
        pia_prompt = get_system_prompt("pia")
        cnc_prompt = get_system_prompt("cnc")
        software_engineer_prompt = get_system_prompt("software_engineer")
        mcp_server_prompt = get_system_prompt("mcp_server")
        
        # Check that the PIA prompt mentions the other agents
        assert "Command & Control Agent" in pia_prompt
        assert "Software Engineer Agent" in pia_prompt
        assert "MCP Server Agent" in pia_prompt
        
        # Check that the CNC prompt mentions the domain agents
        assert "Software Engineer Agent" in cnc_prompt
        assert "MCP Server Agent" in cnc_prompt
