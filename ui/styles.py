import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Silkscreen:wght@400;700&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
  --font-pixel: 'Silkscreen', monospace;
  --font-sans: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  --bg-deep: #080e17;
  --bg-panel: #0e1726;
  --bg-card: #111d2f;
  --border-slate: #243b5c;
  --teal: #2dd4bf;
  --cyan: #38bdf8;
  --amber: #fbbf24;
  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
}

/* Hide Streamlit Top Header Bar / Deploy Button & Protect Material Icons */
[data-testid="stHeader"] {
  background: transparent !important;
  border-bottom: none !important;
}

[data-testid="stToolbar"],
[data-testid="stAppDeployButton"],
.stDeployButton,
#MainMenu,
footer {
  display: none !important;
}

span[data-testid="stIconMaterial"],
.material-symbols-rounded,
.material-icons {
  font-family: 'Material Symbols Rounded' !important;
}

/* Base Minimalist Pixelated Slate-Teal Grid Background */
.stApp {
  background-color: var(--bg-deep) !important;
  background-image:
    radial-gradient(950px 480px at 50% 0%, rgba(45, 212, 191, 0.12) 0%, transparent 70%),
    linear-gradient(rgba(36, 59, 92, 0.24) 1px, transparent 1px),
    linear-gradient(90deg, rgba(36, 59, 92, 0.24) 1px, transparent 1px) !important;
  background-size: 100% 100%, 24px 24px, 24px 24px !important;
  color: var(--text-primary) !important;
  font-family: var(--font-sans) !important;
}

.block-container {
  position: relative;
  z-index: 1;
  max-width: 1180px !important;
  padding-top: 2.5rem !important;
  padding-bottom: 4rem !important;
}

/* Uniform Typography */
p, li, label, input, textarea,
.stMarkdown, .stText, .stAlert {
  font-family: var(--font-sans) !important;
  color: var(--text-primary);
}

h1, h2, h3, h4 {
  font-family: var(--font-pixel) !important;
  letter-spacing: 0.5px;
}

.stMarkdown p, .stMarkdown li {
  font-size: 1.08rem !important;
  line-height: 1.65 !important;
  color: #f1f5f9 !important;
}

.stMarkdown strong, .stMarkdown b {
  color: #ffffff !important;
  font-weight: 700 !important;
}

.stMarkdown a {
  color: var(--teal) !important;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.stCaption, [data-testid="stCaptionContainer"] p {
  font-family: var(--font-mono) !important;
  color: var(--text-secondary) !important;
  font-size: 0.92rem !important;
}

/* Minimalist Pixelated Hero Header */
.cc-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin-bottom: 1.35rem;
}

.cc-brand-row {
  display: inline-flex;
  align-items: center;
  gap: 0.85rem;
  margin-bottom: 0.55rem;
}

.cc-logo-mark {
  display: grid;
  grid-template-columns: repeat(2, 11px);
  grid-template-rows: repeat(2, 11px);
  gap: 3px;
  padding: 6px;
  background: #0d1828;
  border: 2px solid var(--teal);
  box-shadow: 3px 3px 0 #04080e;
}

.cc-logo-mark span {
  display: block;
  width: 11px;
  height: 11px;
  background: var(--teal);
}

.cc-logo-mark span:nth-child(2) { background: var(--cyan); }
.cc-logo-mark span:nth-child(3) { background: var(--amber); }

.cc-hero h1 {
  font-family: var(--font-pixel) !important;
  font-size: 2.35rem !important;
  font-weight: 700 !important;
  color: #ffffff !important;
  margin: 0 !important;
  padding: 0 !important;
  text-shadow: 3px 3px 0 #04080e;
}

.cc-tagline {
  font-family: var(--font-sans) !important;
  font-size: 1.12rem !important;
  color: #cbd5e1 !important;
  font-weight: 500;
  max-width: 760px;
  margin: 0.3rem auto 0.45rem auto !important;
  line-height: 1.55 !important;
}

.cc-section-title {
  font-family: var(--font-pixel) !important;
  font-size: 0.9rem;
  color: var(--teal) !important;
  letter-spacing: 1.5px;
  text-align: center;
  margin: 1.9rem 0 1.1rem 0;
}

