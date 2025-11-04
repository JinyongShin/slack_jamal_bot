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
- **하이브리드 아키텍처**:
  - **Orchestrator Pattern**: 토론 흐름을 프로그래매틱하게 제어
  - **Visual Mentions**: Slack에서 자연스러운 대화 흐름 관찰 가능
  - **Independent Sessions**: 각 에이전트가 독립적인 세션 유지
- **구조화된 토론 흐름**:
  - Jamal (제안) → James (요약) → Ryan (반론) → James (종료 판단)
  - 자동 루프: 종료 조건 도달까지 자동 진행
  - 합의 도달 또는 반복 논점 시 James가 자동 종료

## 프로젝트 구조

```
slack_jamal_bot/
├── src/
│   ├── agents/
│   │   ├── jamal/                # AgentJamal (Proposer)
│   │   │   ├── agent.py          # File-based agent definition
│   │   │   └── __init__.py
│   │   ├── ryan/                 # AgentRyan (Opposer)
│   │   │   ├── agent.py
│   │   │   └── __init__.py
│   │   └── james/                # AgentJames (Mediator)
│   │       ├── agent.py
│   │       └── __init__.py
│   ├── bot/
│   │   ├── slack_handler.py      # Slack 이벤트 처리 (orchestrator 지원)
│   │   └── message_processor.py  # 메시지 처리 로직
│   ├── llm/
│   │   ├── adk_agent.py          # ADK Agent (독립 세션)
│   │   └── agent_roles.py        # 에이전트 역할 정의
│   ├── orchestrator/
│   │   ├── debate_orchestrator.py # 토론 흐름 제어
│   │   └── __init__.py
│   ├── utils/
│   │   └── logger.py             # 로깅 설정
│   ├── config.py                 # 환경 설정
│   ├── main.py                   # 단일 봇 실행 (레거시)
│   └── main_debate.py            # 멀티 에이전트 Orchestrator
├── tests/
│   ├── test_adk_agent.py         # ADK Agent 테스트
│   ├── smoke_test.py             # 초기화 검증
│   ├── unit/                     # 단위 테스트
│   │   ├── test_message_processor.py
│   │   └── ...
│   └── integration/              # 통합 테스트
├── .env.sample                   # 환경변수 템플릿 (Orchestrator Mode용)
├── .env.jamal.sample             # AgentJamal 환경변수 템플릿 (레거시)
├── .env.ryan.sample              # AgentRyan 환경변수 템플릿 (레거시)
├── .env.james.sample             # AgentJames 환경변수 템플릿 (레거시)
├── run_agents.sh                 # 3개 에이전트 동시 실행 스크립트 (레거시)
├── stop_agents.sh                # 모든 에이전트 종료 스크립트 (레거시)
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

### 3. Slack 앱 생성

**Orchestrator Mode**: 3개의 독립 Slack 앱 필요 (각 에이전트가 자신의 봇으로 메시지 전송)

**중요**: 3개 에이전트가 각각 다른 봇 계정으로 메시지를 보내기 위해 3개의 Slack 앱을 만들어야 합니다.

#### 3-1. AgentJamal (Proposer) 앱 생성

1. [Slack API](https://api.slack.com/apps)에서 새 앱 생성
   - App Name: `AgentJamal`
2. **OAuth & Permissions**에서 다음 권한 추가:
   - `app_mentions:read` - 멘션 이벤트 읽기
   - `chat:write` - 메시지 보내기
   - `channels:history` - 채널 히스토리 읽기
   - `reactions:write` - 리액션 추가
3. **Socket Mode** 활성화
   - App-Level Token 생성 (scope: `connections:write`)
   - **App Token 복사** (xapp-로 시작) → `SLACK_APP_TOKEN`
4. **Event Subscriptions**에서 이벤트 구독:
   - `app_mention` - 앱 멘션 이벤트
5. 앱을 워크스페이스에 설치
   - **Bot User OAuth Token 복사** (xoxb-로 시작) → `SLACK_BOT_TOKEN_JAMAL`

#### 3-2. AgentRyan (Opposer) 앱 생성

1. [Slack API](https://api.slack.com/apps)에서 새 앱 생성
   - App Name: `AgentRyan`
2. **OAuth & Permissions**에서 동일한 권한 추가 (위와 동일)
   - `chat:write` - **필수** (메시지 전송용)
   - 나머지 권한도 동일하게 추가
3. **Socket Mode는 활성화하지 않아도 됨** ❌
   - Ryan은 메시지 전송만 하고 이벤트 수신은 안함
   - Event Subscriptions도 설정 안해도 됨
4. 앱을 워크스페이스에 설치
   - **Bot User OAuth Token 복사** (xoxb-로 시작) → `SLACK_BOT_TOKEN_RYAN`

#### 3-3. AgentJames (Mediator) 앱 생성

1. [Slack API](https://api.slack.com/apps)에서 새 앱 생성
   - App Name: `AgentJames`
2. **OAuth & Permissions**에서 동일한 권한 추가 (위와 동일)
   - `chat:write` - **필수** (메시지 전송용)
   - 나머지 권한도 동일하게 추가
3. **Socket Mode는 활성화하지 않아도 됨** ❌
   - James는 메시지 전송만 하고 이벤트 수신은 안함
   - Event Subscriptions도 설정 안해도 됨
4. 앱을 워크스페이스에 설치
   - **Bot User OAuth Token 복사** (xoxb-로 시작) → `SLACK_BOT_TOKEN_JAMES`

**요약**:
- **Jamal**: Socket Mode ✅ + Event Subscriptions ✅ (토론 트리거)
- **Ryan/James**: 메시지 전송만 (Socket Mode ❌)

### 4. Google Generative AI API 키 발급

1. [Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키 발급
2. API 키를 복사

### 5. 환경 변수 설정

샘플 파일을 복사하여 .env 파일을 생성하세요:

```bash
cp .env.sample .env
```

.env 파일을 열어 다음 값들을 입력하세요:

```bash
# 3개 봇 토큰 (각각 다른 Slack 앱의 토큰)
SLACK_BOT_TOKEN_JAMAL=xoxb-your-jamal-bot-token
SLACK_BOT_TOKEN_RYAN=xoxb-your-ryan-bot-token
SLACK_BOT_TOKEN_JAMES=xoxb-your-james-bot-token

