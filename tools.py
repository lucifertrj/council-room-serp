import json
import uuid

import serpapi
import streamlit as st

import config

_RESULT_KEYS = {
    "google": ["organic_results"],
    "google_news": ["news_results"],
    "google_shopping": ["shopping_results"],
    "youtube": ["video_results", "movie_results"],
    "google_hotels": ["properties"],
    "google_flights": ["best_flights", "other_flights"],
    "google_finance": ["markets", "news_results"],
    "google_trends": ["interest_over_time", "related_queries"],
}


def _compact(engine: str, data: dict) -> list[dict]:
    out: list[dict] = []
    for special in ("answer_box", "knowledge_graph"):
        block = data.get(special)
        if isinstance(block, dict):
            out.append({
                "title": block.get("title") or special.replace("_", " ").title(),
                "link": block.get("link", ""),
                "snippet": block.get("answer") or block.get("snippet")
                or block.get("description", ""),
            })
    for key in _RESULT_KEYS.get(engine, ["organic_results"]):
        items = data.get(key)
        if not isinstance(items, list):
            continue
        for item in items[:6]:
            if not isinstance(item, dict):
                continue
            rate = item.get("rate_per_night")
            price = rate.get("lowest", "") if isinstance(rate, dict) else ""
            out.append({
                "title": item.get("title") or item.get("name")
                or item.get("stock") or item.get("query", "Result"),
                "link": item.get("link") or item.get("product_link")
                or item.get("serpapi_link", ""),
                "snippet": item.get("snippet") or item.get("description")
                or item.get("price") or price,
            })
        if out:
            break
    return out[:8]


def _log(engine: str, query: str, extra: str, output: str) -> None:
    entry = {
        "id": uuid.uuid4().hex[:8],
        "engine": engine,
        "query": query or "(none)",
        "extra": extra,
        "output": output,
    }
    st.session_state.setdefault("search_log", []).insert(0, entry)


def make_serp_tool(engine: str):
    def serp_search(query: str, extra_params: str = "") -> str:
        """Search the web via SerpApi and return compact, citable results.

        Args:
            query: The search query (maps to the engine's `q` parameter).
            extra_params: Optional JSON object string of extra SerpApi params for
                this engine, e.g. '{"departure_id": "JFK", "arrival_id": "LHR",
                "outbound_date": "2025-11-01"}'.
        """
        params = {"engine": engine, "api_key": config.SERPAPI_API_KEY}
        if query:
            params["q"] = query
        if extra_params:
            try:
                params.update(json.loads(extra_params))
            except (json.JSONDecodeError, TypeError):
                pass

        try:
            client = serpapi.Client(api_key=config.SERPAPI_API_KEY)
            results = client.search(params)
            data = results.as_dict() if hasattr(results, "as_dict") else dict(results)
        except Exception as exc:
            out = f"SerpApi error: {exc}"
            _log(engine, query, extra_params, out)
            return out

        if data.get("error"):
            out = f"No results: {data['error']}"
            _log(engine, query, extra_params, out)
            return out

        compact = _compact(engine, data)
        if not compact:
            out = "No usable results."
            _log(engine, query, extra_params, out)
            return out

        out = "\n".join(
            f"- {r['title']} | {r['snippet']} | {r['link']}".strip(" |")
            for r in compact
        )
        _log(engine, query, extra_params, out)
        return out

    serp_search.__doc__ = serp_search.__doc__.replace("the engine's", f"the {engine}")
    return serp_search
