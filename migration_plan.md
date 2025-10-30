# Slack Bot → Google ADK 마이그레이션 작업 계획

**시작일**: 2025-01-30
**목표**: Slack 멘션 → ADK 응답 생성 → Slack 답변 (최소 기능)

---

## Phase 0: 환경 설정
- [x] `pyproject.toml` 수정: `google-adk = "^1.17.0"` 추가
- [x] `uv sync` 실행하여 의존성 설치
- [x] `.env.example` 업데이트: `GOOGLE_GENAI_API_KEY` 추가
- [x] `src/config.py` 수정: 환경 변수 추가 및 검증
- [x] 테스트 실행 가능 확인

**커밋**: `chore: Add google-adk dependency and environment setup`

---

## Phase 1: ADKAgent 클래스 생성 (TDD Cycle 1)

### Test 1.1: ADKAgent 초기화 테스트 (RED)
- [x] `tests/test_adk_agent.py` 파일 생성
- [x] 테스트 작성: `test_adk_agent_initializes_with_api_key`
- [x] 테스트 실행 → 실패 확인 (RED)

### Implementation 1.1: ADKAgent 기본 구조 (GREEN)
- [x] `src/llm/adk_agent.py` 파일 생성
- [x] ADKAgent 클래스 구현 (최소한의 코드)
- [x] 테스트 실행 → 통과 확인 (GREEN)

### Refactor 1.1: 코드 정리 (REFACTOR)
- [x] 타입 힌트 추가
- [x] Docstring 추가
- [x] 테스트 재실행 → 통과 확인

**커밋**: `feat: Implement ADKAgent initialization with API key`

---

## Phase 2: 응답 생성 기능 (TDD Cycle 2)

### Test 2.1: 텍스트 입력 → 응답 생성 테스트 (RED)
- [x] 테스트 작성: `test_generate_response_returns_text`
- [x] 테스트 실행 → 실패 확인 (RED)

### Implementation 2.1: generate_response 메서드 (GREEN)
- [x] GitHub problem_forge 저장소에서 ADK 사용 패턴 분석
- [x] ADK samples에서 InMemoryRunner 패턴 확인
- [x] `ADKAgent.generate_response()` 메서드 구현 (InMemoryRunner 사용)
- [x] 테스트 실행 → 통과 확인 (GREEN)

### Refactor 2.1: 에러 처리 추가 (REFACTOR)
- [x] 기본적인 try-except 추가
- [x] 빈 응답 처리
- [x] 사용하지 않는 import 제거
- [x] 테스트 재실행 → 통과 확인

**커밋**: `feat: Add generate_response method to ADKAgent`

---

## Phase 3: MessageProcessor 통합 (TDD Cycle 3)

### Test 3.1: MessageProcessor가 ADKAgent 사용하는 테스트 (RED)
- [x] `tests/test_message_processor.py` 수정
- [x] 테스트 작성: `test_message_processor_uses_adk_agent`
- [x] 테스트 작성: `test_message_processor_with_adk_agent_ignores_tools`
- [x] 테스트 실행 → 실패 확인 (RED)

### Implementation 3.1: MessageProcessor 수정 (GREEN)
- [x] Context7에서 ADK google_search tool 문서 확인
- [x] ADKAgent에 `google_search` tool 추가
- [x] `src/bot/message_processor.py` 수정
- [x] ADKAgent는 tools를 내부적으로 관리하도록 로직 분리
- [x] 테스트 실행 → 통과 확인 (GREEN)

### Refactor 3.1: 인터페이스 정리 (REFACTOR)
- [x] `_is_adk_agent()` 헬퍼 메서드 추가
- [x] `_generate_response()` 메서드 추출하여 코드 가독성 개선
- [x] 기존 메서드 시그니처 유지 확인
- [x] 테스트 재실행 → 통과 확인 (39 passed, 3 skipped)

**커밋**: `feat: Integrate ADKAgent into MessageProcessor`

---

## Phase 4: Slack 통합 테스트 (TDD Cycle 4)

### Test 4.1: 전체 플로우 통합 테스트 (RED)
- [ ] `tests/test_integration.py` 생성 (또는 수정)
- [ ] 테스트 작성: `test_slack_mention_to_response_flow`
- [ ] 테스트 실행 → 실패 확인 (RED)

