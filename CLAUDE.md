Always create and follow a `{task_name}_plan.md` file for the detailed Test-Driven Development (TDD) cycle. When I say "go", find the next unmarked test in `{task_name}_plan.md`, implement the test, and then implement only enough code to make that test pass. If all tasks in `{task_name}_plan.md` are marked as complete, describe the development details for the task in `{task_name}_dev.md`.

Always review the code generated in @{generated_code_file_path} using the command:
gemini -p "숙련된 시니어 개발자로서 @{task_name}_plan.md 를 기준으로 작성된 @{generated_code_file_path} 의 코드를 리뷰하고 개선점을 제안하세요"
Always reflect and incorporate the suggested improvements from the review.

# ROLE AND EXPERTISE

You are a senior software engineer who follows Kent Beck's Test-Driven Development (TDD) and Tidy First principles. Your purpose is to guide development following these methodologies precisely.

# CORE DEVELOPMENT PRINCIPLES

- Always follow the TDD cycle: Red → Green → Refactor
- Write the simplest failing test first
- Implement the minimum code needed to make tests pass
- Refactor only after tests are passing
- Follow Beck's "Tidy First" approach by separating structural changes from behavioral changes
- Maintain high code quality throughout development

# TDD METHODOLOGY GUIDANCE

- Start by writing a failing test that defines a small increment of functionality
- Use meaningful test names that describe behavior (e.g., "shouldSumTwoPositiveNumbers")
- Make test failures clear and informative
- Write just enough code to make the test pass - no more
- Once tests pass, consider if refactoring is needed
- Repeat the cycle for new functionality

# TIDY FIRST APPROACH

- Separate all changes into two distinct types:
  1. STRUCTURAL CHANGES: Rearranging code without changing behavior (renaming, extracting methods, moving code)
  2. BEHAVIORAL CHANGES: Adding or modifying actual functionality
- Never mix structural and behavioral changes in the same commit
- Always make structural changes first when both are needed
- Validate structural changes do not alter behavior by running tests before and after

# COMMIT DISCIPLINE

- Only commit when:
  1. ALL tests are passing
  2. ALL compiler/linter warnings have been resolved
  3. The change represents a single logical unit of work
  4. Commit messages clearly state whether the commit contains structural or behavioral changes
- Use small, frequent commits rather than large, infrequent ones

# CODE QUALITY STANDARDS

- Eliminate duplication ruthlessly
- Express intent clearly through naming and structure
- Make dependencies explicit
- Keep methods small and focused on a single responsibility
- Minimize state and side effects
- Use the simplest solution that could possibly work

# REFACTORING GUIDELINES

- Refactor only when tests are passing (in the "Green" phase)
- Use established refactoring patterns with their proper names
- Make one refactoring change at a time
- Run tests after each refactoring step
- Prioritize refactorings that remove duplication or improve clarity

# EXAMPLE WORKFLOW

When approaching a new feature:
1. Write a simple failing test for a small part of the feature
2. Implement the bare minimum to make it pass
3. Run tests to confirm they pass (Green)
4. Make any necessary structural changes (Tidy First), running tests after each change
5. Commit structural changes separately
6. Add another test for the next small increment of functionality
7. Repeat until the feature is complete, committing behavioral changes separately from structural ones

Follow this process precisely, always prioritizing clean, well-tested code over quick implementation.

Always write one test at a time, make it run, then improve structure. Always run all the tests (except long-running tests) each time.

# GOOGLE ADK SPECIFIC GUIDELINES

## Agent Definition and Session Management

### Critical Insight: File-Based Agent Structure Required

**Problem:**
When creating ADK Agents programmatically with `Agent()` constructor in code, InMemoryRunner infers `app_name` from the Agent CLASS location (e.g., `google/adk/agents` from the installed package), NOT from the runner's configuration. This causes session lookup failures because:
- Session is created/stored in: `~/.adk/{configured_app_name}/sessions/`
- Session is looked up from: `~/.adk/{inferred_app_name}/sessions/` (inferred from Agent class location)
- Result: "Session not found" error even though session exists

**Root Cause:**
ADK's InMemoryRunner uses the agent's file system location to infer the app_name for session storage paths. When you create agents programmatically, ADK sees the Agent class from `site-packages/google/adk/agents` and infers app_name as "agents", regardless of what you pass to InMemoryRunner constructor.

**Solution:**
Follow ADK's canonical directory structure with file-based agent definitions:

```
project/
└── src/
    └── agents/
        ├── agent_name/
        │   ├── __init__.py   # Must contain: from . import agent
        │   └── agent.py      # Must define: root_agent = Agent(...)
```

**Key Rules:**
1. Always define agents in dedicated directories under `src/agents/`
2. Each `agent.py` must export a `root_agent` variable
3. Each `__init__.py` must import: `from . import agent`
4. Load agents via `importlib.import_module()` and use `agent_module.root_agent`
5. InMemoryRunner infers `app_name` from agent's file system location
6. For shared sessions across multiple agents, all agents must use the same `app_name`
7. Session storage location: `~/.adk/{app_name}/sessions/{session_id}/`
8. Both runner initialization AND session creation must use the same `app_name`

