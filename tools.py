import json
import uuid
from datetime import date, timedelta

import serpapi
import streamlit as st

import config

# Engines whose primary query parameter is not `q`.
_QUERY_PARAM = {"youtube": "search_query"}


def _num(value):
    """Best-effort number from a str like 'USD221.35' or '$1,299'."""
    if isinstance(value, (int, float)):
        return value
    if not isinstance(value, str):
        return None
    cleaned = "".join(c for c in value if c.isdigit() or c in ".-")
    try:
        return float(cleaned) if cleaned not in ("", ".", "-") else None
    except ValueError:
        return None


def _defaults(engine: str, params: dict) -> dict:
    """Fill engine-specific required params so a call never hard-fails on an
    omission the model forgot (dates are relative to today)."""
    if engine == "google_flights":
        # One-way unless the caller supplied a return date (round trip needs one).
        if "type" not in params and not any(
            k in params for k in ("return_date", "inbound_date")
        ):
            params["type"] = "2"
    elif engine == "google_hotels":
        if "check_in_date" not in params:
            params["check_in_date"] = (date.today() + timedelta(days=7)).isoformat()
        if "check_out_date" not in params:
            params["check_out_date"] = (date.today() + timedelta(days=9)).isoformat()
    return params


def _row(title, snippet="", link=""):
    return {"title": str(title or "").strip(),
            "snippet": str(snippet or "").strip(),
            "link": str(link or "").strip()}


def _web(data: dict, keys: list[str]) -> list[dict]:
    """Generic list-of-results engines: google, plus a fallback."""
    out = []
    for special in ("answer_box", "knowledge_graph"):
        block = data.get(special)
        if isinstance(block, dict):
            text = (block.get("answer") or block.get("snippet")
                    or block.get("description") or "")
            title = block.get("title") or special.replace("_", " ").title()
            if text:
                out.append(_row(title, text, block.get("link", "")))
    for key in keys:
        items = data.get(key)
        if isinstance(items, list):
            for it in items[:6]:
                if isinstance(it, dict):
                    out.append(_row(it.get("title"), it.get("snippet")
                                    or it.get("description", ""), it.get("link", "")))
            if items:
                break
    return out


def _news(data: dict) -> list[dict]:
    out = []
    for it in data.get("news_results", [])[:6]:
        if not isinstance(it, dict):
            continue
        src = it.get("source")
        src = src.get("name", "") if isinstance(src, dict) else (src or "")
        meta = " · ".join(p for p in (src, it.get("date", "")) if p)
        out.append(_row(it.get("title"), meta, it.get("link", "")))
    return out


def _youtube(data: dict) -> list[dict]:
    out = []
    for it in data.get("video_results", [])[:6]:
        if not isinstance(it, dict):
            continue
        ch = it.get("channel")
        ch = ch.get("name", "") if isinstance(ch, dict) else (ch or "")
        meta = " · ".join(p for p in (
            ch, it.get("views") and f"{it['views']:,} views"
            if isinstance(it.get("views"), int) else it.get("views"),
            it.get("published_date", ""), it.get("length", "")) if p)
        out.append(_row(it.get("title"), meta, it.get("link", "")))
    return out


def _shopping(data: dict) -> list[dict]:
    out = []
    for it in data.get("shopping_results", [])[:6]:
        if not isinstance(it, dict):
            continue
        meta = " · ".join(str(p) for p in (
            it.get("price", ""), it.get("source", ""),
            it.get("rating") and f"{it['rating']}★ ({it.get('reviews', '?')})") if p)
        out.append(_row(it.get("title"), meta,
                        it.get("product_link") or it.get("link", "")))
    return out


def _hotels(data: dict) -> list[dict]:
    out = []
    for it in data.get("properties", [])[:6]:
        if not isinstance(it, dict):
            continue
        rate = it.get("rate_per_night")
        price = rate.get("lowest", "") if isinstance(rate, dict) else ""
        meta = " · ".join(str(p) for p in (
            price, it.get("overall_rating") and f"{it['overall_rating']}★",
            it.get("type", ""), it.get("description", "")) if p)
        out.append(_row(it.get("name"), meta, it.get("link", "")))
    return out


def _flights(data: dict) -> list[dict]:
    out = []
    for key in ("best_flights", "other_flights"):
        for it in data.get(key, [])[:5]:
            if not isinstance(it, dict):
                continue
            legs = it.get("flights", []) or []
            airlines = " / ".join(dict.fromkeys(
                l.get("airline", "") for l in legs if l.get("airline")))
            stops = len(legs) - 1
            dep = legs[0].get("departure_airport", {}) if legs else {}
            arr = legs[-1].get("arrival_airport", {}) if legs else {}
            mins = it.get("total_duration")
            dur = f"{mins // 60}h {mins % 60}m" if isinstance(mins, int) else ""
            route = f"{dep.get('id', '')}→{arr.get('id', '')}".strip("→")
            meta = " · ".join(str(p) for p in (
                it.get("price") and f"${it['price']}", dur,
                "nonstop" if stops == 0 else f"{stops} stop(s)", route,
                dep.get("time", "")) if p)
            out.append(_row(airlines or "Flight", meta, ""))
        if out:
            break
    return out