/* Crisp Minimalist Pixel Cards — Strict Fixed Height so all cards & buttons align horizontally */
.cc-card {
  position: relative;
  border: 2px solid #243b5c;
  border-top: 4px solid var(--accent, var(--teal));
  border-radius: 4px;
  background: #0e1828;
  padding: 1.3rem 1.3rem 1.2rem 1.3rem;
  box-shadow: 5px 5px 0 #050911;
  height: 325px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  margin-bottom: 0.55rem;
  transition: transform 0.12s ease, border-color 0.12s ease, box-shadow 0.12s ease;
}

.cc-card:hover {
  transform: translate(-2px, -2px);
  border-color: var(--accent, var(--teal));
  box-shadow: 7px 7px 0 #050911;
}

.cc-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
}

.cc-icon-box {
  font-family: var(--font-mono) !important;
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--accent, var(--teal)) !important;
  background: rgba(15, 23, 42, 0.95);
  border: 1.5px solid var(--accent, var(--teal));
  width: 38px;
  height: 38px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 2px 2px 0 #050911;
  flex-shrink: 0;
}

.cc-engine-tag {
  font-family: var(--font-mono) !important;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--accent, var(--teal)) !important;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid color-mix(in srgb, var(--accent, var(--teal)) 55%, #243b5c);
  padding: 0.28rem 0.65rem;
  border-radius: 2px;
  white-space: nowrap;
}

.cc-card-body {
  margin: 0.55rem 0 0.65rem 0;
}

.cc-card h4 {
  font-family: var(--font-pixel) !important;
  margin: 0 0 0.4rem 0 !important;
  padding: 0 !important;
  color: #ffffff !important;
  font-size: 1.12rem !important;
  font-weight: 700 !important;
  line-height: 1.3 !important;
}

.cc-card .tl {
  font-family: var(--font-sans) !important;
  color: #e8eff8 !important;
  font-size: 0.96rem !important;
  font-weight: 500;
  line-height: 1.48;
  margin: 0;
}

/* Structured 2-Row Badge Stack inside Cards */
.cc-card-footer {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  margin-top: auto;
}

.cc-card-experts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.45rem;
}

/* Stacked Pill: Name Centered & Larger on Top, Role Centered & Smaller Below */
.cc-pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.18rem;
  font-family: var(--font-mono) !important;
  background: #09101b;
  border: 1px solid #284266;
  padding: 0.42rem 0.65rem;
  border-radius: 3px;
  text-align: center;
}

