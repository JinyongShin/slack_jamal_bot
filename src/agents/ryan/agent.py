"""AgentRyan (Opposer) definition."""

import os
from google.adk import Agent
from google.adk.tools import google_search
from src.llm.agent_roles import AGENT_INSTRUCTIONS, AGENT_NAMES

# Set environment for Google AI (not Vertex AI)
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"

# Define role
ROLE = "opposer"
AGENT_NAME = AGENT_NAMES[ROLE]

# Create root agent for ADK
root_agent = Agent(
    name=AGENT_NAME,
    model="gemini-2.0-flash",
    instruction=AGENT_INSTRUCTIONS[ROLE],
    description=f"{AGENT_NAME} - {ROLE.capitalize()} agent for multi-agent debate",
    tools=[google_search]
)
