import base64
import io
import os
from functools import lru_cache

import streamlit as st
from PIL import Image

import config
from constants import ROOM_ORDER, ROOMS

_ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
_BANNER = os.path.join(_ASSETS, "clubhouse.png")
_PLAYER = os.path.join(_ASSETS, "player.png")

# Exact 6-room symmetric grid coordinates matching the new 3x2 minimalist floorplan
_ROOM_ZONES = [
    {
        "key": "search",
        "x1": 4.5, "y1": 6.5, "x2": 32.5, "y2": 43.0,
        "doorX": 19.5, "doorY": 38.0,
    },
    {
        "key": "travel",
        "x1": 34.5, "y1": 6.5, "x2": 65.5, "y2": 43.0,
        "doorX": 50.0, "doorY": 38.0,
    },
    {
        "key": "finance",
        "x1": 67.5, "y1": 6.5, "x2": 95.5, "y2": 43.0,
        "doorX": 80.5, "doorY": 38.0,
    },
    {
        "key": "media",
        "x1": 4.5, "y1": 56.5, "x2": 32.5, "y2": 93.0,
        "doorX": 26.5, "doorY": 62.0,
    },
    {
        "key": "market",
        "x1": 34.5, "y1": 56.5, "x2": 65.5, "y2": 93.0,
        "doorX": 50.0, "doorY": 62.0,
    },
    {
        "key": "observatory",
        "x1": 67.5, "y1": 56.5, "x2": 95.5, "y2": 93.0,
        "doorX": 80.5, "doorY": 62.0,
    },
]


@lru_cache(maxsize=2)
def _load_assets(mtime_b: float, mtime_p: float) -> tuple[str, str]:
    banner_b64 = ""
    if os.path.exists(_BANNER):
        with Image.open(_BANNER) as img:
            img = img.convert("RGB")
            img.thumbnail((1264, 848), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=90, optimize=True)
            banner_b64 = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

    player_b64 = ""
    if os.path.exists(_PLAYER):
        with Image.open(_PLAYER) as p:
            p = p.convert("RGBA")
            p.thumbnail((140, 220), Image.Resampling.NEAREST)
            buf = io.BytesIO()
            p.save(buf, format="PNG", optimize=True)
            player_b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

    return banner_b64, player_b64


_MAP_HTML = """
<div class="cc-game-shell" id="cc-game-shell" tabindex="0">
  <div class="cc-hud-bar">
    <div class="cc-hud-left">
      <span class="cc-key-badge">▲ ▼ ◄ ►</span>
      <span class="cc-key-badge">WASD</span>
      <span class="cc-hud-text">Walk the corridor · Click any room or press <b>ENTER</b> inside to launch its SerpApi Council</span>
    </div>
    <div class="cc-hud-status" id="cc-hud-status">▣ CENTRAL CORRIDOR</div>
  </div>

  <div class="cc-viewport" id="cc-viewport">
    <img id="cc-map-img" class="cc-map-img" alt="6-Room SerpApi Floorplan" draggable="false" />
    <div id="cc-zones-layer" class="cc-zones-layer"></div>

    <div id="cc-player" class="cc-player">
      <div class="cc-player-prompt" id="cc-player-prompt">ENTER ROOM ►</div>
      <div class="cc-player-tag">OPERATIVE</div>
      <img id="cc-player-img" class="cc-player-sprite" alt="Player" draggable="false" />
      <div class="cc-player-shadow"></div>
    </div>

    <div class="cc-dpad" aria-label="Movement Controls">
      <button type="button" class="cc-dpad-btn up" data-dir="up" title="Walk Up">▲</button>
      <button type="button" class="cc-dpad-btn left" data-dir="left" title="Walk Left">◄</button>
      <button type="button" class="cc-dpad-btn action" id="cc-dpad-enter" title="Enter Current Room">⏎</button>
      <button type="button" class="cc-dpad-btn right" data-dir="right" title="Walk Right">►</button>
      <button type="button" class="cc-dpad-btn down" data-dir="down" title="Walk Down">▼</button>
    </div>
  </div>
</div>
"""

_MAP_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Silkscreen:wght@400;700&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@500;600;700&display=swap');

* {
  box-sizing: border-box;
  user-select: none;
}

.cc-game-shell {
  width: 100%;
  background: #0b131e;
  border: 2px solid #243b5c;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 6px 6px 0 #04080e;
  outline: none;
  font-family: 'Space Grotesk', sans-serif;
}

.cc-game-shell:focus-within, .cc-game-shell:focus {
  border-color: #2dd4bf;
}

