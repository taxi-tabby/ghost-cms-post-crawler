import requests
from datetime import datetime, timezone
import time
import jwt





class GhostCmsClient:
    def __init__(self, url, admin_api_key):
        self.url = url.rstrip("/")
        self.admin_api_key = admin_api_key
        self.session = requests.Session()
        self.token = None
        self.token_expiry = 0
    
    def get_token(self):
        """Get a valid JWT token, creating a new one if necessary"""
        current_time = time.time()
        
        # If token exists and is not expired (with 30-second buffer), return it
        if self.token and self.token_expiry > current_time + 30:
            return self.token
            
        # Otherwise create a new token
        return self._create_new_token()
    
    def _create_new_token(self):
        """Create JWT token for Ghost Admin API authentication"""
        try:
            # Split the key into ID and SECRET
            id, secret = self.admin_api_key.split(':')
            
            iat = int(time.time())
            # Token expires in 5 minutes
            exp = iat + 5 * 60
            
            header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id}
            payload = {
                'iat': iat,
                'exp': exp,
                'aud': '/admin/'
            }
            
            # Create the token with bytes.fromhex(secret)
            token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)
            
            # Store the token and its expiry time
            self.token = token
            self.token_expiry = exp
            print("New authentication token created")
            return token
        except Exception as e:
            print(f"Token creation failed: {e}")
            return None
        
        
    def create_post(self, title, content, status="draft", tags=None, featured=False, head_image_data=None, keyword=None):
        """Create a new post using the JWT token authentication"""
        # Get a valid token
        token = self.get_token()
        if not token:
            print("Failed to get authentication token")
            return False
        
        create_url = f"{self.url}/ghost/api/admin/posts/?source=html"
        
            
        post_title = title
        
        # Check post_title length and truncate if over 90 bytes
        if isinstance(post_title, str):
            encoded_title = post_title.encode('utf-8')
            if len(encoded_title) > 90:
                # Truncate safely by decoding incrementally
                safe_length = 87  # Leave room for "..."
                while safe_length > 0:
                    try:
                        truncated_title = encoded_title[:safe_length].decode('utf-8')
                        post_title = truncated_title + "..."
                        break
                    except UnicodeDecodeError:
                        # If decoding fails, reduce length and try again
                        safe_length -= 1
                        
        
        post_keyword = ""
        if keyword:
            post_keyword = keyword
        
        
        featured_image = ""
        featured_image_alt = ""
        featured_image_caption = ""
        
        if head_image_data:
            featured_image = head_image_data.get("url", "")
            
            # Use description or alt_description for alt text
            if head_image_data.get("description"):
                featured_image_alt = head_image_data.get("description")
            elif head_image_data.get("alt_description"):
                featured_image_alt = head_image_data.get("alt_description")
            
            # Check featured_image_alt length and truncate if over 150 bytes
            if isinstance(featured_image_alt, str):
                encoded_alt = featured_image_alt.encode('utf-8')
                if len(encoded_alt) > 150:
                    # Truncate safely by decoding incrementally
                    safe_length = 147  # Leave room for "..."
                    while safe_length > 0:
                        try:
                            truncated_alt = encoded_alt[:safe_length].decode('utf-8')
                            featured_image_alt = truncated_alt + "..."
                            break
                        except UnicodeDecodeError:
                            # If decoding fails, reduce length and try again
                            safe_length -= 1
            
            
            # Create caption with photo credit
            user = head_image_data.get("user", "")
            user_profile = head_image_data.get("user_profile", "")
            if user and user_profile:
                featured_image_caption = f"Unsplash 에 올려진 <a href='{user_profile}'>{user}</a> 님께서 찍은 사진.\n({post_keyword})"
            elif user:
                featured_image_caption = f"Unsplash 에 올려진 {user} 님께서 찍은 사진.\n({post_keyword})"
        
        
        # Check featured_image length and clear it if over 2000 bytes
        if featured_image and isinstance(featured_image, str):
            if len(featured_image.encode('utf-8')) > 2000:
                featured_image = ""
                featured_image_alt = ""
                featured_image_caption = ""
                print("Featured image URL was too long (>2000 bytes), removing it")
        
        
        # Ensure content is properly formatted as a string
        if content is None:
            content = ""
        
        
        
        # Remove ```html at the beginning if present
        if isinstance(content, str):
            if content.strip().startswith("```html"):
                content = content.strip().replace("```html", "", 1).lstrip()
            
            # Remove trailing ``` if present
            if content.strip().endswith("```"):
                content = content.strip()[:-3].rstrip()
        
        
        
        post_data = {
            "posts": [{
                "feature_image": featured_image,
                "feature_image_alt": featured_image_alt,
                "feature_image_caption": featured_image_caption,
                "title": post_title,
                "html": str(content),
                "status": status,
                "featured": featured,
                "published_at": datetime.now(timezone.utc).isoformat() if status == "published" else None,
                "tags": tags if tags else []
            }]
        }
        
        headers = {
            "Authorization": f"Ghost {token}",
            "Content-Type": "application/json"
        }
        
        # Debug print
        # print(f"Creating post with content: {content[:100]}...")  # Print first 100 chars for debugging
        
        response = self.session.post(create_url, json=post_data, headers=headers)
        
        if response.status_code == 401:
            # Token might be invalid despite our checks - force a new one
            print("Token rejected - creating a new one")
            self.token = None
            token = self.get_token()
            if token:
                headers["Authorization"] = f"Ghost {token}"
                response = self.session.post(create_url, json=post_data, headers=headers)
        
        if response.status_code == 201 or response.status_code == 200:
            print(f"Post '{title}' created successfully")
            return response.json()
        else:
            print(f"Failed to create post: {response.status_code}")
            print(response.text)
            return False
    
    def is_authenticated(self):
        """Check if we can authenticate with the API"""
        token = self.get_token()
        if not token:
            return False
            
        me_url = f"{self.url}/ghost/api/admin/users/me/"
        
        headers = {
            "Authorization": f"Ghost {token}",
            "Content-Type": "application/json"
        }
        
        response = self.session.get(me_url, headers=headers)
        return response.status_code == 200