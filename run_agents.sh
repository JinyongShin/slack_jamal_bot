#!/bin/bash

echo "========================================="
echo "Multi-Agent Debate System"
echo "========================================="
echo "Agents:"
echo "  - AgentJamal (Proposer)"
echo "  - AgentRyan (Opposer)"
echo "  - AgentJames (Mediator)"
echo "========================================="
echo ""

# Load and start AgentJamal
echo "🚀 Starting AgentJamal (Proposer)..."
set -a
source .env.jamal
set +a
uv run python -m src.main &
JAMAL_PID=$!
sleep 2

# Load and start AgentRyan
echo "🚀 Starting AgentRyan (Opposer)..."
set -a
source .env.ryan
set +a
uv run python -m src.main &
RYAN_PID=$!
sleep 2

# Load and start AgentJames
echo "🚀 Starting AgentJames (Mediator)..."
set -a
source .env.james
set +a
uv run python -m src.main &
JAMES_PID=$!
sleep 2

echo ""
echo "========================================="
echo "✅ All agents started successfully!"
echo "========================================="
echo "Process IDs:"
echo "  AgentJamal: $JAMAL_PID"
echo "  AgentRyan: $RYAN_PID"
echo "  AgentJames: $JAMES_PID"
echo "========================================="
echo ""
echo "Press Ctrl+C to stop all agents"
echo ""

# Trap to kill all on exit
trap "echo ''; echo 'Stopping all agents...'; kill $JAMAL_PID $RYAN_PID $JAMES_PID 2>/dev/null; echo 'All agents stopped.'; exit 0" EXIT INT TERM

# Wait for any process to exit
wait