def _finance(data: dict) -> list[dict]:
    out = []
    s = data.get("summary")
    if isinstance(s, dict):
        mv = s.get("price_movement") or {}
        move = ""
        if isinstance(mv, dict) and mv.get("percentage") is not None:
            arrow = "▲" if mv.get("movement") == "Up" else "▼"
            move = f" {arrow} {abs(mv['percentage']):.2f}%"
        title = f"{s.get('title', '')} ({s.get('stock', '')}:{s.get('exchange', '')})"
        snippet = f"{s.get('price', '')}{move} · as of {s.get('date', '')}"
        out.append(_row(title, snippet))
    kg = data.get("knowledge_graph")
    if isinstance(kg, dict):
        stats = (kg.get("key_stats") or {}).get("stats")
        if isinstance(stats, list) and stats:
            pairs = ", ".join(f"{x.get('label')}: {x.get('value')}"
                              for x in stats[:6] if isinstance(x, dict))
            if pairs:
                out.append(_row("Key stats", pairs))
    for it in data.get("news_results", [])[:4]:
        if isinstance(it, dict):
            headline = it.get("title") or it.get("snippet", "")
            src = it.get("source")
            src = src.get("name", "") if isinstance(src, dict) else (src or "")
            meta = " · ".join(p for p in (src, it.get("date", "")) if p)
            out.append(_row(headline, meta, it.get("link", "")))
    return out


def _trends(data: dict) -> list[dict]:
    iot = data.get("interest_over_time")
    if not isinstance(iot, dict):
        return []
    timeline = iot.get("timeline_data", [])
    series: dict[str, list[int]] = {}
    for point in timeline:
        for v in point.get("values", []):
            if not isinstance(v, dict):
                continue
            q = v.get("query", "query")
            ev = v.get("extracted_value")
            if isinstance(ev, (int, float)):
                series.setdefault(q, []).append(ev)
    out = []
    leader = None
    for q, vals in series.items():
        if not vals:
            continue
        first, last, peak = vals[0], vals[-1], max(vals)
        recent = vals[-3:] if len(vals) >= 3 else vals
        slope = recent[-1] - recent[0]
        traj = "rising" if slope > 3 else "falling" if slope < -3 else "flat"
        avg = sum(vals) / len(vals)
        if leader is None or avg > leader[1]:
            leader = (q, avg)
        out.append(_row(
            q, f"now {last}/100 (peak {peak}, start {first}) · trajectory: {traj}"))
    if len(series) > 1 and leader:
        out.insert(0, _row("Comparison", f"{leader[0]} leads on average interest"))
    rq = data.get("related_queries")
    if isinstance(rq, dict):
        rising = rq.get("rising") or []
        names = ", ".join(r.get("query", "") for r in rising[:4]
                          if isinstance(r, dict) and r.get("query"))
        if names:
            out.append(_row("Rising related queries", names))
    # Regional breakdown when the caller requested data_type=GEO_MAP.
    for key in ("compared_breakdown_by_region", "interest_by_region"):
        region = data.get(key)
        if isinstance(region, list) and region:
            tops = []
            for r in region[:5]:
                if not isinstance(r, dict):
                    continue
                val = r.get("value")
                if isinstance(val, list):
                    val = ", ".join(str(v.get("extracted_value", v.get("value", "")))
                                    for v in val if isinstance(v, dict))
                tops.append(f"{r.get('location', '')}: {val}")
            if tops:
                out.append(_row("Top regions", " · ".join(tops)))
            break
    return out


_EXTRACTORS = {
    "google": lambda d: _web(d, ["organic_results"]),
    "google_news": _news,
    "youtube": _youtube,
    "google_shopping": _shopping,
    "google_hotels": _hotels,
    "google_flights": _flights,
    "google_finance": _finance,
    "google_trends": _trends,
}


def _compact(engine: str, data: dict) -> list[dict]:
    extractor = _EXTRACTORS.get(engine, lambda d: _web(d, ["organic_results"]))
    rows = [r for r in extractor(data) if r["title"] or r["snippet"]]
    return rows[:8]


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
            query: The search query (e.g. a topic, ticker like NVDA:NASDAQ, or
                for hotels/trends the subject).
            extra_params: Optional JSON object string of extra SerpApi params for
                this engine, e.g. '{"departure_id": "JFK", "arrival_id": "LAX",
                "outbound_date": "2026-11-01"}' for flights, or
                '{"check_in_date": "2026-11-01", "check_out_date": "2026-11-03"}'
                for hotels.
        """
        params = {"engine": engine, "api_key": config.SERPAPI_API_KEY}
        if query:
            params[_QUERY_PARAM.get(engine, "q")] = query
        if extra_params:
            try:
                params.update(json.loads(extra_params))
            except (json.JSONDecodeError, TypeError):
                pass
        params = _defaults(engine, params)

        try:
            client = serpapi.Client(api_key=config.SERPAPI_API_KEY)
            results = client.search(params)
            data = results.as_dict() if hasattr(results, "as_dict") else dict(results)
        except Exception as exc:
            out = f"SerpApi error: {exc}"
            _log(engine, query, extra_params, out)
            return out

        if isinstance(data, dict) and data.get("error"):
            out = f"No results: {data['error']}"
            _log(engine, query, extra_params, out)
            return out

        compact = _compact(engine, data if isinstance(data, dict) else {})
        if not compact:
            out = "No usable results for this query."
            _log(engine, query, extra_params, out)
            return out

        out = "\n".join(
            " | ".join(p for p in (r["title"], r["snippet"], r["link"]) if p)
            for r in compact
        )
        _log(engine, query, extra_params, out)
        return out

    return serp_search
