
import google_ai_studio
import crawler
import store
import unsplash

from urllib.parse import urlparse
import json
import os
import random
import cms_client

import argparse



def parse_arguments():
    parser = argparse.ArgumentParser(description='Web crawler application')
    
    parser.add_argument('--unsplash-access-key', type=str, help='Unsplash API access key')
    parser.add_argument('--google-ai-api-key', type=str, help='Google AI Studio API key')
    
    parser.add_argument('--cms-admin-api-key', type=str, help='Ghost CMS admin API key')
    parser.add_argument('--cms-url', type=str, default='', help='Ghost CMS URL')
    
    return parser.parse_args()




if __name__ == "__main__":
    
    
    args = parse_arguments()

    key_unsplash_access = args.unsplash_access_key if args.unsplash_access_key else ""
    key_google_ai = args.google_ai_api_key if args.google_ai_api_key else ""
    key_cms_admin_api = args.cms_admin_api_key if args.cms_admin_api_key else ""
    key_cms_url = args.cms_url if args.cms_url else ""
    
    # Check if any required keys are missing
    if not key_unsplash_access or not key_google_ai or not key_cms_admin_api or not key_cms_url:
        print("Error: Missing required API keys (Need to fill out the arguments)")
        print(f"Unsplash access key: {'Set' if key_unsplash_access else 'Missing'}")
        print(f"Google AI API key: {'Set' if key_google_ai else 'Missing'}")
        print(f"CMS admin API key: {'Set' if key_cms_admin_api else 'Missing'}")
        print(f"CMS URL: {'Set' if key_cms_url else 'Missing'}")
        exit()
    
    
    
    
    image = unsplash.UnsplashAPI(access_key=key_unsplash_access)
    s3 = store.URLDatabase()
    craw = crawler.WebCrawler()
    ai = google_ai_studio.GeminiClient(api_key=key_google_ai)
    
    
    
    
    # Read the target URLs from the JSON file
    try:
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'targeturl_base.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            target_urls = json.load(f)
        print(f"Successfully loaded {len(target_urls)} target URLs")
    except Exception as e:
        print(f"Error loading target URLs: {e}")
        target_urls = []
        

    ghost_client = cms_client.GhostCmsClient(
        url=key_cms_url,
        admin_api_key=key_cms_admin_api
    )
    
        
        
    # Randomly select 2 URLs from the target list if there are more than 2
    if len(target_urls) > 2:
        target_urls = random.sample(target_urls, 2)
        print(f"Randomly selected {len(target_urls)} URLs for processing")
    else:
        print(f"Using all {len(target_urls)} available URLs as the list is small")
        
        
    for buff in target_urls:

        DATA_URI = buff['url']
        DATA_LIST_PATTERN = buff['list_pattern']
        DATA_PATTERN = buff['pattern']
        html_mother = craw.extract_links(url=DATA_URI, css_selectors=DATA_LIST_PATTERN)
        
        if not html_mother:
            print(f"No links found for {DATA_URI}")
            continue
        
        random_link = random.choice(html_mother)
        parsed_url = urlparse(random_link)
        
        if not parsed_url.scheme:
            base_url = urlparse(DATA_URI)
            domain = f"{base_url.scheme}://{base_url.netloc}"
        else:
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
        path = parsed_url.path
        
        if parsed_url.query:
            path = path + '?' + parsed_url.query
            
        if path and not path.startswith('/'):
            path = '/' + path
        
        check_uri = s3.read_by_domain_and_path(domain=domain, uripath=path)
        

        
        if check_uri:
            print(f"Already crawled ({domain}{path})")
            continue
        else:
            print(f"Not crawled yet ({domain}{path})")
            s3.create(domain=domain, uripath=path)
        
        
        html = craw.get_page_content(url=f'{domain}{path}')
        
        
        post_title = ai.extract_content_from_html(
                custom_prompt="""
Translate to Korean.
Create a short, clickbait title based on the article.
Title should be 20-30 characters.
Add the country being discussed in [Country] format at the start of the title.
Avoid controversial titles.
Return only the title text.
Do not include sources.
Keep company names and special terms in their original form.
                """,
                html_content=html, 
                selector_map=DATA_PATTERN,
            )
        


        
        
        post_content = ai.extract_content_from_html(
                custom_prompt="""
Summarize the given text and write it in HTML format.
Use <h1~6> for sections.
Use <ul>, <li> for lists and key points.
Use <table>, <tr>, <td> for data comparison.
Minimize <p>, prioritize <ul> and <table>.
Use <b>, <strong> for important points.
Use <i>, <em> for reference points.
Use <blockquote> for quotes.
Do not use images or videos, describe with text.
Avoid controversial sentences.
Summarize only key information.
Follow this order:
Event description
Background
Key points
Expected impact
Only use HTML format.
Focus on development and IT.
Do not include sources.
Keep company and product names as is.
Write in Korean.
                """,
                html_content=html, 
                selector_map=DATA_PATTERN
            )
        
        post_keyword = ai.extract_content_from_html(
                custom_prompt="""
Read the text.
Choose relevant keywords from the options below.
The keywords will be used to search images in the Unsplash API.
Make sure the keywords are short, clear, and specific.
Avoid using general or cliché terms.
Use only English.
Return keywords in a simple comma-separated list (e.g., Electric scooter, Micromobility, Sharing service).
                """,
                html_content=html, 
                selector_map=DATA_PATTERN
            )


        post_image = image.search_random_photo(keyword=post_keyword, per_page=16)

        
        ghost_client.create_post(
            head_image_data=post_image,
            title=f"{post_title}",
            content=f"""{post_content}""",
            status="published",
            keyword=post_keyword,
            tags=[
                {"name": "News"},
                {"name": "posts"},
                {"name": "AI-generated"},
                {"name": "crawled"},
            ],
        )
        
        
    
    
