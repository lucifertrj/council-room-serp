import streamlit as st
from agno.agent import Agent
from agno.models.anthropic import Claude

import config
from constants import BASE_PROMPT, Expert
from tools import make_serp_tool


@st.cache_resource(show_spinner=False)
def _model() -> Claude:
    return Claude(id=config.MODEL_ID, api_key=config.ANTHROPIC_API_KEY)


def build_expert_agent(expert: Expert) -> Agent:
    return Agent(
        name=expert.name,
        model=_model(),
        tools=[make_serp_tool(expert.engine)],
        instructions=[
            BASE_PROMPT,
            f"You are {expert.name}, the room's {expert.role}. {expert.prompt}",
            f"Always use serp_search (engine: {expert.engine}) before answering.",
        ],
        markdown=True,
    )


def build_prompt(query: str, prior: list[tuple[str, str]]) -> str:
    parts = [f"User query: {query}"]
    if prior:
        parts.append("\nYour co-expert already said:")
        parts += [f"\n**{name}**:\n{text}" for name, text in prior]
        parts.append("\nAdd your facet; do not repeat them.")
    return "\n".join(parts)