# Socket Mode 토큰 (Jamal 앱의 App-Level Token)
SLACK_APP_TOKEN=xapp-your-app-token

# Google AI API 키
GOOGLE_GENAI_API_KEY=your-google-genai-api-key
```

**중요**:
- 3개의 `SLACK_BOT_TOKEN_*` 모두 필요
- `SLACK_APP_TOKEN`은 Jamal 앱의 App-Level Token 사용
- `GOOGLE_GENAI_API_KEY`는 모든 에이전트가 공유

**레거시 모드 (3개 독립 프로세스)**:
필요시 `.env.jamal`, `.env.ryan`, `.env.james` 파일로 각각 실행 가능

## 실행 방법

### Orchestrator Mode (권장) ✅

하나의 프로세스에서 모든 에이전트 실행:

```bash
uv run python -m src.main_debate
```

**특징:**
- ✅ **3개 Slack 봇**으로 각 에이전트가 자신의 계정으로 메시지 전송
- ✅ Slack에서 실제로 3명이 대화하는 것처럼 보임
- ✅ 프로그래매틱 토론 흐름 제어
- ✅ 자동 루프 실행 (종료 조건까지)
- ✅ 독립적인 세션 관리 (에이전트별 context 유지)

**실행 전 확인:**
- `.env` 파일이 있는지 확인
- 3개 봇 토큰: `SLACK_BOT_TOKEN_JAMAL`, `SLACK_BOT_TOKEN_RYAN`, `SLACK_BOT_TOKEN_JAMES`
- Socket Mode 토큰: `SLACK_APP_TOKEN`
- API 키: `GOOGLE_GENAI_API_KEY`

### 레거시 Mode (3개 독립 앱) ⚠️

> **참고**: 이 방식은 더 이상 권장하지 않습니다. Orchestrator Mode를 사용하세요.

개별 프로세스로 각 에이전트 실행:

```bash
# 터미널 1
set -a && source .env.jamal && set +a
uv run python -m src.main

# 터미널 2
set -a && source .env.ryan && set +a
uv run python -m src.main

# 터미널 3
set -a && source .env.james && set +a
uv run python -m src.main
```

또는 스크립트 사용:
```bash
./run_agents.sh  # 시작
./stop_agents.sh # 종료
```

**단점:**
- ❌ 3개의 독립된 Slack 앱 필요
- ❌ 3개 프로세스 관리 복잡
- ❌ 수동으로 토론 진행 필요
- ❌ Orchestrator 없음

## 사용 방법

### 토론 시작 (Orchestrator Mode)

Slack에서 **`@AgentJamal`을 멘션하면 자동으로 토론이 시작**됩니다:

```
@AgentJamal AI 기술의 미래에 대해 토론해볼까요?
```

**중요 사항**:
- **토론 시작**: **`@AgentJamal`만 멘션**하면 토론 시작 (Proposer 역할)
- **이유**: AgentJamal 앱만 Socket Mode 연결 (이벤트 수신)
- **메시지 전송**: 토론이 시작되면 3개 봇(@AgentJamal, @AgentRyan, @AgentJames)이 각자 메시지 전송
- **시각적 효과**: Slack에서 3명이 실제로 대화하는 것처럼 보임

**아키텍처 참고**:
- Ryan과 James는 Socket Mode 연결 없음 (메시지 전송만)
- Jamal이 트리거 역할 (토론 시작자)

토론 자동 진행:
1. **AgentJamal (Proposer)**: 긍정적 주장 제시
2. **AgentJames (Mediator)**: Jamal의 의견 요약, Ryan에게 전달
3. **AgentRyan (Opposer)**: 비판적 분석 제시
4. **AgentJames (Mediator)**: 종료 판단 또는 Jamal에게 재요청
5. (반복) 종료 조건까지 자동 루프

### 토론 진행 예시

```
사용자: @AgentJamal AI 기술이 일자리를 대체할까요?

