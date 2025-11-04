# Multi-Agent Debate System

Google Agent Development Kit (ADK)를 활용한 3개 에이전트 토론 시스템입니다.

## 주요 기능

- **3개 에이전트 토론 시스템**:
  - **AgentJamal (Proposer)**: 아이디어 제안, 긍정적 측면 강조
  - **AgentRyan (Opposer)**: 비판적 분석, 문제점 지적
  - **AgentJames (Mediator)**: 의견 종합, 균형잡힌 결론 도출
- **AI 에이전트 기반 대화**: Google ADK + Gemini 2.0 Flash를 사용한 고품질 대화
- **실시간 정보 검색**:
  - Google Search 도구 내장 (최신 정보 자동 검색)
  - 날씨, 뉴스, 일반 정보 등 모든 검색 가능
- **공유 대화 컨텍스트**:
  - 3개 에이전트가 동일 스레드의 대화 히스토리 공유
  - Google ADK 세션 관리를 통한 자동 컨텍스트 공유
  - 경량 파일 기반 세션 레지스트리
  - 자동 세션 만료 (기본 24시간)
- **구조화된 토론 흐름**:
  - 에이전트 간 자동 멘션
  - 합의 도달 또는 반복 논점 시 자동 종료

## 프로젝트 구조

```
slack_jamal_bot/
├── src/
│   ├── bot/
│   │   ├── slack_handler.py      # Slack 이벤트 처리
│   │   └── message_processor.py  # 메시지 처리 로직
│   ├── llm/
│   │   ├── adk_agent.py          # Multi-role ADK Agent (공유 세션)
│   │   └── agent_roles.py        # 에이전트 역할 정의 (Proposer/Opposer/Mediator)
│   ├── utils/
│   │   ├── logger.py             # 로깅 설정
│   │   └── session_registry.py   # 공유 세션 레지스트리 (thread-safe)
│   ├── config.py                 # 환경 설정
│   └── main.py                   # 봇 실행 진입점
├── tests/
│   ├── test_adk_agent.py         # ADK Agent 테스트
│   ├── smoke_test.py             # 초기화 검증
│   ├── unit/                     # 단위 테스트
│   │   ├── test_session_registry.py
│   │   └── ...
│   └── integration/              # 통합 테스트
├── .env.jamal.sample             # AgentJamal 환경변수 템플릿
├── .env.ryan.sample              # AgentRyan 환경변수 템플릿
├── .env.james.sample             # AgentJames 환경변수 템플릿
├── .env.jamal                    # AgentJamal 환경변수 (gitignored)
├── .env.ryan                     # AgentRyan 환경변수 (gitignored)
├── .env.james                    # AgentJames 환경변수 (gitignored)
├── run_agents.sh                 # 3개 에이전트 동시 실행 스크립트
├── stop_agents.sh                # 모든 에이전트 종료 스크립트
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

### 3. Slack 앱 3개 생성

**중요**: 3개의 독립적인 Slack 앱이 필요합니다.

각 에이전트마다 다음 과정을 반복하세요:

1. [Slack API](https://api.slack.com/apps)에서 새 앱 생성
   - App Name: `AgentJamal`, `AgentRyan`, `AgentJames`
2. **OAuth & Permissions**에서 다음 권한 추가:
   - `app_mentions:read` - 멘션 이벤트 읽기
   - `chat:write` - 메시지 보내기
   - `channels:history` - 채널 히스토리 읽기
   - `reactions:write` - 리액션 추가
3. **Socket Mode** 활성화
   - App-Level Token 생성 (scope: `connections:write`)
   - **App Token 복사** (xapp-로 시작)
4. **Event Subscriptions**에서 이벤트 구독:
   - `app_mention` - 앱 멘션 이벤트
5. 앱을 워크스페이스에 설치
   - **Bot User OAuth Token 복사** (xoxb-로 시작)

### 4. Google Generative AI API 키 발급

1. [Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키 발급
2. API 키를 복사 (3개 봇이 공유)

### 5. 환경 변수 설정

샘플 파일을 복사하여 3개의 .env 파일을 생성하세요:

```bash
cp .env.jamal.sample .env.jamal
cp .env.ryan.sample .env.ryan
cp .env.james.sample .env.james
```

각 파일을 열어 다음 값들을 입력하세요:

**.env.jamal** (AgentJamal - Proposer):
- `SLACK_BOT_TOKEN`: AgentJamal의 Bot User OAuth Token
- `SLACK_APP_TOKEN`: AgentJamal의 App-Level Token
- `GOOGLE_GENAI_API_KEY`: Google AI Studio에서 발급받은 API 키

**.env.ryan** (AgentRyan - Opposer):
- `SLACK_BOT_TOKEN`: AgentRyan의 Bot User OAuth Token
- `SLACK_APP_TOKEN`: AgentRyan의 App-Level Token
- `GOOGLE_GENAI_API_KEY`: 동일한 Google API 키 (3개 봇 공유)

**.env.james** (AgentJames - Mediator):
- `SLACK_BOT_TOKEN`: AgentJames의 Bot User OAuth Token
- `SLACK_APP_TOKEN`: AgentJames의 App-Level Token
- `GOOGLE_GENAI_API_KEY`: 동일한 Google API 키 (3개 봇 공유)

**참고**:
- 각 봇은 고유한 Slack 토큰이 필요합니다
- GOOGLE_GENAI_API_KEY는 3개 봇이 동일한 값을 사용합니다

## 실행 방법

### 방법 1: 3개 에이전트 동시 실행 (권장)

```bash
# 모든 에이전트 시작
./run_agents.sh

