"""
util.py — Distillation prompt builders (no model calls).

These functions build prompts that the orchestrator can send to any LLM.
They never call an LLM directly — they only return strings.
"""

from __future__ import annotations

from .models import Message


def build_distill_facts_prompt(messages: list[Message]) -> str:
    """Build a prompt asking an LLM to extract key facts from messages.

    Args:
        messages: List of Message objects to distill.

    Returns:
        A prompt string. The orchestrator sends this to the model.
    """
    conversation = _format_messages(messages)

    return f"""Extract the key facts from the following conversation.

Rules:
- Each fact should be a single, self-contained statement.
- Include decisions made, requirements stated, preferences expressed, and technical details.
- Omit greetings, filler, and meta-conversation.
- Output one fact per line, prefixed with "- ".
- Assign importance 1-10 (10 = critical decision, 1 = minor detail).
- Format: "- [importance] fact text"

Conversation:
{conversation}

Facts:"""


def build_rolling_summary_prompt(
    messages: list[Message],
    existing_summary: str | None = None,
) -> str:
    """Build a prompt asking an LLM to produce/update a rolling summary.

    Args:
        messages: New messages to incorporate.
        existing_summary: Previous summary to update (if any).

    Returns:
        A prompt string. The orchestrator sends this to the model.
    """
    conversation = _format_messages(messages)

    if existing_summary:
        return f"""Update the following rolling summary with new conversation content.

Existing summary:
{existing_summary}

New conversation:
{conversation}

Rules:
- Preserve all important information from the existing summary.
- Integrate new information concisely.
- Keep the summary under 500 words.
- Focus on: decisions, current state, open questions, next steps.
- Use present tense for current state, past tense for completed items.

Updated summary:"""

    return f"""Write a concise summary of the following conversation.

Conversation:
{conversation}

Rules:
- Keep the summary under 500 words.
- Focus on: decisions, current state, open questions, next steps.
- Use present tense for current state, past tense for completed items.

Summary:"""


def _format_messages(messages: list[Message]) -> str:
    """Format a list of messages into a readable conversation string."""
    lines = []
    for msg in messages:
        role = msg.role.capitalize()
        lines.append(f"[{role}]: {msg.content}")
    return "\n".join(lines)