🤖 [토론 자동 진행]

@AgentJamal (봇 계정):
AI 기술은 새로운 일자리를 창출할 것입니다.
과거 산업혁명 때도 기계가 일부 일자리를 대체했지만,
더 많은 새로운 직종이 생겨났습니다.
@AgentJames

@AgentJames (봇 계정):
Jamal님은 AI가 새로운 일자리를 창출할 것이라 보십니다.
역사적 사례를 근거로 제시하셨네요.
@AgentRyan 반론 부탁드립니다.

@AgentRyan (봇 계정):
흥미로운 관점이지만, 몇 가지 우려사항이 있습니다.
AI의 발전 속도는 과거 산업혁명과는 비교할 수 없을 정도로 빠릅니다.
단기적으로 대량 실업이 발생할 수 있으며...
@AgentJames

@AgentJames (봇 계정):
토론을 종료합니다.

두 분의 의견을 종합하면, AI가 일자리에 미치는 영향은
단기와 장기로 나누어 볼 필요가 있습니다:
- 단기: 일부 직종에서 대체 발생 가능
- 장기: 새로운 직종 창출 및 생산성 향상

[종료]
```

**시각적 효과**:
- Slack에서 `@AgentJamal`, `@AgentRyan`, `@AgentJames` 세 명이 실제로 대화
- 각 봇의 프로필 사진과 이름으로 표시
- 자연스러운 3자 토론 형태

**특징:**
- 사용자는 첫 멘션만 하면 자동으로 토론 진행
- Orchestrator가 토론 흐름 제어
- Slack에서 자연스러운 대화 형태로 관찰 가능
- AgentJames가 종료 조건 자동 판단
- 최대 10라운드까지 진행 (설정 변경 가능)

## 최근 수정 사항

### 2025-01-04: 3개 독립 봇으로 메시지 전송 (Major Update)
- **변경**: 1개 봇 → 3개 독립 봇으로 메시지 전송
- **이유**: 사용자가 각 에이전트가 자신의 봇 계정으로 메시지를 보내는 것을 원함
- **구현**:
  - Config: 3개 토큰 로드 (`SLACK_BOT_TOKEN_JAMAL`, `_RYAN`, `_JAMES`)
  - main_debate.py: 3개 WebClient 생성
  - DebateOrchestrator: 에이전트별 client 매핑, speaker 파라미터 추가
- **결과**: Slack에서 `@AgentJamal`, `@AgentRyan`, `@AgentJames`가 각각 메시지 전송
- **설정**: 3개 Slack 앱 필요 (각각 독립 봇)

### 2025-01-04: 봇 멘션 감지 로직 수정
- **문제**: 잘못된 조건 (`if "@AgentJamal" in text`)으로 토론이 시작되지 않음
- **원인**: Slack은 멘션을 `<@USER_ID>` 형식으로 전송 (문자열 `"@AgentJamal"`이 아님)
- **수정**: 조건 제거하여 모든 봇 멘션에서 토론 시작
- **영향**: Orchestrator Mode에서 봇 멘션 시 정상적으로 토론 시작

### 2025-01-04: Session 관리 개선
- **문제**: `session_id` 누락으로 런타임 에러 발생
- **수정**: `_get_or_create_session()` 메서드 추가 (get-or-create 패턴)
- **개선**: 각 에이전트가 독립적인 세션 관리 (`app_name: debate_{agent_name}`)
- **참고**: ADK의 `session_id`는 required 파라미터 (자동 관리 아님)

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

### Orchestrator Mode 구조 (권장)

```
┌──────────────────────────────────────────────────────────┐
│                      Slack Workspace                      │
│               User mentions @AgentJamal                   │
└──────────────────────────────────────────────────────────┘
                              │
                              │ Socket Mode (Jamal only)
                              ▼
                    ┌──────────────────┐
                    │   SlackBot       │
                    │   Handler        │
                    │ (Jamal's token)  │
                    └─────────┬────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ DebateOrchestrator│
                    │ - Flow control   │
                    │ - Active debates │
                    │ - 3 Slack clients│
                    └─────────┬────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ AgentJamal   │      │ AgentRyan    │      │ AgentJames   │
│ (AI Agent)   │      │ (AI Agent)   │      │ (AI Agent)   │
│ app_name:    │      │ app_name:    │      │ app_name:    │
│ debate_jamal │      │ debate_ryan  │      │ debate_james │
└──────┬───────┘      └──────┬───────┘      └──────┬───────┘
       │                     │                     │
       │    Independent Sessions (per thread)     │
       │                     │                     │
       ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ ADK Session  │      │ ADK Session  │      │ ADK Session  │
│ (Jamal's     │      │ (Ryan's      │      │ (James's     │
│  history)    │      │  history)    │      │  history)    │
└──────┬───────┘      └──────┬───────┘      └──────┬───────┘
       │                     │                     │
       └─────────────────────┼─────────────────────┘
                             ▼
                    ┌──────────────────┐
                    │   Gemini 2.0     │
                    │   + google_search│
                    └──────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ Slack Bot    │      │ Slack Bot    │      │ Slack Bot    │
