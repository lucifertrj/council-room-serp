import streamlit as st

import config
from constants import ROOMS
from ui import landing, room
from ui.sidebar import render_search_log
from ui.styles import inject


def main() -> None:
    st.set_page_config(page_title=config.APP_TITLE, page_icon="▣", layout="wide",
                       initial_sidebar_state="expanded")
    inject()
    st.session_state.setdefault("room", None)
    st.session_state.setdefault("messages", {})
    st.session_state.setdefault("search_log", [])

    render_search_log()

    active = st.session_state.room
    if active and active in ROOMS:
        room.render(active)
    else:
        landing.render()


if __name__ == "__main__":
    main()
