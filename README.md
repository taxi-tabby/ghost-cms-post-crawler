# Web Crawler and Content Publisher

이 프로젝트는 웹 크롤링을 통해 콘텐츠를 수집하고, AI를 이용해 콘텐츠를 가공한 후 CMS(Ghost)에 게시하는 자동화 시스템입니다.

## 프로젝트 구조

- `app.py`: 메인 실행 파일
- `crawler.py`: 웹 크롤링 기능을 담당하는 모듈
- `store.py`: URL 데이터베이스 관리 모듈
- `google_ai_studio.py`: Google의 Gemini AI API 연동 모듈
- `unsplash.py`: Unsplash API를 통한 이미지 검색 모듈
- `cms_client.py`: Ghost CMS API 연동 모듈
- `targeturl_base.json`: 크롤링 대상 URL 및 패턴 정의 파일
- `tests/`: 테스트 코드 디렉토리

## 설치 방법

1. 프로젝트를 클론합니다:
   ```bash
   git clone [repository-url]
   cd [repository-directory]
   ```

2. 필요한 패키지를 설치합니다:
   ```bash
   pip install -r requirements.txt
   ```
   
   필요한 주요 패키지:
   - requests
   - beautifulsoup4
   - PyJWT
   - pytest (테스트용)



## 테스트

이 프로젝트는 pytest를 사용하여 테스트합니다:

```bash
pytest -vv -s    
```

## 환경 설정

다음 API 키가 필요합니다:

1. Google AI Studio(Gemini) API 키
2. Unsplash API 키
3. Ghost CMS Admin API 키

## 사용 방법

### 해당 프로젝트를 fork 하기
1. 프로젝트 repository 를 fork 하기
2. app.py 에 작성된 프롬프트를 사용하려는 서비스에 맞게 수정하기.
3. app.py 하단에 작성된 tags 를 수정하기.
4. 저장하기. (명령줄 실행) 으로.




### 명령줄 실행

```bash
python app.py --unsplash-access-key YOUR_UNSPLASH_KEY \
              --google-ai-api-key YOUR_GOOGLE_AI_KEY \
              --cms-admin-api-key YOUR_GHOST_ADMIN_API_KEY \
              --cms-url YOUR_GHOST_CMS_URL
```


그리고 app.py를 수정하여 환경 변수를 로드하도록 할 수 있습니다.

## Crontab 설정 (권장)

자동화된 실행을 위해 crontab을 사용하는 것이 권장됩니다.

1. 아래 명령어로 crontab 편집기를 엽니다:
   ```bash
   crontab -e
   ```

2. 다음과 같이 작업을 추가합니다:
   ```
   # 매일 오전 9시에 실행
   0 9 * * * cd /path/to/your/project && python app.py --unsplash-access-key YOUR_UNSPLASH_KEY --google-ai-api-key YOUR_GOOGLE_AI_KEY --cms-admin-api-key YOUR_GHOST_ADMIN_API_KEY --cms-url YOUR_GHOST_CMS_URL >> /path/to/logfile.log 2>&1
   ```

3. 실행 주기 예시:
   - `*/30 * * * *`: 30분마다 실행
   - `0 */2 * * *`: 2시간마다 실행
   - `0 9,18 * * *`: 매일 오전 9시와 오후 6시에 실행
   - `0 9 * * 1-5`: 평일(월-금) 오전 9시에 실행

## 동작 과정

1. `targeturl_base.json`에서 정의된 URL 중 무작위로 2개를 선택
2. 각 URL에서 정의된 패턴에 맞게 링크를 추출
3. 추출된 링크 중 하나를 무작위로 선택하여 콘텐츠 크롤링
4. 이미 크롤링된 URL인지 SQLite 데이터베이스로 확인
5. Google Gemini AI를 사용하여 콘텐츠 제목과 본문을 가공 (한글 번역 및 요약)
6. Unsplash API를 사용하여 관련 이미지 검색
7. Ghost CMS API를 통해 가공된 콘텐츠와 이미지를 블로그에 게시

## 주의사항

- 크롤링은 대상 웹사이트의 이용약관을 준수하여 진행해야 합니다.
- API 키는 절대 소스 코드에 직접 입력하지 마시고, 환경 변수나 별도의 설정 파일을 통해 관리하세요.
- 과도한 요청으로 인한 API 사용량 제한에 주의하세요.

## 적용 예시

이 프로젝트를 통해 운영되는 사이트 예시:
- [SmallBrain Lab Blog](https://blog.smallbrain-labo.work/)



