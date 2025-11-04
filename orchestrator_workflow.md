# 🎯 DebateOrchestrator 완전 분석

## 📚 목차
1. [역할과 책임](#1-역할과-책임)
2. [코드 구조](#2-코드-구조)
3. [동작 흐름](#3-동작-흐름)
4. [핵심 메커니즘](#4-핵심-메커니즘)
5. [진단 이슈](#5-진단-이슈)

---

## 1. 역할과 책임

### 🎭 핵심 역할
**DebateOrchestrator**는 3개 AI 에이전트의 토론을 **프로그래매틱하게 제어**하는 중앙 컨트롤러입니다.

```
사용자 멘션 → SlackBot → DebateOrchestrator → 자동 토론 진행
```

### 📋 책임 영역

| 책임 | 설명 |
|------|------|
| **흐름 제어** | Jamal → James → Ryan → James 순서 강제 |
| **메시지 라우팅** | 각 에이전트의 봇 계정으로 메시지 전송 |
| **상태 관리** | Active debates 추적 (중복 방지) |
| **종료 판단** | James의 응답에서 종료 신호 감지 |
| **컨텍스트 관리** | 누적된 토론 내용을 각 에이전트에 전달 |

---

## 2. 코드 구조

### 🏗️ 클래스 구성

```python
class DebateOrchestrator:
    # 클래스 변수 (모든 인스턴스 공유)
    active_debates: Dict[str, bool] = {}  # thread_ts → 활성 여부
    _lock = threading.Lock()               # 동시성 제어

    # 인스턴스 변수
    self.clients = {                       # 3개 Slack 클라이언트
        "jamal": WebClient,
        "ryan": WebClient,
        "james": WebClient
    }
    self.jamal = ADKAgent                  # AI 에이전트들
    self.ryan = ADKAgent
    self.james = ADKAgent
    self.max_rounds = 10                   # 최대 라운드
```

### 📦 주요 메서드 (8개)

#### Public Methods (2개)
1. **`start_debate()`** - 토론 시작 (백그라운드 스레드 생성)
2. **`is_debate_active()`** - 토론 활성 상태 확인 (클래스 메서드)

#### Private Methods (6개)
3. **`_run_debate()`** - 토론 루프 실행
4. **`_agent_speak()`** - AI 에이전트 응답 생성
5. **`_check_termination()`** - 종료 조건 확인
6. **`_post_with_mention()`** - 멘션 포함 메시지 전송
7. **`_post_message()`** - Slack 메시지 전송
8. **`_lock`** - 스레드 안전성 보장

---

## 3. 동작 흐름

### 🔄 전체 프로세스

```
┌─────────────────────────────────────────────────────────┐
│ 1. start_debate() - 토론 시작                            │
└─────────────────────────────────────────────────────────┘
                     │
                     ├─ active_debates[thread_ts] = True
                     ├─ 백그라운드 스레드 생성
                     └─ _run_debate() 실행
                              │
┌─────────────────────────────────────────────────────────┐
│ 2. _run_debate() - 토론 루프 (최대 10라운드)              │
└─────────────────────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │   Round N (반복)         │
        └────────────┬────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
┌────────┐      ┌────────┐      ┌────────┐
│ Jamal  │──→   │ James  │──→   │ Ryan   │
│제안    │      │요약    │      │반론    │
└────────┘      └────────┘      └────────┘
                                     │
                                     ▼
                               ┌────────┐
                               │ James  │
                               │종료판단 │
                               └────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                terminated?                      계속?
                    │                                 │
                    ▼                                 │
               [토론 종료]                             │
                    │                                 │
                    └─────────────────────────────────┘
                                     │
                                [다음 라운드]
```

### 📝 세부 흐름 (1 라운드)

```python
# Round N 시작
context = "주제: {initial_message}"  # 초기 컨텍스트

# 1단계: Jamal 제안
jamal_response = _agent_speak(jamal, context, thread_ts)
_post_with_mention(jamal_response, "@AgentJames", speaker="jamal")
context += "\n\nAgentJamal: {jamal_response}"

# 2단계: James 요약
james_prompt = f"{context}\n\n위 내용을 요약하고 AgentRyan에게 전달해주세요."
james_summary = _agent_speak(james, james_prompt, thread_ts)
_post_with_mention(james_summary, "@AgentRyan", speaker="james")
context += "\n\nAgentJames: {james_summary}"

# 3단계: Ryan 반론
ryan_response = _agent_speak(ryan, context, thread_ts)
_post_with_mention(ryan_response, "@AgentJames", speaker="ryan")
context += "\n\nAgentRyan: {ryan_response}"

# 4단계: James 종료 판단
james_check_prompt = f"{context}\n\n합의가 이루어졌거나 논의가 반복되면..."
james_check = _agent_speak(james, james_check_prompt, thread_ts)

if _check_termination(james_check):  # "토론을 종료합니다" 감지
    terminated = True
    next_agent = None
else:
    next_agent = "@AgentJamal"

_post_with_mention(james_check, next_agent, speaker="james")
context += "\n\nAgentJames: {james_check}"
```

---

## 4. 핵심 메커니즘

### 🔒 동시성 제어 (Active Debates Registry)

```python
# 클래스 변수로 모든 인스턴스가 공유
active_debates: Dict[str, bool] = {}
_lock = threading.Lock()

# 토론 시작 시
with self._lock:
    if thread_ts in self.active_debates:
        logger.warning("Debate already active")
        return  # 중복 방지!
    self.active_debates[thread_ts] = True

# 토론 종료 시 (finally 블록)
with self._lock:
    if thread_ts in self.active_debates:
        del self.active_debates[thread_ts]
```

**목적**:
- 같은 스레드에서 토론이 중복 실행되는 것 방지
- Slack 이벤트가 중복으로 오는 경우 보호

### 🎭 멀티 봇 메시지 전송

```python
# 초기화 시
self.clients = {
    "jamal": WebClient(token=SLACK_BOT_TOKEN_JAMAL),
    "ryan": WebClient(token=SLACK_BOT_TOKEN_RYAN),
    "james": WebClient(token=SLACK_BOT_TOKEN_JAMES)
}

# 메시지 전송 시
def _post_message(self, ..., speaker: str = "jamal"):
    client = self.clients.get(speaker, self.clients["jamal"])
    client.chat_postMessage(...)  # 해당 봇의 계정으로 전송!
```

**핵심**: `speaker` 파라미터로 어떤 봇 계정을 사용할지 결정

### 🧠 컨텍스트 누적 (Context Building)

```python
context = f"주제: {initial_message}"

# 각 에이전트 발언 후 누적
context += f"\n\nAgentJamal: {jamal_response}"
context += f"\n\nAgentJames: {james_summary}"
context += f"\n\nAgentRyan: {ryan_response}"
context += f"\n\nAgentJames: {james_check}"

# 다음 에이전트는 전체 히스토리를 받음
next_response = agent.generate_response(text=context, ...)
```

**중요**:
- 각 에이전트는 **전체 토론 히스토리**를 받음
- ADK 세션과는 별개로 작동 (세션은 에이전트별 개인 기억)

### 🛑 종료 조건 판단

```python
def _check_termination(self, james_response: str) -> bool:
    termination_phrases = [
        "토론을 종료합니다",
        "토론을 마치겠습니다",
        "논의를 종료합니다"
    ]

    response_lower = james_response.lower()
    for phrase in termination_phrases:
        if phrase.lower() in response_lower:
            return True
    return False
```

**판단 주체**: AgentJames (Mediator)만 종료 결정

### 🧵 백그라운드 실행

```python
def start_debate(self, ...):
    # 백그라운드 스레드 생성 (non-blocking)
    debate_thread = threading.Thread(
        target=self._run_debate,
        args=(channel, thread_ts, initial_message, user_id),
        daemon=True  # 메인 프로세스 종료 시 같이 종료
    )
    debate_thread.start()
    # 즉시 리턴 → Slack 이벤트 핸들러가 블록되지 않음
```

**중요**: Slack 이벤트 핸들러는 빠르게 리턴해야 함 (타임아웃 방지)

---

## 5. 진단 이슈

### ✅ 해결됨: `user_id` 파라미터 활용

**위치**: `src/orchestrator/debate_orchestrator.py:114`

```python
def _run_debate(
    self,
    channel: str,
    thread_ts: str,
    initial_message: str,
    user_id: str
) -> None:
    try:
        logger.info(f"Debate started by user: {user_id} in thread: {thread_ts}")
        # ...
```

**해결 방법**: Option B (로깅 활용) 구현
- 각 토론을 시작한 사용자를 로그에 기록
- 토론 추적 및 디버깅에 유용
- 동작에 영향 없이 가시성 향상

**추가 개선사항**:
- `_post_message()` 메서드에 상세 디버그 로깅 추가
- 어떤 봇 계정이 실제로 메시지를 전송했는지 확인 가능
- Multi-bot 메시지 라우팅 문제 진단에 활용

---

## 📊 전체 아키텍처 요약

```
SlackBot (handler)
      ↓ [app_mention event]
DebateOrchestrator.start_debate()
      ↓ [background thread]
_run_debate() [Loop N times]
      ↓
      ├─ _agent_speak(jamal) → jamal_response
      ├─ _post_message(speaker="jamal") → @AgentJamal 계정으로 Slack에 전송
      ├─ _agent_speak(james) → james_summary
      ├─ _post_message(speaker="james") → @AgentJames 계정으로 Slack에 전송
      ├─ _agent_speak(ryan) → ryan_response
      ├─ _post_message(speaker="ryan") → @AgentRyan 계정으로 Slack에 전송
      ├─ _agent_speak(james) → james_check
      ├─ _check_termination(james_check)
      └─ _post_message(speaker="james") → 종료 또는 계속
```

**핵심 포인트:**
1. **프로그래매틱 제어**: 순서가 코드로 강제됨
2. **멀티 봇**: 각 에이전트가 자신의 봇 계정으로 메시지 전송
3. **컨텍스트 누적**: 전체 토론 히스토리를 계속 전달
4. **백그라운드 실행**: 이벤트 핸들러 블록 방지
5. **동시성 제어**: active_debates 레지스트리로 중복 방지

이 구조 덕분에 자동화된 3자 토론이 가능합니다! 🎉

---

## 📁 파일 위치

- **소스 코드**: `src/orchestrator/debate_orchestrator.py`
- **호출 지점**: `src/main_debate.py`
- **이벤트 핸들러**: `src/bot/slack_handler.py`

## 🔗 관련 문서

- [README.md](./README.md) - 프로젝트 전체 설명
- [CLAUDE.md](./CLAUDE.md) - 개발 방법론
- [migration_plan.md](./migration_plan.md) - 아키텍처 변경 히스토리