# 종료하려면 Ctrl+C 또는
./stop_agents.sh
```

### 방법 2: 개별 에이전트 실행

**AgentJamal 실행:**
```bash
set -a && source .env.jamal && set +a
uv run python -m src.main
```

**AgentRyan 실행:**
```bash
set -a && source .env.ryan && set +a
uv run python -m src.main
```

**AgentJames 실행:**
```bash
set -a && source .env.james && set +a
uv run python -m src.main
```

### 방법 3: 초기화 검증 (smoke test)
```bash
PYTHONPATH=. uv run python tests/smoke_test.py
```

## 사용 방법

### 토론 시작

Slack에서 아무 에이전트나 멘션하여 토론을 시작하세요:

```
@AgentJamal AI 기술의 미래에 대해 토론해볼까요?
```

### 토론 진행 예시

```
사용자: @AgentJamal AI 기술이 일자리를 대체할까요?

AgentJamal (Proposer):
AI 기술은 새로운 일자리를 창출할 것입니다.
과거 산업혁명 때도 기계가 일부 일자리를 대체했지만,
더 많은 새로운 직종이 생겨났습니다.
@AgentRyan 당신의 의견은 어떤가요?

AgentRyan (Opposer):
흥미로운 관점이지만, 몇 가지 우려사항이 있습니다.
AI의 발전 속도는 과거 산업혁명과는 비교할 수 없을 정도로 빠릅니다.
단기적으로 대량 실업이 발생할 수 있으며...
@AgentJames 중재를 부탁드립니다.