.cc-hud-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.65rem;
  padding: 0.6rem 1rem;
  background: #0e1828;
  border-bottom: 2px solid #1e314d;
}

.cc-hud-left {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.cc-key-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  font-weight: 700;
  color: #2dd4bf;
  background: #080e17;
  border: 1.5px solid #2dd4bf;
  padding: 0.22rem 0.55rem;
  border-radius: 2px;
  box-shadow: 2px 2px 0 #04080e;
}

.cc-hud-text {
  color: #e2e8f0;
  font-size: 0.95rem;
  font-weight: 500;
}

.cc-hud-text b {
  color: #2dd4bf;
  font-family: 'JetBrains Mono', monospace;
}

.cc-hud-status {
  font-family: 'Silkscreen', monospace;
  font-size: 0.76rem;
  color: #2dd4bf;
  background: #080e17;
  border: 1.5px solid #2c4970;
  padding: 0.32rem 0.8rem;
  border-radius: 2px;
  white-space: nowrap;
}

.cc-viewport {
  position: relative;
  width: 100%;
  aspect-ratio: 1264 / 848;
  background: #080e17;
  overflow: hidden;
}

.cc-map-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  pointer-events: none;
  image-rendering: pixelated;
}

.cc-zones-layer {
  position: absolute;
  inset: 0;
  z-index: 2;
}

.cc-zone {
  position: absolute;
  border: 2px solid transparent;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.14s ease;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.55rem;
}

.cc-zone:hover, .cc-zone.active {
  border: 2px solid var(--accent, #2dd4bf);
  background: radial-gradient(circle at 50% 50%, rgba(15, 23, 42, 0.1), color-mix(in srgb, var(--accent) 22%, rgba(8, 14, 23, 0.55)));
  box-shadow: inset 0 0 20px color-mix(in srgb, var(--accent) 30%, transparent);
}

.cc-zone-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.4rem;
  width: 100%;
}

.cc-zone-header {
  display: inline-flex;
  align-items: center;
  gap: 0.42rem;
  background: rgba(8, 14, 23, 0.94);
  border: 1.5px solid var(--accent, #2dd4bf);
  padding: 0.28rem 0.6rem;
  border-radius: 2px;
  box-shadow: 3px 3px 0 #04080e;
}

.cc-zone-icon {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.94rem;
  font-weight: 700;
  color: var(--accent, #2dd4bf);
}

.cc-zone-title {
  font-family: 'Silkscreen', monospace;
  font-size: 0.74rem;
  color: #ffffff;
}

.cc-zone-serp {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--accent, #2dd4bf);
  background: rgba(8, 14, 23, 0.94);
  border: 1px solid rgba(255, 255, 255, 0.22);
  padding: 0.22rem 0.5rem;
  border-radius: 2px;
  box-shadow: 2px 2px 0 #04080e;
}

.cc-zone-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.4rem;
  width: 100%;
}

.cc-zone-sub {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.74rem;
  font-weight: 600;
  color: #f8fafc;
  background: rgba(8, 14, 23, 0.94);
  border: 1px solid #2c4970;
  padding: 0.24rem 0.55rem;
  border-radius: 2px;
  opacity: 0;
  transform: translateY(3px);
  transition: all 0.14s ease;
}

.cc-zone:hover .cc-zone-sub, .cc-zone.active .cc-zone-sub {
  opacity: 1;
  transform: translateY(0);
}

.cc-zone-cta {
  font-family: 'Silkscreen', monospace;
  font-size: 0.66rem;
  color: #080e17;
  background: var(--accent, #2dd4bf);
  padding: 0.28rem 0.6rem;
  border-radius: 2px;
  box-shadow: 3px 3px 0 #04080e;
  opacity: 0;
  transform: scale(0.95);
  transition: all 0.14s ease;
}

.cc-zone:hover .cc-zone-cta, .cc-zone.active .cc-zone-cta {
  opacity: 1;
  transform: scale(1);
}

/* Minimalist Pixel Character */
.cc-player {
  position: absolute;
  z-index: 10;
  width: 4.8%;
  min-width: 36px;
  max-width: 54px;
  transform: translate(-50%, -82%);
  pointer-events: none;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.cc-player-sprite {
  width: 100%;
  height: auto;
  display: block;
  image-rendering: pixelated;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.85));
  transition: transform 0.08s ease;
}

.cc-player.walking .cc-player-sprite {
  animation: walk-bob 0.22s infinite alternate steps(2);
}

@keyframes walk-bob {
  from { transform: translateY(0px); }
  to   { transform: translateY(-4px); }
}

.cc-player-shadow {
  width: 70%;
  height: 8px;
  background: rgba(4, 8, 14, 0.75);
  margin-top: -3px;
  border-radius: 2px;
}

.cc-player-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.56rem;
  font-weight: 700;
  color: #2dd4bf;
  background: #080e17;
  border: 1px solid #2dd4bf;
  padding: 0.08rem 0.32rem;
  border-radius: 2px;
  margin-bottom: 3px;
  white-space: nowrap;
  box-shadow: 2px 2px 0 #04080e;
}

