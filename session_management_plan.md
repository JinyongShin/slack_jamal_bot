# Session Management Implementation Plan

## 목표 (Goal)
Slack 스레드별 대화 맥락 유지를 위한 Google ADK 세션 관리 구현

## 배경 (Background)
- 현재 문제: 매 메시지마다 새로운 ADK 세션을 생성하여 대화 맥락이 유지되지 않음
- Slack의 `thread_ts`는 이미 수집 중이지만 활용하지 않음
- Google ADK는 세션 기반 대화 히스토리 관리를 지원함

## 핵심 전략 (Core Strategy)
- In-memory dictionary로 `{channel}:{thread_ts}` → `session_id` 매핑 관리
- 대화 내용 자체는 ADK가 자동 저장
- 우리는 Slack thread_ts와 ADK session_id 간의 매핑만 관리
- 세션 TTL: 24시간 (환경변수로 설정 가능)

## 구현 단계 (Implementation Steps)

### Phase 1: 세션 관리 테스트 작성 ✅ COMPLETED
**파일:** `tests/test_session_management.py`

**작성한 테스트:**
- ✅ `test_session_created_for_new_thread` - 새 스레드에 대한 세션 생성
- ✅ `test_session_reused_for_existing_thread` - 동일 스레드의 세션 재사용
- ✅ `test_different_threads_have_separate_sessions` - 다른 스레드는 별도 세션
- ✅ `test_expired_session_is_recreated` - 만료된 세션 재생성
- ✅ `test_session_last_used_updated_on_access` - 접근 시 타임스탬프 갱신
- ✅ `test_multiple_expired_sessions_cleaned_up` - 여러 만료 세션 정리

### Phase 2: ADKAgent 세션 관리 구현
**파일:** `src/llm/adk_agent.py`

**구현 내용:**
1. `__init__` 메서드에 세션 캐시 추가
   ```python
   self._session_cache = {}  # {channel:thread_ts -> {session_id, created_at, last_used}}
   self._session_ttl_hours = int(os.getenv("SESSION_TTL_HOURS", "24"))
   ```

2. `_get_or_create_session(channel, thread_ts, user_id)` 메서드 구현
   - 세션 키 생성: `f"{channel}:{thread_ts}"`
   - 캐시에서 세션 확인
   - 만료된 세션 정리
   - 없으면 새 세션 생성 및 캐시 저장
   - 있으면 last_used 갱신하여 반환

3. `_cleanup_expired_sessions()` 메서드 구현
   - 만료된 세션들을 캐시에서 제거
   - TTL 기반 만료 체크

4. `generate_response()` 메서드 수정
   - `channel`, `thread_ts` 파라미터 추가
   - `_get_or_create_session()` 호출하여 session_id 획득
   - 기존의 새 세션 생성 코드 제거

### Phase 3: MessageProcessor 업데이트
**파일:** `src/bot/message_processor.py`

**구현 내용:**
- `process_message()` 메서드에서 `channel` 파라미터를 `generate_response()`에 전달
- 이미 받고 있는 `thread_ts`, `user` 파라미터도 함께 전달

### Phase 4: Config 업데이트
**파일:** `src/config.py`, `.env.example`

**구현 내용:**
1. `src/config.py`에 `SESSION_TTL_HOURS` 추가
   ```python
   SESSION_TTL_HOURS: int = int(os.getenv("SESSION_TTL_HOURS", "24"))
   ```

2. `.env.example`에 새 환경변수 문서화
   ```env
   # Session Management
   SESSION_TTL_HOURS=24
   ```

### Phase 5: 기존 테스트 업데이트
**파일:** `tests/test_adk_agent.py`, `tests/unit/test_message_processor.py`

**구현 내용:**
- 새 파라미터(`channel`, `thread_ts`)에 맞게 테스트 수정
- Mock 객체 업데이트

### Phase 6: 통합 테스트 및 검증
1. `pytest`로 모든 테스트 실행
2. 로컬 Slack 환경에서 실제 테스트
   - 동일 스레드 내 연속 대화
   - 다른 스레드 간 격리 확인

## TDD 사이클 (TDD Cycle)

각 Phase는 다음 순서로 진행:
1. **Red**: 실패하는 테스트 작성
2. **Green**: 테스트를 통과하는 최소 구현
3. **Refactor**: 코드 정리 및 개선

## 파일 수정 목록 (Files to Modify)

### 신규 파일
- ✅ `tests/test_session_management.py` - 세션 관리 테스트

### 수정 파일
- `src/llm/adk_agent.py` - 세션 관리 로직 추가
- `src/bot/message_processor.py` - channel 파라미터 전달
- `src/config.py` - SESSION_TTL_HOURS 추가
- `.env.example` - 새 환경변수 문서화
- `tests/test_adk_agent.py` - 기존 테스트 업데이트
- `tests/unit/test_message_processor.py` - 기존 테스트 업데이트

## 기대 효과 (Expected Benefits)
- ✅ 동일 Slack 스레드에서 연속적인 대화 가능
- ✅ 이전 대화 맥락을 기억하는 AI 응답
- ✅ 스레드별로 독립적인 대화 세션 유지
- ✅ 자동 세션 만료로 메모리 효율성 확보
- ✅ 추가 Slack 권한이나 사용자 조치 불필요

## 제약 사항 (Constraints)
- 봇 재시작 시 in-memory 캐시 초기화 (새 대화로 시작)
- 메모리 기반이므로 대규모 트래픽에는 Redis 등으로 업그레이드 필요
- 단일 봇 인스턴스 환경에 적합 (multi-instance 환경은 추가 작업 필요)

## 다음 단계 (Next Steps)
1. ✅ Phase 1 완료: 테스트 작성
2. ✅ Phase 2 완료: ADKAgent 구현
3. ✅ Phase 3 완료: MessageProcessor 업데이트
4. ✅ Phase 4 완료: Config 업데이트
5. ✅ Phase 5 완료: 기존 테스트 업데이트
6. ✅ Phase 6 완료: 통합 테스트

## 구현 완료 ✅
- 모든 Phase 완료 (2025-10-30)
- 테스트 결과: 27 passed, 4 skipped
- 상세 내용: `session_management_dev.md` 참조

## 참고 자료 (References)
- Google ADK Python SDK: `/google/adk-python`
- 현재 코드베이스: `src/llm/adk_agent.py`, `src/bot/slack_handler.py`
- ADK 세션 관리 문서: Context7에서 확인한 session_service 사용법
