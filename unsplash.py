import requests
import os
from typing import List, Dict, Any, Optional

class UnsplashAPI:
    """
    A class to interact with the Unsplash API for fetching images based on keywords.
    """
    BASE_URL = "https://api.unsplash.com/"
    
    def __init__(self, access_key: str, secret_key: str = None):
        """
        Initialize the UnsplashAPI with your access key and optional secret key.
        
        Args:
            access_key: Your Unsplash API access key (Client ID)
            secret_key: Your Unsplash API secret key (for OAuth authentication)
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.headers = {
            "Authorization": f"Client-ID {access_key}",
            "Accept-Version": "v1"
        }
        self.oauth_token = None
        
    def search_single_photo(self, keyword: str) -> Dict[str, Any]:
        """
        Search for a single photo based on keyword.
        
        Args:
            keyword: The search term
            
        Returns:
            Dict containing image information (URL, author, download link, etc.)
        """
        endpoint = f"{self.BASE_URL}search/photos"
        params = {
            "query": keyword,
            "per_page": 1
        }
        
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        
        results = response.json().get("results", [])
        if not results:
            return {}
        
        photo = results[0]
        return {
            "id": photo.get("id"),
            "description": photo.get("description"),
            "alt_description": photo.get("alt_description"),
            "url": photo.get("urls", {}).get("regular"),
            "small_url": photo.get("urls", {}).get("small"),
            "thumb_url": photo.get("urls", {}).get("thumb"),
            "download_url": photo.get("links", {}).get("download"),
            "user": photo.get("user", {}).get("name"),
            "user_profile": photo.get("user", {}).get("links", {}).get("html")
        }
        
        
    def search_random_photo(self, keyword: str, per_page: int = 30) -> Dict[str, Any]:
        """
        Search for photos based on keyword and return a random one from the results.
        
        Args:
            keyword: The search term
            per_page: Number of photos to search from before selecting random one (default: 30)
                
        Returns:
            Dict containing random image information from the search results
        """
        import random
        
        endpoint = f"{self.BASE_URL}search/photos"
        params = {
            "query": keyword,
            "per_page": min(per_page, 30)  # Limit to 30 as that's a reasonable number
        }
        
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        
        results = response.json().get("results", [])
        if not results:
            return {}
        
        # Choose a random photo from results
        photo = random.choice(results)
        
        return {
            "id": photo.get("id"),
            "description": photo.get("description"),
            "alt_description": photo.get("alt_description"),
            "url": photo.get("urls", {}).get("regular"),
            "small_url": photo.get("urls", {}).get("small"),
            "thumb_url": photo.get("urls", {}).get("thumb"),
            "download_url": photo.get("links", {}).get("download"),
            "user": photo.get("user", {}).get("name"),
            "user_profile": photo.get("user", {}).get("links", {}).get("html")
        }
    
    
    
    def search_photos(self, keyword: str, per_page: int = 10, page: int = 1) -> List[Dict[str, Any]]:
        """
        Search for multiple photos based on keyword.
        
        Args:
            keyword: The search term
            per_page: Number of photos per page (default: 10)
            page: Page number (default: 1)
            
        Returns:
            List of dictionaries containing image information
        """
        endpoint = f"{self.BASE_URL}search/photos"
        params = {
            "query": keyword,
            "per_page": per_page,
            "page": page
        }
        
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        
        results = response.json().get("results", [])
        photos_info = []
        
        for photo in results:
            photos_info.append({
                "id": photo.get("id"),
                "description": photo.get("description"),
                "alt_description": photo.get("alt_description"),
                "url": photo.get("urls", {}).get("regular"),
                "small_url": photo.get("urls", {}).get("small"),
                "thumb_url": photo.get("urls", {}).get("thumb"),
                "download_url": photo.get("links", {}).get("download"),
                "user": photo.get("user", {}).get("name"),
                "user_profile": photo.get("user", {}).get("links", {}).get("html")
            })
        
        return photos_info
    
    def get_random_photo(self, keyword: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a random photo, optionally filtered by keyword.
        
        Args:
            keyword: Optional search term to filter random photos
            
        Returns:
            Dict containing image information
        """
        endpoint = f"{self.BASE_URL}photos/random"
        params = {}
        
        if keyword:
            params["query"] = keyword
            
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        
        photo = response.json()
        return {
            "id": photo.get("id"),
            "description": photo.get("description"),
            "alt_description": photo.get("alt_description"),
            "url": photo.get("urls", {}).get("regular"),
            "small_url": photo.get("urls", {}).get("small"),
            "thumb_url": photo.get("urls", {}).get("thumb"),
            "download_url": photo.get("links", {}).get("download"),
            "user": photo.get("user", {}).get("name"),
            "user_profile": photo.get("user", {}).get("links", {}).get("html")
        }
    
    def get_random_photos(self, count: int = 3, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get multiple random photos, optionally filtered by keyword.
        
        Args:
            count: Number of random photos to return (max 30)
            keyword: Optional search term to filter random photos
            
        Returns:
            List of dictionaries containing image information
        """
        endpoint = f"{self.BASE_URL}photos/random"
        params = {"count": min(count, 30)}  # Unsplash API limits to 30
        
        if keyword:
            params["query"] = keyword
            
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        
        photos = response.json()
        photos_info = []
        
        for photo in photos:
            photos_info.append({
                "id": photo.get("id"),
                "description": photo.get("description"),
                "alt_description": photo.get("alt_description"),
                "url": photo.get("urls", {}).get("regular"),
                "small_url": photo.get("urls", {}).get("small"),
                "thumb_url": photo.get("urls", {}).get("thumb"),
                "download_url": photo.get("links", {}).get("download"),
                "user": photo.get("user", {}).get("name"),
                "user_profile": photo.get("user", {}).get("links", {}).get("html")
            })
        
        return photos_info
    
    def download_photo(self, photo_id: str, save_path: str) -> str:
        """
        Download a photo by its ID and save it to disk.
        
        Args:
            photo_id: The Unsplash photo ID
            save_path: Directory where to save the image
            
        Returns:
            Path to the saved image file
        """
        endpoint = f"{self.BASE_URL}photos/{photo_id}/download"
        
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        
        download_url = response.json().get("url")
        if not download_url:
            raise ValueError("Download URL not found")
        
        img_response = requests.get(download_url)
        img_response.raise_for_status()
        
        # Make sure directory exists
        os.makedirs(save_path, exist_ok=True)
        
        # Get filename from URL or use photo ID
        filename = photo_id + ".jpg"
        file_path = os.path.join(save_path, filename)
        
        with open(file_path, "wb") as f:
            f.write(img_response.content)
            
        return file_path