.cc-player-prompt {
  font-family: 'Silkscreen', monospace;
  font-size: 0.6rem;
  color: #080e17;
  background: #2dd4bf;
  border: 1.5px solid #ffffff;
  padding: 0.22rem 0.48rem;
  border-radius: 2px;
  margin-bottom: 4px;
  white-space: nowrap;
  box-shadow: 3px 3px 0 #04080e;
  display: none;
  pointer-events: auto;
  cursor: pointer;
}

.cc-player-prompt.visible {
  display: block;
}

/* On-screen Pixel D-Pad */
.cc-dpad {
  position: absolute;
  right: 12px;
  bottom: 12px;
  z-index: 15;
  display: grid;
  grid-template-columns: repeat(3, 32px);
  grid-template-rows: repeat(3, 32px);
  gap: 3px;
  background: rgba(8, 14, 23, 0.88);
  padding: 5px;
  border-radius: 3px;
  border: 1.5px solid #243b5c;
  box-shadow: 4px 4px 0 #04080e;
}

.cc-dpad-btn {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 700;
  color: #f1f5f9;
  background: #132238;
  border: 1px solid #284266;
  border-radius: 2px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.cc-dpad-btn:hover {
  background: #1d3354;
  border-color: #2dd4bf;
  color: #2dd4bf;
}

.cc-dpad-btn.up    { grid-column: 2; grid-row: 1; }
.cc-dpad-btn.left  { grid-column: 1; grid-row: 2; }
.cc-dpad-btn.action {
  grid-column: 2;
  grid-row: 2;
  background: #163040;
  border-color: #2dd4bf;
  color: #2dd4bf;
}
.cc-dpad-btn.right { grid-column: 3; grid-row: 2; }
.cc-dpad-btn.down  { grid-column: 2; grid-row: 3; }
"""

_MAP_JS = """
export default function(component) {
  const { data, setTriggerValue, parentElement } = component;
  if (!data) return;

  const shell = parentElement.querySelector('#cc-game-shell');
  const mapImg = parentElement.querySelector('#cc-map-img');
  const playerEl = parentElement.querySelector('#cc-player');
  const playerImg = parentElement.querySelector('#cc-player-img');
  const promptEl = parentElement.querySelector('#cc-player-prompt');
  const zonesLayer = parentElement.querySelector('#cc-zones-layer');
  const statusEl = parentElement.querySelector('#cc-hud-status');
  const enterBtn = parentElement.querySelector('#cc-dpad-enter');

  if (data.banner) mapImg.src = data.banner;
  if (data.player) playerImg.src = data.player;

  const rooms = data.rooms || [];
  // Spawn player right in the center horizontal corridor
  let px = 50.0;
  let py = 50.0;
  let targetX = null;
  let targetY = null;
  let pendingRoomEnter = null;
  let facing = 1;
  let activeZone = null;
  let enterCooldown = false;

  const keys = { up: false, down: false, left: false, right: false };

  zonesLayer.innerHTML = '';
  const zoneEls = {};
  rooms.forEach((r) => {
    const z = document.createElement('div');
    z.className = 'cc-zone';
    z.style.left = r.x1 + '%';
    z.style.top = r.y1 + '%';
    z.style.width = (r.x2 - r.x1) + '%';
    z.style.height = (r.y2 - r.y1) + '%';
    z.style.setProperty('--accent', r.accent);

    z.innerHTML = `
      <div class="cc-zone-top">
        <div class="cc-zone-header">
          <span class="cc-zone-icon">${r.icon}</span>
          <span class="cc-zone-title">${r.name}</span>
        </div>
        <span class="cc-zone-serp">${r.engine_short}</span>
      </div>
      <div class="cc-zone-bottom">
        <div class="cc-zone-sub">${r.icon} Council · ${r.crew}</div>
        <div class="cc-zone-cta">ENTER ►</div>
      </div>
    `;

    z.addEventListener('click', (e) => {
      e.stopPropagation();
      targetX = r.doorX;
      targetY = r.doorY;
      pendingRoomEnter = r.key;
      shell.focus();
    });

    zonesLayer.appendChild(z);
    zoneEls[r.key] = z;
  });

  const viewport = parentElement.querySelector('#cc-viewport');
  viewport.addEventListener('click', (e) => {
    if (e.target.closest('.cc-dpad')) return;
    const rect = viewport.getBoundingClientRect();
    targetX = Math.max(7, Math.min(93, ((e.clientX - rect.left) / rect.width) * 100));
    targetY = Math.max(10, Math.min(90, ((e.clientY - rect.top) / rect.height) * 100));
    pendingRoomEnter = null;
    shell.focus();
  });

  function triggerEnter(roomKey) {
    if (enterCooldown || !roomKey) return;
    enterCooldown = true;
    setTriggerValue('selected_room', roomKey);
    setTimeout(() => { enterCooldown = false; }, 800);
  }

  promptEl.addEventListener('click', (e) => {
    e.stopPropagation();
    if (activeZone) triggerEnter(activeZone.key);
  });

  enterBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    if (activeZone) {
      triggerEnter(activeZone.key);
    }
  });

  parentElement.querySelectorAll('.cc-dpad-btn[data-dir]').forEach((btn) => {
    const dir = btn.getAttribute('data-dir');
    const start = (e) => {
      e.preventDefault();
      e.stopPropagation();
      targetX = null;
      targetY = null;
      pendingRoomEnter = null;
      keys[dir] = true;
      shell.focus();
    };
    const end = (e) => {
      e.preventDefault();
      keys[dir] = false;
    };
    btn.addEventListener('mousedown', start);
    btn.addEventListener('touchstart', start, { passive: false });
    window.addEventListener('mouseup', end);
    window.addEventListener('touchend', end);
  });

  function onKeyDown(e) {
    const tag = (document.activeElement && document.activeElement.tagName) || '';
    if (tag === 'INPUT' || tag === 'TEXTAREA') return;

    if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') {
      keys.up = true; targetX = null; targetY = null; pendingRoomEnter = null; e.preventDefault();
    } else if (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') {
      keys.down = true; targetX = null; targetY = null; pendingRoomEnter = null; e.preventDefault();
    } else if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') {
      keys.left = true; targetX = null; targetY = null; pendingRoomEnter = null; e.preventDefault();
    } else if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') {
      keys.right = true; targetX = null; targetY = null; pendingRoomEnter = null; e.preventDefault();
    } else if ((e.key === 'Enter' || e.key === ' ') && activeZone) {
      e.preventDefault();
      triggerEnter(activeZone.key);
    }
  }

  function onKeyUp(e) {
    if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') keys.up = false;
    if (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') keys.down = false;
    if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') keys.left = false;
    if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') keys.right = false;
  }

  window.addEventListener('keydown', onKeyDown);
  window.addEventListener('keyup', onKeyUp);

  let rafId = null;
  const speed = 0.48;

  function step() {
    let dx = 0;
    let dy = 0;

    if (keys.left) dx -= speed;
    if (keys.right) dx += speed;
    if (keys.up) dy -= speed;
    if (keys.down) dy += speed;

    if (dx !== 0 && dy !== 0) {
      dx *= 0.7071;
      dy *= 0.7071;
    }

    if (targetX !== null && targetY !== null) {
      const tx = targetX - px;
      const ty = targetY - py;
      const dist = Math.hypot(tx, ty);
      if (dist < 1.1) {
        px = targetX;
        py = targetY;
        targetX = null;
        targetY = null;
        if (pendingRoomEnter) {
          const rk = pendingRoomEnter;
          pendingRoomEnter = null;
          triggerEnter(rk);
        }
      } else {
        const moveSpeed = pendingRoomEnter ? speed * 1.65 : speed * 1.25;
        dx = (tx / dist) * moveSpeed;
        dy = (ty / dist) * moveSpeed;
      }
    }

    const isMoving = Math.abs(dx) > 0.01 || Math.abs(dy) > 0.01;
    if (dx < -0.01) facing = -1;
    if (dx > 0.01) facing = 1;

    px = Math.max(7, Math.min(93, px + dx));
    py = Math.max(10, Math.min(90, py + dy));

    playerEl.style.left = px + '%';
    playerEl.style.top = py + '%';
    playerEl.classList.toggle('walking', isMoving);
    playerImg.style.transform = `scaleX(${facing})`;

    let found = null;
    for (const r of rooms) {
      if (px >= r.x1 && px <= r.x2 && py >= r.y1 && py <= r.y2) {
        found = r;
        break;
      }
    }

    activeZone = found;
    for (const r of rooms) {
      const el = zoneEls[r.key];
      if (el) el.classList.toggle('active', Boolean(found && found.key === r.key));
    }

    if (found) {
      statusEl.textContent = `${found.icon} ${found.name} [${found.engine_short}] — PRESS ENTER`;
      statusEl.style.borderColor = found.accent;
      statusEl.style.color = found.accent;
      promptEl.textContent = `ENTER ${found.name.toUpperCase()} ►`;
      promptEl.style.background = found.accent;
      promptEl.classList.add('visible');
    } else {
      statusEl.textContent = '▣ CENTRAL CORRIDOR // 6 SERP ROOMS';
      statusEl.style.borderColor = '#243b5c';
      statusEl.style.color = '#2dd4bf';
      promptEl.classList.remove('visible');
    }

    rafId = requestAnimationFrame(step);
  }

  rafId = requestAnimationFrame(step);

  return () => {
    if (rafId) cancelAnimationFrame(rafId);
    window.removeEventListener('keydown', onKeyDown);
    window.removeEventListener('keyup', onKeyUp);
  };
}
"""

_clubhouse_map = st.components.v2.component(
    "clubhouse_interactive_map",
    html=_MAP_HTML,
    css=_MAP_CSS,
    js=_MAP_JS,
)


def render() -> None:
    st.markdown(
        f"<div class='cc-hero'>"
        f"<div class='cc-brand-row'>"
        f"<div class='cc-logo-mark'><span></span><span></span><span></span><span></span></div>"
        f"<h1>{config.APP_TITLE}</h1>"
        f"</div>"
        f"<p class='cc-tagline'>{config.APP_TAGLINE}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    mtime_b = os.path.getmtime(_BANNER) if os.path.exists(_BANNER) else 0.0
    mtime_p = os.path.getmtime(_PLAYER) if os.path.exists(_PLAYER) else 0.0
    banner_b64, player_b64 = _load_assets(mtime_b, mtime_p)

    rooms_payload = []
    for z in _ROOM_ZONES:
        r = ROOMS[z["key"]]
        engine_short = r.caption.replace("serpapi : ", "")
        rooms_payload.append({
            **z,
            "name": r.name,
            "icon": r.icon,
            "accent": r.accent,
            "engine_short": engine_short,
            "tagline": r.tagline,
            "crew": " + ".join(e.name for e in r.experts),
        })

    res = _clubhouse_map(
        data={
            "banner": banner_b64,
            "player": player_b64,
            "rooms": rooms_payload,
        },
        on_selected_room_change=lambda: None,
        key="clubhouse_world",
    )

    if res and getattr(res, "selected_room", None):
        st.session_state.room = res.selected_room
        st.rerun()

    st.markdown("<div class='cc-section-title'>// DIRECT TERMINAL ACCESS — 6 SPECIALIZED SERPAPI ROOMS</div>", unsafe_allow_html=True)

    for start in (0, 3):
        cols = st.columns(3, gap="medium")
        for col, key in zip(cols, ROOM_ORDER[start:start + 3]):
            room = ROOMS[key]
            experts_row = "".join(
                f"<div class='cc-pill' title='Talk 1-on-1 with {e.name} ({e.engine})'>"
                f"<span class='cc-pill-name'>{e.name}</span>"
                f"<span class='cc-pill-role'>{e.role}</span>"
                f"</div>"
                for e in room.experts
            )
            with col:
                st.markdown(
                    f"<div class='cc-card' style='--accent:{room.accent}'>"
                    f"<div class='cc-card-top'>"
                    f"<span class='cc-icon-box'>{room.icon}</span>"
                    f"<span class='cc-engine-tag'>{room.caption}</span>"
                    f"</div>"
                    f"<div class='cc-card-body'>"
                    f"<h4>{room.name}</h4>"
                    f"<div class='tl'>{room.tagline}</div>"
                    f"</div>"
                    f"<div class='cc-card-footer'>"
                    f"<div class='cc-pill council-pill'>"
                    f"<span class='cc-pill-name'>{room.icon} Room Council</span>"
                    f"<span class='cc-pill-role'>Both Analysts Collaborate</span>"
                    f"</div>"
                    f"<div class='cc-card-experts'>{experts_row}</div>"
                    f"</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                if st.button(f"ENTER {room.name.upper()} ►", key=f"enter_{key}", width="stretch"):
                    st.session_state.room = key
                    st.rerun()