AgentJames (Mediator):
두 분의 의견을 종합하면, AI가 일자리에 미치는 영향은
단기와 장기로 나누어 볼 필요가 있습니다.
- 단기: 일부 직종에서 대체 발생
- 장기: 새로운 직종 창출 및 생산성 향상
토론을 종료합니다. [최종 결론 요약]
```

### 단독 질문

개별 에이전트에게 직접 질문할 수도 있습니다:

```
@AgentJamal 오늘 서울 날씨 어때?
@AgentRyan 이 프로젝트의 위험 요소는?
@AgentJames 두 의견을 종합하면?
```

**특징:**
- 모든 에이전트가 Google Search를 자동으로 사용하여 최신 정보를 제공합니다
- 동일 스레드 내에서 3개 에이전트가 대화 히스토리를 공유합니다
- 에이전트 간 자동 멘션으로 자연스러운 토론이 진행됩니다
- AgentJames가 합의 도달 또는 반복 시 토론을 자동으로 종료합니다

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

### 전체 시스템 구조

```
┌──────────────────────────────────────────────────────────────┐
│                         Slack Workspace                       │
│  User mentions @AgentJamal, @AgentRyan, or @AgentJames       │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ Socket Mode (3 connections)
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ AgentJamal   │      │ AgentRyan    │      │ AgentJames   │
│ (Proposer)   │      │ (Opposer)    │      │ (Mediator)   │
└──────────────┘      └──────────────┘      └──────────────┘
        │                     │                     │
        │                     │                     │
        │     ┌───────────────┴───────────────┐     │
        └─────┤  Shared Session Registry      ├─────┘
              │  (FileSessionRegistry)         │
              │  thread_ts → session_id        │
              └───────────────┬────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   ADK Session    │
                    │ (Conversation    │
                    │   History)       │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Gemini 2.0     │
                    │   + google_search│
                    └──────────────────┘
```

### 개별 에이전트 구조

```
┌─────────────────────────────────────────┐
│  Single Agent Instance (any role)       │
│  ┌────────────────────────────────┐    │
│  │  SlackBot Handler              │    │
│  │  - Socket Mode listener        │    │
│  │  - Event routing               │    │
│  └────────────────────────────────┘    │
│               │                         │
│               ▼                         │
│  ┌────────────────────────────────┐    │
│  │  MessageProcessor              │    │
│  │  - Text cleaning               │    │
│  │  - Context injection           │    │
│  └────────────────────────────────┘    │
│               │                         │
│               ▼                         │
│  ┌────────────────────────────────┐    │
│  │  ADKAgent (role-specific)      │    │
│  │  - Role: proposer/opposer/     │    │
│  │          mediator               │    │
│  │  - Shared session access       │    │
│  │  - Google Search tool          │    │
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### 핵심 특징

1. **공유 세션 레지스트리**
   - 3개 에이전트가 같은 `session_id` 사용
   - 파일 기반 (./shared_sessions.json)
   - fcntl 파일 잠금으로 동시성 보장

2. **ADK 세션 관리**
   - Google ADK가 대화 히스토리 자동 관리
   - 별도 DB 불필요
   - 스레드별 독립적인 컨텍스트

3. **역할 기반 Instruction**
   - 각 에이전트가 고유한 역할과 말투
   - agent_roles.py에 중앙 관리
   - 환경 변수로 역할 선택

## 마이그레이션 히스토리

### Phase 1-5: Gemini API → Google ADK
이 프로젝트는 기존 Gemini API에서 Google ADK로 마이그레이션되었습니다:
- **이전**: GeminiClient + 수동 tool_handlers (weather, news)
- **현재**: ADKAgent + google_search 내장
- **개선**: 코드 54% 감소, 실시간 정보 검색 가능

자세한 내용은 `migration_plan.md`와 `PHASE5_RESULTS.md`를 참조하세요.

### Phase 6: Multi-Agent Debate System
단일 봇에서 3개 에이전트 토론 시스템으로 확장:
- **이전**: 단일 AgentJamal 봇
- **현재**: AgentJamal (Proposer) + AgentRyan (Opposer) + AgentJames (Mediator)
- **핵심 변경사항**:
  - FileSessionRegistry 추가 (공유 세션 관리)
  - agent_roles.py 추가 (역할별 instruction)
  - 멀티 인스턴스 실행 지원
  - 공유 대화 컨텍스트
- **개선**: 구조화된 토론, 다각적 분석, 균형잡힌 결론

## 라이선스

MIT License
