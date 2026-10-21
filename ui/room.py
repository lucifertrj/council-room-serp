import os

import streamlit as st

from agent import build_expert_agent, build_prompt
from constants import ROOMS, Expert, Room
from utils import stream_agent

_ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
_PLAYER = os.path.join(_ASSETS, "player.png")
_USER_AVATAR = _PLAYER if os.path.exists(_PLAYER) else ":material/person:"


def _avatar(value: str) -> str:
    if isinstance(value, str) and os.path.exists(value):
        return value
    if isinstance(value, str) and value and ord(value[0]) >= 0x1F000:
        return value
    return ":material/smart_toy:"


def _header(room: Room) -> None:
    st.markdown(f"<style>:root {{ --room-accent: {room.accent}; }}</style>", unsafe_allow_html=True)
    with st.container(border=True, key=f"room_hdr_box_{room.key}"):
        top_left, top_right = st.columns([4.8, 1.2], vertical_alignment="center")
        with top_left:
            crew_html = (
                f"<div class='cc-pill council-pill'>"
                f"<span class='cc-pill-name'>{room.icon} Room Council</span>"
                f"<span class='cc-pill-role'>Both Analysts Collaborate</span>"
                f"</div>"
                + "".join(
                    f"<div class='cc-pill'>"
                    f"<span class='cc-pill-name'>{e.name}</span>"
                    f"<span class='cc-pill-role'>{e.role} · {e.engine}</span>"
                    f"</div>"
                    for e in room.experts
                )
            )
            st.markdown(
                f"<div class='cc-header' style='--accent:{room.accent}'>"
                f"<div class='cc-header-main'>"
                f"<div class='cc-header-top'>"
                f"<span class='cc-icon-box'>{room.icon}</span>"
                f"<h2>{room.name}</h2>"
                f"<span class='cc-engine-tag'>{room.caption}</span>"
                f"</div>"
                f"<p class='cc-room-sub'>{room.tagline}</p>"
                f"</div>"
                f"<div class='cc-crew'>{crew_html}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with top_right:
            if st.button("◄ FLOORPLAN", width="stretch"):
                st.session_state.room = None
                st.rerun()


def _run_expert(expert: Expert, query: str, prior: list[tuple[str, str]]) -> dict:
    agent = build_expert_agent(expert)
    log = st.session_state.setdefault("search_log", [])
    before = len(log)
    with st.chat_message(expert.name, avatar=_avatar(expert.avatar)):
        st.markdown(f"{expert.avatar} **{expert.name}** · _{expert.role}_ · `serpapi:{expert.engine}`")
        status = st.status(f"Querying SerpApi ({expert.engine})…", expanded=False)
        answer = st.empty()
        text = ""
        for chunk in stream_agent(agent, build_prompt(query, prior)):
            text += chunk
            answer.markdown(text)
        # The SerpApi tool logs each call at the front of search_log; the entries
        # added during this run are everything before our snapshot index.
        added = st.session_state.search_log[:len(st.session_state.search_log) - before]
        with status:
            if added:
                for entry in reversed(added):  # chronological order
                    label = f"**`{entry['engine']}`** · `{entry['query']}`"
                    if entry.get("extra"):
                        label += f"  ·  `{entry['extra']}`"
                    st.markdown(label)
                    st.code(entry["output"][:1500] or "—")
            else:
                st.caption("No SerpApi calls recorded for this turn.")
        n = len(added)
        status.update(
            label=f"✓ {n} SerpApi search{'es' if n != 1 else ''} · {expert.engine}",
            state="complete", expanded=False,
        )
    return {"name": expert.name, "role": expert.role,
            "avatar": expert.avatar, "content": text}


def _render_turn(turn: dict) -> None:
    if turn["role"] == "user":
        with st.chat_message("user", avatar=_USER_AVATAR):
            st.markdown(turn["content"])
        return
    for e in turn["experts"]:
        with st.chat_message(e["name"], avatar=_avatar(e.get("avatar"))):
            st.markdown(f"{e.get('avatar', '')} **{e['name']}** · _{e['role']}_")
            st.markdown(e["content"])


def _generate(experts: list[Expert], query: str) -> dict:
    out, prior = [], []
    for expert in experts:
        e = _run_expert(expert, query, prior)
        out.append(e)
        prior.append((e["name"], e["content"]))
    return {"role": "assistant", "experts": out}


def render(room_key: str) -> None:
    room = ROOMS[room_key]
    _header(room)

    council_opt = f"{room.icon} Full Council (Both Analysts)"
    option_map = {council_opt: "🏛️ Council"}
    for e in room.experts:
        opt_label = f"{e.avatar} {e.name} · {e.role} [{e.engine}]"
        option_map[opt_label] = e.name

    options = list(option_map.keys())

    st.markdown(
        f"<div class='cc-comm-box'>"
        f"<div class='cc-comm-info'>"
        f"<span class='cc-comm-icon'>{room.icon}</span>"
        f"<div>"
        f"<div class='cc-comm-title'>COMMUNICATION CHANNEL</div>"
        f"<div class='cc-comm-desc'>Select <b>{room.icon} Full Council</b> so {' & '.join(e.name for e in room.experts)} collaborate on your query, or pick a single specialist below for a 1-on-1 deep dive.</div>"
        f"</div>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    selected_opt = st.segmented_control(
        "Communication Target",
        options,
        default=council_opt,
        key=f"chan_{room_key}",
        label_visibility="collapsed",
    ) or council_opt
    channel = option_map[selected_opt]

    store = st.session_state.messages.setdefault(room_key, {})
    thread = store.setdefault(channel, [])

    for turn in thread:
        _render_turn(turn)

    query = None
    if not thread:
        st.markdown("<div class='cc-try-label'>// TEST THIS ROOM WITH A LIVE QUERY</div>", unsafe_allow_html=True)
        cols = st.columns(len(room.samples), gap="small")
        for col, s in zip(cols, room.samples):
            if col.button(s, key=f"s_{room_key}_{channel}_{s}", width="stretch"):
                query = s

    prompt_target = f"{room.name} Council" if channel == "🏛️ Council" else channel
    typed = st.chat_input(f"Ask {prompt_target}…", key=f"in_{room_key}_{channel}")
    query = query or typed
    if not query:
        return

    experts = (room.experts if channel == "🏛️ Council"
               else [e for e in room.experts if e.name == channel])

    thread.append({"role": "user", "content": query})
    with st.chat_message("user", avatar=_USER_AVATAR):
        st.markdown(query)
    thread.append(_generate(experts, query))
    st.rerun()
