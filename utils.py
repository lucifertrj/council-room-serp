from collections.abc import Iterator

from agno.agent import Agent


def stream_agent(agent: Agent, prompt: str) -> Iterator[str]:
    """Yield text deltas from an agno run.

    agno 3.1.7 only surfaces `RunContent` (text) events through the stream;
    tool-call activity is not exposed here, so the room reports tool usage from
    the SerpApi tool's own `search_log` instead (see ui/room.py).
    """
    streamed = False
    try:
        for event in agent.run(prompt, stream=True):
            content = getattr(event, "content", None)
            if isinstance(content, str) and content:
                streamed = True
                yield content
    except Exception as exc:
        yield f"\n\n_Error: {exc}_"
        return

    if not streamed:
        try:
            result = agent.run(prompt)
            text = getattr(result, "content", None)
            yield text if isinstance(text, str) and text else "_No response._"
        except Exception as exc:
            yield f"_Error: {exc}_"
