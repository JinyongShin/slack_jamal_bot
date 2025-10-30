# AgentJamal Slack Bot

Google Agent Development Kit (ADK)를 활용한 지능형 Slack 챗봇입니다.

## 주요 기능

- **Slack 메시지 자동 응답**: @AgentJamal 멘션 시 자동 응답
- **AI 에이전트 기반 대화**: Google ADK + Gemini 2.0 Flash를 사용한 고품질 대화
- **실시간 정보 검색**:
  - Google Search 도구 내장 (최신 정보 자동 검색)
  - 날씨, 뉴스, 일반 정보 등 모든 검색 가능
- **건방진 개성**: 오만하고 건방진 AgentJamal의 독특한 말투
- **스레드 대화**: 스레드 내에서 맥락 유지

## 프로젝트 구조

```
slack_jamal_bot/
├── src/
│   ├── bot/
│   │   ├── slack_handler.py      # Slack 이벤트 처리
│   │   └── message_processor.py  # 메시지 처리 로직
│   ├── llm/
│   │   └── adk_agent.py          # Google ADK Agent (google_search 내장)
│   ├── utils/
│   │   └── logger.py             # 로깅 설정
│   ├── config.py                 # 환경 설정
│   └── main.py                   # 봇 실행 진입점
├── tests/
│   ├── test_adk_agent.py         # ADK Agent 테스트
│   ├── smoke_test.py             # 초기화 검증
│   ├── unit/                     # 단위 테스트
│   └── integration/              # 통합 테스트
├── .env.example                  # 환경변수 템플릿
├── migration_plan.md             # 마이그레이션 계획
├── PHASE5_RESULTS.md             # Phase 5 검증 결과
└── README.md
```

## 설치 및 설정

### 1. 저장소 클론

```bash
git clone <repository-url>
cd slack_jamal_bot
```

### 2. Python 환경 설정

Python 3.11.9 이상이 필요합니다.

```bash
# uv를 사용하여 의존성 설치
uv sync
```

### 3. Slack 앱 설정

1. [Slack API](https://api.slack.com/apps)에서 새 앱 생성
2. **OAuth & Permissions**에서 다음 권한 추가:
   - `app_mentions:read` - 멘션 이벤트 읽기
   - `chat:write` - 메시지 보내기
   - `reactions:write` - 리액션 추가
3. **Socket Mode** 활성화
4. **Event Subscriptions**에서 이벤트 구독:
   - `app_mention` - 앱 멘션 이벤트
5. 앱을 워크스페이스에 설치

### 4. Google Generative AI API 키 발급

1. [Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키 발급
2. API 키를 복사

### 5. 환경 변수 설정

```bash
cp .env.example .env
```

.env 파일을 열어 다음 값을 입력:

```env
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
GOOGLE_GENAI_API_KEY=your-google-genai-api-key-here
LOG_LEVEL=INFO
```

## 실행 방법

### 방법 1: 직접 실행
```bash
python -m src.main
```

### 방법 2: uv 사용
```bash
uv run python -m src.main
```

### 방법 3: 초기화 검증 (smoke test)
```bash
PYTHONPATH=. uv run python tests/smoke_test.py
```

## 사용 방법

Slack에서 봇을 멘션하여 사용:

```
@AgentJamal 안녕하세요!
@AgentJamal 오늘 서울 날씨 어때?
@AgentJamal 2024년 노벨상 수상자는 누구야?
@AgentJamal 최신 AI 뉴스 알려줘
```

**특징**: AgentJamal은 Google Search를 자동으로 사용하여 최신 정보를 제공합니다!

## 트러블슈팅

### Socket Mode 연결 실패

**증상**: `SocketModeClient failed to connect`

**해결 방법:**
- SLACK_APP_TOKEN이 올바른지 확인 (`xapp-`로 시작)
- Slack 앱에서 Socket Mode가 활성화되었는지 확인
- 네트워크 연결 확인

### Google API 오류

**증상**: `Error generating response`

**해결 방법:**
- GOOGLE_GENAI_API_KEY가 올바른지 확인
- [Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키 재발급
- API 키에 공백이나 줄바꿈이 없는지 확인

### 초기화 실패

**증상**: `ModuleNotFoundError: No module named 'src'`

**해결 방법:**
```bash
# PYTHONPATH 지정하여 실행
PYTHONPATH=. python -m src.main
```

### App name mismatch 경고

**증상**: `App name mismatch detected` 경고 메시지

**해결 방법**: 이 경고는 ADK 내부 경고로 기능에 영향이 없습니다. 무시해도 됩니다.

## 테스트

```bash
# 모든 테스트 실행
uv run pytest tests/ --ignore=tests/integration

# Smoke test (초기화 검증)
PYTHONPATH=. uv run python tests/smoke_test.py

# 특정 테스트만 실행
uv run pytest tests/unit/test_message_processor.py -v
```

## 기술 스택

- **Python**: 3.11.9
- **패키지 관리**: uv
- **Slack SDK**: slack-bolt, slack-sdk
- **AI Framework**: Google ADK (Agent Development Kit) v1.17.0
- **LLM**: Gemini 2.0 Flash
- **도구**: google_search (ADK 내장)
- **기타**: python-dotenv

## 아키텍처

```
┌─────────────┐
│    Slack    │ ─── Socket Mode ───┐
└─────────────┘                     │
                                    ▼
                            ┌─────────────────┐
                            │ SlackBot Handler│
                            └─────────────────┘
                                    │
                                    ▼
                          ┌──────────────────────┐
                          │ MessageProcessor     │
                          └──────────────────────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │  ADKAgent     │
                            │  (Gemini 2.0) │
                            └───────────────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │ google_search │
                            │    (Tool)     │
                            └───────────────┘
```

## 마이그레이션 히스토리

이 프로젝트는 기존 Gemini API에서 Google ADK로 마이그레이션되었습니다:

- **이전**: GeminiClient + 수동 tool_handlers (weather, news)
- **현재**: ADKAgent + google_search 내장
- **개선**: 코드 54% 감소, 실시간 정보 검색 가능

자세한 내용은 `migration_plan.md`와 `PHASE5_RESULTS.md`를 참조하세요.

## 라이선스

MIT License