### Implementation 4.1: main.py 수정 (GREEN)
- [ ] `src/main.py` 수정
- [ ] GeminiClient → ADKAgent로 초기화 변경
- [ ] 테스트 실행 → 통과 확인 (GREEN)

### Refactor 4.1: 설정 통합 (REFACTOR)
- [ ] Config 클래스 정리
- [ ] Import 구문 정리
- [ ] 테스트 재실행 → 통과 확인

**커밋**: `feat: Integrate ADKAgent into Slack bot main flow`

---

## Phase 5: 로컬 실행 및 검증

### 수동 테스트
- [ ] 환경 변수 설정: `.env` 파일에 `GOOGLE_GENAI_API_KEY` 추가
- [ ] `python -m src.main` 실행
- [ ] Slack에서 봇 멘션
- [ ] 응답 확인
- [ ] 에러 로그 확인

### 문제 발생 시
- [ ] 에러 메시지 기록
- [ ] Context7에서 ADK 문서 재확인
- [ ] 테스트 추가 (발견된 버그에 대해)
- [ ] 수정 후 다시 테스트

**커밋**: `test: Verify Slack integration with ADK agent`

---

## Phase 6: 문서화

- [ ] `README.md` 업데이트 (ADK 사용, 환경 변수, 실행 방법)
- [ ] `migration_dev.md` 작성 (개발 과정, 이슈, 해결 방법)

**커밋**: `docs: Update README and add migration documentation`

---

## Phase 7: 레거시 코드 삭제 (Structural Changes)

### 7.1: 삭제 전 확인
- [ ] `git status` 확인
- [ ] 모든 테스트 실행 → 통과 확인
- [ ] 삭제할 파일 목록 확인

### 7.2: GeminiClient 삭제
- [ ] `src/llm/gemini_client.py` 삭제
- [ ] `src/llm/__init__.py`에서 GeminiClient import 제거
- [ ] 테스트 실행 → 통과 확인

**커밋**: `refactor: Remove deprecated GeminiClient`

### 7.3: Weather Tool 삭제
- [ ] `src/tools/weather.py` 삭제
- [ ] `src/tools/__init__.py`에서 weather import 제거
- [ ] 테스트 실행 → 통과 확인

**커밋**: `refactor: Remove deprecated weather tool`

### 7.4: News Tool 삭제
- [ ] `src/tools/news_rss.py` 삭제
- [ ] `src/tools/__init__.py`에서 news import 제거
- [ ] 테스트 실행 → 통과 확인

**커밋**: `refactor: Remove deprecated news tool`

### 7.5: Tools 디렉토리 정리
- [ ] `src/tools/__init__.py` 확인 (비어있으면 삭제)
- [ ] `src/tools/` 디렉토리 삭제 (비어있으면)
- [ ] 테스트 실행 → 통과 확인

**커밋**: `refactor: Clean up empty tools directory`

### 7.6: 의존성 정리
- [ ] `pyproject.toml`에서 사용하지 않는 의존성 제거
- [ ] `uv sync` 실행
- [ ] 테스트 실행 → 통과 확인

**커밋**: `chore: Remove unused dependencies`

### 7.7: Import 구문 정리
- [ ] 삭제된 모듈 import 검색 및 제거
- [ ] 테스트 실행 → 통과 확인

**커밋**: `refactor: Clean up imports after code deletion`

### 7.8: 테스트 파일 정리
- [ ] 레거시 코드 테스트 파일 삭제
- [ ] 모든 테스트 실행 → 통과 확인

**커밋**: `test: Remove tests for deleted legacy code`

### 7.9: 최종 검증
- [ ] 전체 테스트 스위트 실행
- [ ] Linter 실행
- [ ] 로컬에서 Slack bot 실행 테스트
- [ ] 모든 기능 정상 동작 확인

**커밋**: `refactor: Complete legacy code cleanup`

---

## 진행 상황
- **현재 Phase**: 3 (완료)
- **완료된 테스트**: 11/11 MessageProcessor 테스트 통과
- **다음 작업**: Phase 4 - Slack 통합 테스트
