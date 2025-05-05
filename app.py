
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
                    (중요) 내용을 한국어로 번역해 주세요.
                    기사 내용을 바탕으로 짧고 임팩트 있는 제목을 생성하세요.  
                    제목은 클릭베이트 스타일로 간결하게 작성하고, 길이는 20-30자 사이로 설정해주세요.  
                    제목 앞에 해당 내용이 어느 나라 이야기인지 [국가] 형태로 넣어주세요.
                    문제의 여지나 논란이 있을 것 같은 제목을 최대한 피하세요.
                    HTML 태그나 추가 포맷 없이 제목 텍스트만 반환하고, 추가 설명은 포함하지 마세요. 
                    출처를 굳이 남기지 마세요. 기업이나 제품 등의 이름은 중요한 정보입니다.
                    회사 명이나 기능 명칭 또는 특수 명사, 대명사 등은 굳이 번역할 필요 없으면 그대로 작성하세요.
                """,
                html_content=html, 
                selector_map=DATA_PATTERN
            )
        


        
        
        post_content = ai.extract_content_from_html(
                custom_prompt="""
                    모든 내용을 한글로 요약하고 HTML 태그를 사용하여 포맷해주세요.  
                    - <h1~6>는 주요 섹션에 골라서 사용하세요.  
                    - <ul>/<li>는 핵심 사항이나 목록을 작성하는 데 사용하세요.  
                    - <table>, <tr>, <td>는 데이터를 비교하거나 조직하는 데 사용하세요.  
                    - <p>는 최소화하고 <ul>과 <table>을 우선적으로 사용하여 가독성을 높이세요.  
                    - 중요한 사실은 <b> 또는 <strong>로 강조하세요.  
                    - 참고할 내용은 <i> 또는 <em>로 강조하세요.
                    - 인용구는 <blockquote>로 감싸세요.
                    - 이미지나 비디오 링크는 최대한 사용하면 안됩니다, 정말 별 수 없다면 아스키 아트같이 비슷한 것을 생성하여 최대한 텍스트로 설명하도록 하세요.

                    문제의 여지나 논란이 있을 것 같은 문장은 최대한 피하세요.
                    간결하게 요약하고 핵심 정보에 집중하세요.
                    요약 순서는
                    - 발생한 사건 또는 문제에 대한 설명
                    - 사건의 배경 또는 맥락
                    - 핵심 요약 정보
                    - 추후 예상되는 영향 또는 결과  
                    HTML 형식으로만 반환하고, ```html과 같은 코드 블록 구분자나 추가 설명은 포함하지 마세요.
                    
                    내용을 개발 및 IT와 연관되도록 해야 해.
                    출처를 굳이 남기지 마세요. 기업이나 제품 등의 이름은 중요한 정보입니다.
                    회사 명이나 기능 명칭 또는 특수 명사, 대명사 등은 굳이 번역할 필요 없으면 그대로 작성하세요.
                    (중요) 내용을 한국어로 번역해 주세요.
                """,
                html_content=html, 
                selector_map=DATA_PATTERN
            )
        
        post_keyword = ai.extract_content_from_html(
                custom_prompt="""
Read the content and combine relevant keywords from the options provided below.
These keywords will be used for searching photos in the Unsplash API.
Keywords should be short and concise, but not too generic or formulaic.
Keywords must be in English only.
Example: AI, Technology, Innovation
                    
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
        
        
    
    
