"""Debate Orchestrator for managing multi-agent debate flow."""

import threading
from typing import Dict, Optional
from slack_sdk import WebClient
from src.llm.adk_agent import ADKAgent
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DebateOrchestrator:
    """
    Orchestrates multi-agent debates with hybrid architecture.

    Controls debate flow programmatically while injecting visual mentions
    for Slack observability. Maintains active debate registry to prevent
    Slack mention events from interfering with orchestrated flow.
    """

    # Class variable: tracks active debates to prevent event interference
    active_debates: Dict[str, bool] = {}
    _lock = threading.Lock()

    def __init__(
        self,
        jamal_client: WebClient,
        ryan_client: WebClient,
        james_client: WebClient,
        jamal_agent: ADKAgent,
        ryan_agent: ADKAgent,
        james_agent: ADKAgent,
        max_rounds: int = 10
    ) -> None:
        """
        Initialize DebateOrchestrator.

        Args:
            jamal_client: Slack WebClient for AgentJamal
            ryan_client: Slack WebClient for AgentRyan
            james_client: Slack WebClient for AgentJames
            jamal_agent: Proposer agent (AgentJamal)
            ryan_agent: Opposer agent (AgentRyan)
            james_agent: Mediator agent (AgentJames)
            max_rounds: Maximum debate rounds before forced termination
        """
        # Map each agent to their corresponding Slack client
        self.clients = {
            "jamal": jamal_client,
            "ryan": ryan_client,
            "james": james_client
        }

        self.jamal = jamal_agent
        self.ryan = ryan_agent
        self.james = james_agent
        self.max_rounds = max_rounds

        logger.info("DebateOrchestrator initialized with 3 separate bot clients")

    def start_debate(
        self,
        channel: str,
        thread_ts: str,
        initial_message: str,
        user_id: str
    ) -> None:
        """
        Start orchestrated debate in background thread.

        Flow: Jamal → James (summary) → Ryan → James (check/continue)
        James decides termination based on consensus or repetition.

        Args:
            channel: Slack channel ID
            thread_ts: Thread timestamp
            initial_message: User's initial message to debate
            user_id: User ID who triggered debate
        """
        # Mark debate as active
        with self._lock:
            if thread_ts in self.active_debates:
                logger.warning(f"Debate already active for thread: {thread_ts}")
                return
            self.active_debates[thread_ts] = True

        logger.info(f"Starting debate in thread: {thread_ts}")

        # Run debate in background thread to avoid blocking
        debate_thread = threading.Thread(
            target=self._run_debate,
            args=(channel, thread_ts, initial_message, user_id),
            daemon=True
        )
        debate_thread.start()

    def _run_debate(
        self,
        channel: str,
        thread_ts: str,
        initial_message: str,
        user_id: str
    ) -> None:
        """
        Execute debate loop until termination.

        Args:
            channel: Slack channel ID
            thread_ts: Thread timestamp
            initial_message: User's initial message
            user_id: User ID
        """
        try:
            round_count = 0
            terminated = False

            # Build context from initial message
            context = f"주제: {initial_message}"

            while not terminated and round_count < self.max_rounds:
                round_count += 1
                logger.info(f"[Round {round_count}] Starting debate round in thread: {thread_ts}")

                # 1. AgentJamal proposes
                jamal_response = self._agent_speak(
                    agent=self.jamal,
                    context=context,
                    thread_ts=thread_ts
                )

                self._post_with_mention(
                    channel=channel,
                    thread_ts=thread_ts,
                    text=jamal_response,
                    next_agent="@AgentJames",
                    speaker="jamal"
                )

                context += f"\n\nAgentJamal: {jamal_response}"

                # 2. AgentJames summarizes
                james_summary_prompt = f"{context}\n\n위 내용을 요약하고 AgentRyan에게 전달해주세요."
                james_summary = self._agent_speak(
                    agent=self.james,
                    context=james_summary_prompt,
                    thread_ts=thread_ts
                )

                self._post_with_mention(
                    channel=channel,
                    thread_ts=thread_ts,
                    text=james_summary,
                    next_agent="@AgentRyan",
                    speaker="james"
                )

                context += f"\n\nAgentJames: {james_summary}"

                # 3. AgentRyan opposes
                ryan_response = self._agent_speak(
                    agent=self.ryan,
                    context=context,
                    thread_ts=thread_ts
                )

                self._post_with_mention(
                    channel=channel,
                    thread_ts=thread_ts,
                    text=ryan_response,
                    next_agent="@AgentJames",
                    speaker="ryan"
                )

                context += f"\n\nAgentRyan: {ryan_response}"

                # 4. AgentJames checks termination
                james_check_prompt = f"{context}\n\n합의가 이루어졌거나 논의가 반복되면 '토론을 종료합니다'로 시작하는 최종 결론을 작성하세요. 그렇지 않으면 AgentJamal에게 추가 의견을 요청하세요."
                james_check = self._agent_speak(
                    agent=self.james,
                    context=james_check_prompt,
                    thread_ts=thread_ts
                )

                # Check for termination
                if self._check_termination(james_check):
                    terminated = True
                    next_agent = None
                else:
                    next_agent = "@AgentJamal"

                self._post_with_mention(
                    channel=channel,
                    thread_ts=thread_ts,
                    text=james_check,
                    next_agent=next_agent,
                    speaker="james"
                )

                context += f"\n\nAgentJames: {james_check}"

            if round_count >= self.max_rounds:
                logger.warning(f"Debate reached max rounds ({self.max_rounds}) in thread: {thread_ts}")
                self._post_message(
                    channel=channel,
                    thread_ts=thread_ts,
                    text=f"⚠️ 토론이 최대 라운드({self.max_rounds})에 도달하여 종료되었습니다.",
                    speaker="james"
                )

            logger.info(f"Debate completed in thread: {thread_ts} after {round_count} rounds")

        except Exception as e:
            logger.error(f"Error in debate loop for thread {thread_ts}: {e}", exc_info=True)
            self._post_message(
                channel=channel,
                thread_ts=thread_ts,
                text=f"❌ 토론 중 오류가 발생했습니다: {str(e)}",
                speaker="james"
            )

        finally:
            # Remove from active debates
            with self._lock:
                if thread_ts in self.active_debates:
                    del self.active_debates[thread_ts]
            logger.info(f"Debate cleanup completed for thread: {thread_ts}")

    def _agent_speak(
        self,
        agent: ADKAgent,
        context: str,
        thread_ts: str
    ) -> str:
        """
        Get response from agent.

        Args:
            agent: ADKAgent instance
            context: Current debate context
            thread_ts: Thread timestamp

        Returns:
            Agent's response text
        """
        try:
            response = agent.generate_response(
                text=context,
                thread_ts=thread_ts
            )
            return response
        except Exception as e:
            logger.error(f"Error getting response from {agent.agent_name}: {e}", exc_info=True)
            return f"[Error: {agent.agent_name} failed to respond]"

    def _check_termination(self, james_response: str) -> bool:
        """
        Check if debate should terminate based on James's response.

        Args:
            james_response: AgentJames's response text

        Returns:
            True if debate should terminate
        """
        termination_phrases = [
            "토론을 종료합니다",
            "토론을 마치겠습니다",
            "논의를 종료합니다"
        ]

        response_lower = james_response.lower()
        for phrase in termination_phrases:
            if phrase.lower() in response_lower:
                logger.info(f"Termination detected: '{phrase}' found in response")
                return True

        return False

    def _post_with_mention(
        self,
        channel: str,
        thread_ts: str,
        text: str,
        next_agent: Optional[str] = None,
        speaker: str = "jamal"
    ) -> None:
        """
        Post message to Slack with optional mention injection.

        Mentions are for visual effect only, not functional triggers.

        Args:
            channel: Slack channel ID
            thread_ts: Thread timestamp
            text: Message text
            next_agent: Agent to mention (e.g., "@AgentRyan") or None
            speaker: Which agent is speaking ("jamal", "ryan", or "james")
        """
        if next_agent:
            message = f"{text}\n\n{next_agent}"
        else:
            message = text

        self._post_message(channel, thread_ts, message, speaker)

    def _post_message(
        self,
        channel: str,
        thread_ts: str,
        text: str,
        speaker: str = "jamal"
    ) -> None:
        """
        Post message to Slack thread using the appropriate bot client.

        Args:
            channel: Slack channel ID
            thread_ts: Thread timestamp
            text: Message text
            speaker: Which agent is speaking ("jamal", "ryan", or "james")
        """
        try:
            # Select the appropriate Slack client based on speaker
            client = self.clients.get(speaker, self.clients["jamal"])
            client.chat_postMessage(
                channel=channel,
                thread_ts=thread_ts,
                text=text
            )
            logger.debug(f"Message posted as {speaker}: {text[:50]}...")
        except Exception as e:
            logger.error(f"Failed to post message to Slack as {speaker}: {e}", exc_info=True)

    @classmethod
    def is_debate_active(cls, thread_ts: str) -> bool:
        """
        Check if debate is active for given thread.

        Args:
            thread_ts: Thread timestamp

        Returns:
            True if debate is active
        """
        with cls._lock:
            return thread_ts in cls.active_debates