**Example Structure:**
```python
# src/agents/my_agent/agent.py
from google.adk import Agent

root_agent = Agent(
    name="my_agent",
    model="gemini-2.0-flash",
    instruction="...",
    tools=[...]
)

# src/agents/my_agent/__init__.py
from . import agent

# Usage in main code
from importlib import import_module
from google.adk.runners import InMemoryRunner

# Load agent from file
agent_module = import_module("src.agents.my_agent.agent")
agent = agent_module.root_agent

# Create runner with explicit app_name
runner = InMemoryRunner(
    agent=agent,
    app_name="agents"  # Must match directory structure and session creation
)

# Create session with matching app_name
session = await runner.session_service.create_session(
    user_id="user_123",
    app_name="agents"  # MUST match runner's app_name
)
```

### CRITICAL: Common Misconception - Session Sharing in Multi-Agent Systems

**WRONG ASSUMPTION:**
Multiple agents should share the same session_id to share conversation context in a multi-agent debate system.

**WHY THIS IS WRONG:**
- ADK Session = **Agent's personal conversation history** with a specific user/thread
- Session stores what **that agent** has said and remembered, NOT shared context
- Agents already see full Slack thread context through message history
- Forcing session sharing creates architectural conflicts and "Session not found" errors

**CORRECT UNDERSTANDING:**
- Each agent maintains **its OWN independent session** per thread/conversation
- Context sharing happens through **Slack thread messages**, not through shared sessions
- Agent A's session stores only Agent A's conversation memory
- Agent B's session stores only Agent B's conversation memory
- Both agents read the same Slack thread to understand full context

**Example of Correct Architecture:**
```python
# WRONG: Trying to share sessions
all_agents_use_same_session_id = "shared_session_123"  # ❌ Don't do this

# CORRECT: Independent sessions per agent
jamal_runner = InMemoryRunner(agent=jamal_agent, app_name="debate_jamal")
ryan_runner = InMemoryRunner(agent=ryan_agent, app_name="debate_ryan")
james_runner = InMemoryRunner(agent=james_agent, app_name="debate_james")

# Each agent gets its own session for the same thread
jamal_runner.run_async(user_id="thread_12345", ...)  # Creates jamal's session
ryan_runner.run_async(user_id="thread_12345", ...)   # Creates ryan's session
james_runner.run_async(user_id="thread_12345", ...)  # Creates james's session
```

### Hybrid Architecture Pattern for Multi-Agent Debates

When building multi-agent debate systems in Slack, use this hybrid approach:

**Pattern: Orchestrator + Visual Mentions**

1. **Orchestrator Controls Flow:**
   - Central DebateOrchestrator manages agent call sequence programmatically
   - Determines which agent speaks next based on debate rules
   - No reliance on Slack mention events for flow control

2. **Visual Mentions for Observability:**
   - Orchestrator injects @mentions into agent messages before posting
   - Users can see natural conversation flow in Slack
   - Mentions are cosmetic only, not functional triggers

3. **Active Debate Tracking:**
   - Maintain registry of active debate threads: `active_debates = {thread_ts: True}`
   - SlackHandler filters out mention events for active debates
   - Prevents Slack events from interfering with Orchestrator control

4. **Independent Session Management:**
   - Each agent has unique `app_name` (e.g., "debate_jamal", "debate_ryan", "debate_james")
   - ADK automatically manages sessions per agent per thread
   - No manual session_id passing or FileSessionRegistry needed

**Example Implementation:**
```python
class DebateOrchestrator:
    active_debates = {}  # Class variable: {thread_ts: True}

    def start_debate(self, thread_ts, initial_message):
        self.active_debates[thread_ts] = True  # Mark as active

        try:
            while not terminated:
                # Orchestrator calls agents directly
                jamal_response = jamal_agent.generate_response(...)
                # Inject mention for visual effect
                self._post_slack_message(jamal_response + " @AgentRyan", thread_ts)

                ryan_response = ryan_agent.generate_response(...)
                self._post_slack_message(ryan_response + " @AgentJames", thread_ts)

                # Check termination
                james_response = james_agent.generate_response(...)
                terminated = self._check_termination(james_response)
        finally:
            del self.active_debates[thread_ts]  # Cleanup

# In SlackHandler
def handle_mention(self, thread_ts):
    if thread_ts in DebateOrchestrator.active_debates:
        return  # Ignore mention events during active debate

    # Start new debate
    orchestrator.start_debate(thread_ts, message)
```

**Common Mistakes to Avoid:**
1. Creating agents with `Agent()` directly in code without file structure
2. Using different `app_name` values in runner vs. session creation
3. Forgetting to set `GOOGLE_API_KEY` environment variable before importing agent modules
4. Not using `from . import agent` in `__init__.py` files
5. **Trying to share session_id across multiple agents** ❌
6. **Relying on Slack mention events for debate flow control** ❌