import streamlit as st


def render_search_log() -> None:
    with st.sidebar:
        st.markdown("### 🔎 Search Log")
        log = st.session_state.get("search_log", [])
        if not log:
            st.caption("SerpApi calls will stream in here as the experts search.")
            return

        top = st.columns([3, 2])
        top[0].caption(f"{len(log)} call(s)")
        if top[1].button("Clear all", width="stretch"):
            st.session_state.search_log = []
            st.rerun()

        for entry in log:
            st.markdown(
                f"<div class='cc-log'><span class='eng'>{entry['engine']}</span>"
                f"<div class='q'>🔎 {entry['query']}</div></div>",
                unsafe_allow_html=True,
            )
            with st.expander("input / output"):
                if entry.get("extra"):
                    st.caption("params")
                    st.code(entry["extra"], language="json")
                st.caption("output")
                st.text(entry["output"][:1800])
            if st.button("🗑 delete", key=f"del_{entry['id']}",
                         width="stretch"):
                st.session_state.search_log = [
                    e for e in log if e["id"] != entry["id"]
                ]
                st.rerun()

