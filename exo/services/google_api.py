"""
Google API service for exo.

This module provides functions for interacting with Google APIs.
"""

import os
import logging
import requests
from exo.config import get_google_api_key

logger = logging.getLogger(__name__)

# Google API endpoints
GOOGLE_MAPS_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"
GOOGLE_PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
GOOGLE_SEARCH_API_URL = "https://www.googleapis.com/customsearch/v1"

class GoogleAPIError(Exception):
    """Exception raised for Google API errors."""
    pass

def check_api_key():
    """Check if the Google API key is configured."""
    api_key = get_google_api_key()
    if not api_key:
        logger.warning("Google API key is not configured")
        return False
    return True

def geocode(address):
    """
    Geocode an address using Google Maps API.
    
    Args:
        address (str): The address to geocode
        
    Returns:
        dict: The geocoding result
    """
    api_key = get_google_api_key()
    if not api_key:
        raise GoogleAPIError("Google API key is not configured")
    
    params = {
        "address": address,
        "key": api_key
    }
    
    try:
        response = requests.get(GOOGLE_MAPS_API_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data["status"] != "OK":
            raise GoogleAPIError(f"Geocoding error: {data['status']}")
        
        return data["results"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error geocoding address: {e}")
        raise GoogleAPIError(f"Error geocoding address: {e}")

def search_places(query, location=None, radius=None):
    """
    Search for places using Google Places API.
    
    Args:
        query (str): The search query
        location (tuple, optional): The location (latitude, longitude)
        radius (int, optional): The search radius in meters
        
    Returns:
        dict: The search results
    """
    api_key = get_google_api_key()
    if not api_key:
        raise GoogleAPIError("Google API key is not configured")
    
    params = {
        "input": query,
        "inputtype": "textquery",
        "fields": "formatted_address,name,geometry,place_id",
        "key": api_key
    }
    
    if location and radius:
        params["locationbias"] = f"circle:{radius}@{location[0]},{location[1]}"
    
    try:
        response = requests.get(GOOGLE_PLACES_API_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data["status"] != "OK":
            raise GoogleAPIError(f"Places search error: {data['status']}")
        
        return data["candidates"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching places: {e}")
        raise GoogleAPIError(f"Error searching places: {e}")

def search_web(query, num_results=10):
    """
    Search the web using Google Custom Search API.
    
    Args:
        query (str): The search query
        num_results (int, optional): The number of results to return
        
    Returns:
        dict: The search results
    """
    api_key = get_google_api_key()
    if not api_key:
        raise GoogleAPIError("Google API key is not configured")
    
    # Google Custom Search Engine ID (this should be configured separately)
    search_engine_id = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")
    if not search_engine_id:
        raise GoogleAPIError("Google Search Engine ID is not configured")
    
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query,
        "num": min(num_results, 10)  # Maximum 10 results per request
    }
    
    try:
        response = requests.get(GOOGLE_SEARCH_API_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        if "error" in data:
            raise GoogleAPIError(f"Web search error: {data['error']['message']}")
        
        return data.get("items", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching web: {e}")
        raise GoogleAPIError(f"Error searching web: {e}")
