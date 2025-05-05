import requests
import json
from bs4 import BeautifulSoup

class GeminiClient:
    """A client for interacting with Google's Gemini API."""
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    
    def __init__(self, api_key):
        """
        Initialize the Gemini client.
        
        Args:
            api_key (str): Your Gemini API key
        """
        self.api_key = api_key
        
    def generate_content(self, model="gemini-2.0-flash", prompt="", temperature=None, max_tokens=None):
        """
        Generate content using the Gemini API.
        
        Args:
            model (str): Model name to use (default: gemini-2.0-flash)
            prompt (str): Text prompt for the model
            temperature (float, optional): Controls randomness (0.0-1.0)
            max_tokens (int, optional): Maximum number of tokens to generate
            
        Returns:
            dict: The API response as a dictionary
        """
        url = f"{self.BASE_URL}/models/{model}:generateContent?key={self.api_key}"
        
        # Prepare request payload
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        # Add optional parameters if provided
        generation_config = {}
        if temperature is not None:
            generation_config["temperature"] = temperature
        if max_tokens is not None:
            generation_config["maxOutputTokens"] = max_tokens
            
        if generation_config:
            payload["generationConfig"] = generation_config
            
        # Make the API call
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        return response.json()
    
    def get_text_response(self, prompt, model="gemini-2.0-flash"):
        """
        Get just the text response from the Gemini API.
        
        Args:
            prompt (str): Text prompt for the model
            model (str): Model name to use
            
        Returns:
            str: The generated text response or error message
        """
        response = self.generate_content(model=model, prompt=prompt)
        
        try:
            return response["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return f"Error: {response.get('error', {}).get('message', 'Unknown error')}"


    def extract_content_from_html(self, html_content, selector_map, custom_prompt=None):
        """
        Extract content from HTML using CSS selectors and format as key-value pairs.
        
        Args:
            html_content (str): HTML content to parse
            selector_map (dict): Dictionary mapping keys to CSS selectors
                Example: {"title": "h1.main-title", "price": "span.price"}
            custom_prompt (str, optional): Custom prompt to guide extraction process
                
        Returns:
            str: Formatted string with extracted content as "-key : value" pairs
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        result = {}
        formatted_result = ""
        
        for key, selector in selector_map.items():
            elements = soup.select(selector)
            if elements:
                # If multiple elements found, collect them in a list
                if len(elements) > 1:
                    result[key] = [elem.get_text(strip=True) for elem in elements]
                else:
                    result[key] = elements[0].get_text(strip=True)
            else:
                result[key] = None
                
            # Format as "-key : value"
            value_str = str(result[key]) if result[key] is not None else ""
            formatted_result += f"-{key} : {value_str}\n"
        
        # Apply custom prompt to format or enhance the extraction if provided
        if custom_prompt and formatted_result:
            prompt = f"{custom_prompt}\n\nExtracted content:\n{formatted_result}"
            formatted_result = self.get_text_response(prompt)
            
        return formatted_result.strip()