│ @AgentJamal  │      │ @AgentRyan   │      │ @AgentJames  │
│ (Post msgs)  │      │ (Post msgs)  │      │ (Post msgs)  │
└──────────────┘      └──────────────┘      └──────────────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            ▼
                  ┌────────────────────┐
                  │  Slack Workspace   │
                  │ (3 bots chatting)  │
                  └────────────────────┘
```

### 핵심 특징

1. **3-Bot Visual Architecture** ⭐ NEW
   - **3개 독립 Slack 봇**: 각 에이전트가 자신의 봇 계정으로 메시지 전송
   - **이벤트 수신**: AgentJamal만 Socket Mode 연결 (토론 트리거)
   - **메시지 전송**: 3개 WebClient로 각 봇이 독립적으로 메시지 전송
   - **시각적 효과**: Slack에서 3명이 실제로 대화하는 것처럼 보임

2. **Hybrid Architecture**
   - Orchestrator가 토론 흐름을 프로그래매틱하게 제어
   - Visual mentions는 Slack 관찰용 (기능적 트리거 아님)
   - Active debate tracking으로 이벤트 간섭 방지

3. **Independent Session Management**
   - 각 에이전트가 독립적인 `app_name` 사용
   - ADK가 에이전트별 세션 자동 관리
   - Context 공유는 Slack 메시지를 통해 발생

4. **File-Based Agent Structure**
   - ADK 요구사항: `src/agents/{name}/agent.py`
   - 각 agent.py가 `root_agent` export
   - app_name을 파일 위치에서 자동 추론

5. **Debate Flow Control**
   - 정해진 순서: Jamal → James → Ryan → James
   - James가 종료 조건 판단
   - 최대 라운드 제한으로 무한 루프 방지

## 마이그레이션 히스토리

### Phase 1-5: Gemini API → Google ADK
이 프로젝트는 기존 Gemini API에서 Google ADK로 마이그레이션되었습니다:
- **이전**: GeminiClient + 수동 tool_handlers (weather, news)
- **현재**: ADKAgent + google_search 내장
- **개선**: 코드 54% 감소, 실시간 정보 검색 가능

자세한 내용은 `migration_plan.md`와 `PHASE5_RESULTS.md`를 참조하세요.

### Phase 6: Multi-Agent Debate System (Orchestrator)
단일 봇에서 3개 에이전트 토론 시스템으로 확장:
- **이전**: 단일 AgentJamal 봇
- **현재**: AgentJamal (Proposer) + AgentRyan (Opposer) + AgentJames (Mediator)
- **핵심 변경사항**:
  - **DebateOrchestrator 추가**: 프로그래매틱 토론 흐름 제어
  - **독립 세션 관리**: 각 에이전트가 독립적인 app_name으로 세션 관리
  - **File-based Agent 구조**: `src/agents/{name}/agent.py` 구조로 ADK 요구사항 준수
  - **Hybrid Architecture**: Orchestrator 제어 + Visual mentions for observability
  - **자동 루프**: 종료 조건까지 자동 토론 진행
- **개선**:
  - Session 충돌 해결 (독립 세션으로 "Session not found" 오류 제거)
  - 단일 프로세스 실행 (3개 프로세스 → 1개 프로세스)
  - 프로그래매틱 흐름 제어로 안정적인 토론 진행
  - Slack에서 자연스러운 대화 관찰 가능

## 라이선스

MIT License
