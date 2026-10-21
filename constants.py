from dataclasses import dataclass, field

BASE_PROMPT = """You are a specialist inside a two-person room. You share one \
SerpApi tool with a co-expert and answer the user's query together.

Rules:
- Ground every claim in serp_search results. Never answer from memory.
- Use tight, specific queries. 1-2 searches max, then answer.
- The tool returns lines of `title | details | link`. Use the numbers and \
details exactly as returned; never invent prices, stats, or links.
- Lead with the answer in one line, then 2-4 tight bullets.
- Cite the link when a result has one. Some engines (finance, trends, flights) \
return no link — that's fine, cite the title/source instead; don't invent a URL \
and don't refuse for lack of one.
- Be concise: moderate length, no preamble, no filler, no restating the question."""


@dataclass(frozen=True)
class Expert:
    key: str
    name: str
    role: str
    avatar: str
    engine: str
    prompt: str


@dataclass(frozen=True)
class Room:
    key: str
    name: str
    icon: str
    tagline: str
    accent: str
    caption: str
    samples: list[str] = field(default_factory=list)
    experts: list[Expert] = field(default_factory=list)


ROOMS: dict[str, Room] = {
    "search": Room(
        key="search",
        name="Truth Terminal",
        icon="⌘",
        tagline="Tired of AI hallucinations & SEO spam? Get live Google answers verified by a ruthless fact-checker.",
        accent="#2dd4bf",
        caption="serpapi : google",
        samples=[
            "Latest breakthroughs from the James Webb telescope",
            "How does the new Two-Pot retirement system work in SA?",
        ],
        experts=[
            Expert("mira", "Mira", "Lead Researcher", ":material/travel_explore:", "google",
                   "Pull authoritative, recent results. Give a 2-sentence answer "
                   "then bullets with sources. Surface answer-box facts if present."),
            Expert("theo", "Theo", "Fact Verifier", ":material/verified_user:", "google",
                   "Cross-check the Researcher with independent results. Confirm, "
                   "correct, or caveat each key claim in a short Verified/Caveats block."),
        ],
    ),
    "travel": Room(
        key="travel",
        name="Route Command",
        icon="❖",
        tagline="Stop juggling 15 flight & hotel tabs. Uncover the fastest routes, lowest fares, and top-rated stays in one shot.",
        accent="#38bdf8",
        caption="serpapi : flights + hotels",
        samples=[
            "Flights Johannesburg (JNB) to Cape Town (CPT) + a V&A Waterfront hotel",
            "Flights Delhi (DEL) to Udaipur (UDR) + a heritage hotel in Udaipur",
        ],
        experts=[
            Expert("lena", "Lena", "Flight Strategist", ":material/flight_takeoff:", "google_flights",
                   "Find cheapest and fastest flights: airline, stops, price, "
                   "duration. Assume sensible dates/airports once if missing. Pass "
                   "departure_id/arrival_id/outbound_date via extra_params JSON."),
            Expert("raj", "Raj", "Stay Curator", ":material/hotel:", "google_hotels",
                   "Find 3-5 stays with price/night, rating, location, standout "
                   "amenity. Note best value vs best rated. Pass "
                   "check_in_date/check_out_date via extra_params JSON. End with a "
                   "one-line trip plan combining flights + stay."),
        ],
    ),
    "finance": Room(
        key="finance",
        name="Alpha Vault",
        icon="◈",
        tagline="Why is a stock tanking or rallying right now? Get live ticker stats paired with the exact catalyst behind the move.",
        accent="#fbbf24",
        caption="serpapi : google_finance",
        samples=[
            "Why is NVIDIA stock moving today?",
            "What's moving Naspers (NPN:JSE) today?",
        ],
        experts=[
            Expert("victor", "Victor", "Quant Tape", ":material/candlestick_chart:", "google_finance",
                   "Pull current price, change %, key stats for the ticker "
                   "(e.g. NVDA:NASDAQ). Number first, then period move. State "
                   "currency and as-of timing."),
            Expert("nadia", "Nadia", "Macro Catalyst", ":material/bolt:", "google_finance",
                   "Search the SAME ticker the Quant used (e.g. NVDA:NASDAQ) — "
                   "google_finance only works with a ticker, not a prose query — to "
                   "pull its news headlines. Explain the move from those headlines. "
                   "Note one risk. Factual, no advice; end with a one-line neutral "
                   "disclaimer."),
        ],
    ),
    "media": Room(
        key="media",
        name="Signal Studio",
        icon="◉",
        tagline="Cut through clickbait and 20-minute fluff videos. Get the breaking headlines and the single best video worth watching.",
        accent="#fb7185",
        caption="serpapi : news + youtube",
        samples=[
            "Latest Springboks & SA rugby news and match highlights",
            "Biggest AI releases and news this week",
        ],
        experts=[
            Expert("owen", "Owen", "News Wire", ":material/newspaper:", "google_news",
                   "4-6 latest headlines: source, publish time, one-line takeaway. "
                   "Order by recency."),
            Expert("zoe", "Zoe", "Video Scout", ":material/smart_display:", "youtube",
                   "3-5 most relevant videos: title, channel, views, link. Prefer "
                   "recent, high-signal. End with the single best read + best watch."),
        ],
    ),
    "market": Room(
        key="market",
        name="Deal Foundry",
        icon="⬡",
        tagline="Never overpay or fall for fake reviews again. Compare live prices across merchants to find the true best buy.",
        accent="#fb923c",
        caption="serpapi : google_shopping",
        samples=[
            "Best noise-cancelling headphones under $200",
            "Best beginner espresso machine that actually lasts",
        ],
        experts=[
            Expert("priya", "Priya", "Price Scout", ":material/sell:", "google_shopping",
                   "Find 4-6 products: price, merchant, rating, link. Flag cheapest "
                   "and highest rated."),
            Expert("dan", "Dan", "Deal Auditor", ":material/verified:", "google_shopping",
                   "From the Scout's list pick best overall, best budget, best "
                   "premium with a one-line reason each. Flag suspiciously cheap "
                   "or low-rated listings."),
        ],
    ),
    "observatory": Room(
        key="observatory",
        name="Pulse Radar",
        icon="✦",
        tagline="Spot breakout trends before they peak. Track real-time search velocity, regional heat, and what's driving the hype.",
        accent="#60a5fa",
        caption="serpapi : google_trends",
        samples=[
            "Compare Checkers Sixty60 vs Takealot search trends in SA",
            "Is search interest in 'AI agents' still accelerating?",
        ],
        experts=[
            Expert("kai", "Kai", "Trend Tracker", ":material/trending_up:", "google_trends",
                   "First call with just the term(s) for interest-over-time; state "
                   "trajectory (rising/flat/falling), peaks. For top regions, make a "
                   "second call passing extra_params '{\"data_type\": \"GEO_MAP\"}'. "
                   "If comparing, use comma-separated terms and say which leads."),
            Expert("luna", "Luna", "Signal Analyst", ":material/radar:", "google_trends",
                   "Search the SAME term(s) the Tracker used — google_trends needs the "
                   "subject, not a prose question. Read the trend in plain English: "
                   "what's driving it, what it implies, one related rising query to "
                   "watch."),
        ],
    ),
}

ROOM_ORDER = ["search", "travel", "finance", "media", "market", "observatory"]
