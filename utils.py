from collections.abc import Iterator

from agno.agent import Agent


def stream_agent(agent: Agent, prompt: str) -> Iterator[tuple[str, str]]:
    yielded_text = False
    try:
        for event in agent.run(prompt, stream=True):
            name = getattr(event, "event", "") or type(event).__name__
            if "Content" in name:
                content = getattr(event, "content", None)
                if isinstance(content, str) and content:
                    yielded_text = True
                    yield ("text", content)
            elif "Tool" in name and "Completed" not in name:
                tool = getattr(event, "tool", None)
                tname = (getattr(tool, "tool_name", None)
                         or getattr(event, "tool_name", None) or "serp_search")
                targs = (getattr(tool, "tool_args", None)
                         or getattr(event, "tool_args", None) or {})
                q = targs.get("query") or targs.get("q") or "" if isinstance(targs, dict) else ""
                yield ("tool", f"🔎 `{tname}` → {q}" if q else f"🔎 `{tname}`")
    except Exception as exc:
        yield ("text", f"\n\n_Error: {exc}_")
        return

    if not yielded_text:
        try:
            result = agent.run(prompt)
            text = getattr(result, "content", None)
            yield ("text", text if isinstance(text, str) else "_No response._")
        except Exception as exc:
            yield ("text", f"_Error: {exc}_")
