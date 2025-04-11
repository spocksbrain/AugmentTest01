#!/usr/bin/env python3
"""
Test script for the onboarding process
"""

import os
import sys
import logging
from exo.core.onboarding import Onboarding

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Test the onboarding process."""
    logger.info("Testing onboarding process")
    
    # Create an onboarding instance
    onboarding = Onboarding()
    
    # Print the current configuration
    config_path = os.path.join(os.path.expanduser("~"), ".exo", "config.json")
    logger.info(f"Configuration file path: {config_path}")
    logger.info(f"Configuration file exists: {os.path.exists(config_path)}")
    
    # Print the current environment variables
    logger.info("Current environment variables:")
    for var in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY"]:
        logger.info(f"  {var}: {'Set' if var in os.environ else 'Not set'}")
    
    # Print the current configuration
    logger.info("Current configuration:")
    for var in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY"]:
        logger.info(f"  {var}: {'Set' if var in onboarding.config else 'Not set'}")
    
    # Run the onboarding process
    logger.info("Running onboarding process")
    success = onboarding.run_onboarding(interactive=True)
    
    # Print the result
    logger.info(f"Onboarding process {'succeeded' if success else 'failed'}")
    
    # Print the updated configuration
    logger.info("Updated configuration:")
    for var in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY"]:
        logger.info(f"  {var}: {'Set' if var in onboarding.config else 'Not set'}")

if __name__ == "__main__":
    main()