.cc-pill.council-pill {
  width: 100%;
  border-color: color-mix(in srgb, var(--accent, var(--teal)) 65%, #243b5c);
  background: color-mix(in srgb, var(--accent, var(--teal)) 13%, #09101b);
}

.cc-pill-name {
  display: block;
  width: 100%;
  text-align: center;
  font-family: var(--font-mono) !important;
  font-size: 0.92rem !important;
  font-weight: 700 !important;
  color: var(--accent, var(--teal)) !important;
  line-height: 1.2;
}

.cc-pill-role {
  display: block;
  width: 100%;
  text-align: center;
  font-family: var(--font-sans) !important;
  font-size: 0.76rem !important;
  font-weight: 500 !important;
  color: #cbd5e1 !important;
  line-height: 1.2;
}

/* Minimalist Pixelated Buttons */
.stButton button {
  font-family: var(--font-pixel) !important;
  font-size: 0.82rem !important;
  font-weight: 400 !important;
  letter-spacing: 0.5px;
  color: #ffffff !important;
  background: #132238 !important;
  border: 2px solid #2c4970 !important;
  border-radius: 3px !important;
  padding: 0.68rem 0.95rem !important;
  min-height: 46px !important;
  box-shadow: 4px 4px 0 #050911 !important;
  transition: transform 0.08s ease, border-color 0.08s ease, background 0.08s ease !important;
  white-space: normal !important;
  line-height: 1.35 !important;
}

.stButton button p {
  font-family: var(--font-pixel) !important;
  font-size: 0.82rem !important;
  color: #ffffff !important;
}

.stButton button:hover {
  background: #1a2f4c !important;
  border-color: var(--teal) !important;
  color: var(--teal) !important;
  transform: translate(-1px, -1px);
  box-shadow: 5px 5px 0 #050911 !important;
}

.stButton button:hover p {
  color: var(--teal) !important;
}

.stButton button:active {
  transform: translate(2px, 2px);
  box-shadow: 1px 1px 0 #050911 !important;
}

/* Unified Room Header Box (Wraps Room Info + Floorplan Button Inside One Card) */
div[class*="st-key-room_hdr_box_"] {
  border: 2px solid #243b5c !important;
  border-left: 6px solid var(--room-accent, var(--teal)) !important;
  background: #0e1828 !important;
  padding: 1.25rem 1.45rem !important;
  border-radius: 4px !important;
  box-shadow: 5px 5px 0 #050911 !important;
  margin-bottom: 1rem !important;
}

.cc-header {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}

.cc-header-main {
  display: flex;
  flex-direction: column;
  gap: 0.42rem;
}

.cc-header-top {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.cc-header h2 {
  font-family: var(--font-pixel) !important;
  margin: 0 !important;
  padding: 0 !important;
  font-size: 1.4rem !important;
  color: #ffffff !important;
}

.cc-room-sub {
  font-family: var(--font-sans) !important;
  color: #e8eff8 !important;
  font-size: 1.04rem !important;
  margin: 0 !important;
}

.cc-crew {
  display: grid;
  grid-template-columns: repeat(3, minmax(150px, 210px));
  gap: 0.5rem;
}

/* Communication Mode Selector Box */
.cc-comm-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.85rem;
  background: #0c1523;
  border: 1.5px solid #243b5c;
  border-radius: 4px;
  padding: 0.85rem 1.15rem;
  margin: 0.25rem 0 0.85rem 0;
}

.cc-comm-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.cc-comm-icon {
  font-family: var(--font-mono) !important;
  font-size: 1.25rem;
  color: var(--teal) !important;
  width: 38px;
  height: 38px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #080e17;
  border: 1.5px solid var(--teal);
  box-shadow: 2px 2px 0 #04080e;
}

.cc-comm-title {
  font-family: var(--font-pixel) !important;
  font-size: 0.82rem;
  color: #ffffff;
  margin: 0 0 0.2rem 0;
}

.cc-comm-desc {
  font-family: var(--font-sans) !important;
  font-size: 0.96rem;
  color: #cbd5e1;
  margin: 0;
}

.cc-try-label {
  font-family: var(--font-pixel) !important;
  font-size: 0.8rem;
  color: var(--teal) !important;
  margin: 1.1rem 0 0.55rem 0;
  letter-spacing: 1px;
}

/* Chat Messages & Input */
[data-testid="stChatMessage"] {
  background: #0e1828 !important;
  border: 1.5px solid #243b5c !important;
  border-radius: 4px !important;
  padding: 1.05rem 1.2rem !important;
  margin-bottom: 0.8rem !important;
  box-shadow: 4px 4px 0 #050911;
}

[data-testid="stChatInput"] {
  background: #0e1828 !important;
  border: 2px solid #2c4970 !important;
  border-radius: 4px !important;
}

[data-testid="stChatInput"] textarea {
  font-family: var(--font-sans) !important;
  font-size: 1.02rem !important;
  color: #ffffff !important;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
  background: #09101b !important;
  border-right: 2px solid #243b5c !important;
}

.cc-log {
  border: 1.5px solid #243b5c;
  border-left: 4px solid var(--teal);
  background: #0e1828;
  padding: 0.6rem 0.75rem;
  border-radius: 3px;
  margin-bottom: 0.55rem;
  box-shadow: 3px 3px 0 #050911;
}

.cc-log .eng {
  font-family: var(--font-mono) !important;
  font-size: 0.76rem;
  font-weight: 700;
  color: var(--teal) !important;
  display: block;
  margin-bottom: 0.22rem;
}

.cc-log .q {
  font-family: var(--font-mono) !important;
  font-size: 0.9rem !important;
  color: #f8fafc !important;
}
</style>
"""


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
