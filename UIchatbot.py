import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()

st.set_page_config(page_title="Mood AI", page_icon="🎭", layout="centered")

# ---------------------------------------------------------------------------
# Mode definitions — each mood gets its own persona, color, and vibe
# ---------------------------------------------------------------------------
MODES = {
    "angry": {
        "label": "Angry",
        "emoji": "🔥",
        "tagline": "Short fuse. Zero patience. Answers you anyway.",
        "system": "You are a angry ai agent that answers questions in an angry way to a girl.",
        "accent": "#E4572E",
        "accent_dark": "#B8401A",
        "bg": "#FFF4EF",
    },
    "flirty": {
        "label": "Flirty",
        "emoji": "💋",
        "tagline": "Winks between the words. Charm on tap.",
        "system": "You are a flirty ai agent that answers questions in a flirty way to a girl.",
        "accent": "#D6336C",
        "accent_dark": "#A8285A",
        "bg": "#FFF0F5",
    },
    "funny": {
        "label": "Funny",
        "emoji": "😂",
        "tagline": "Every answer comes with a punchline.",
        "system": "You are a funny ai agent that answers questions in a funny way to a girl.",
        "accent": "#F2A93B",
        "accent_dark": "#C9800F",
        "bg": "#FFFBF0",
    },
}

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "mode_key" not in st.session_state:
    st.session_state.mode_key = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------------------------
# Shared styling
# ---------------------------------------------------------------------------
def inject_css(mode):
    accent = mode["accent"] if mode else "#7C6BAF"
    accent_dark = mode["accent_dark"] if mode else "#5B4D8A"
    bg = mode["bg"] if mode else "#F7F5FB"

    st.markdown(
        f"""
        <style>
            .stApp {{
                background: {bg};
            }}
            #MainMenu, footer, header {{visibility: hidden;}}

            .mood-title {{
                font-family: 'Georgia', serif;
                font-size: 2.6rem;
                font-weight: 700;
                text-align: center;
                color: #2B2B2B;
                margin-bottom: 0.1rem;
                letter-spacing: -0.02em;
            }}
            .mood-subtitle {{
                text-align: center;
                color: #6B6B6B;
                font-size: 1rem;
                margin-bottom: 2.2rem;
            }}

            div[data-testid="stVerticalBlockBorderWrapper"] {{
                border-radius: 18px !important;
            }}

            .active-banner {{
                display: flex;
                align-items: center;
                gap: 0.6rem;
                background: {accent};
                color: white;
                padding: 0.7rem 1.1rem;
                border-radius: 14px;
                font-size: 1.05rem;
                font-weight: 600;
                margin-bottom: 1.2rem;
                box-shadow: 0 3px 10px rgba(0,0,0,0.08);
            }}

            .stChatMessage {{
                border-radius: 16px !important;
    
            }}
            
            /* User bubble = light grey */
.stChatMessage:has([data-testid="stChatMessageAvatarUser"]) {{
    background-color: #E4E4E4 !important;
}}

/* Bot bubble = grey */
.stChatMessage:has([data-testid="stChatMessageAvatarCustom"]) {{
    background-color: #9E9E9E !important;
}}

/* Make text dark so it's visible on grey */
.stChatMessage p, .stChatMessage span,
.stChatMessage div, .stChatMessage li, .stChatMessage code,
.stChatMessage [data-testid="stMarkdownContainer"] * {{
    color: #1A1A1A !important;
}}

            div[data-testid="stChatInput"] textarea {{
                border-radius: 12px !important;
            }}

            .stButton>button {{
                border-radius: 12px;
                font-weight: 600;
                transition: transform 0.15s ease;
            }}
            .stButton>button:hover {{
                transform: translateY(-2px);
            }}

            .mode-btn>button {{
                background: {accent} !important;
                color: white !important;
                border: none !important;
            }}
            .mode-btn>button:hover {{
                background: {accent_dark} !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Screen 1 — Mood picker
# ---------------------------------------------------------------------------
def render_mode_picker():
    inject_css(None)
    st.markdown('<div class="mood-title">🎭 Pick your AI\'s mood</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="mood-subtitle">The bot will stay fully in character until you reset it.</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    for col, (key, mode) in zip(cols, MODES.items()):
        with col:
            with st.container(border=True):
                st.markdown(
                    f"<div style='text-align:center; font-size:2.4rem;'>{mode['emoji']}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='text-align:center; font-weight:700; font-size:1.15rem; color:{mode['accent']};'>{mode['label']}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='text-align:center; font-size:0.85rem; color:#777; min-height:2.6em;'>{mode['tagline']}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown('<div class="mode-btn">', unsafe_allow_html=True)
                if st.button("Choose", key=f"pick_{key}", use_container_width=True):
                    st.session_state.mode_key = key
                    st.session_state.messages = [SystemMessage(content=mode["system"])]
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Screen 2 — Chat
# ---------------------------------------------------------------------------
def render_chat():
    mode = MODES[st.session_state.mode_key]
    inject_css(mode)

    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.9)

    top_left, top_right = st.columns([4, 1])
    with top_left:
        st.markdown(
            f'<div class="active-banner">{mode["emoji"]} {mode["label"]} mode is live</div>',
            unsafe_allow_html=True,
        )
    with top_right:
        if st.button("🔄 Switch mood", use_container_width=True):
            st.session_state.mode_key = None
            st.session_state.messages = []
            st.rerun()

    # Render chat history (skip the SystemMessage)
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.markdown(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant", avatar=mode["emoji"]):
                st.markdown(msg.content)

    prompt = st.chat_input("Type your message here...")
    if prompt:
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=mode["emoji"]):
            with st.spinner("Thinking..."):
                res = llm.invoke(st.session_state.messages)
                st.markdown(res.content)

        st.session_state.messages.append(AIMessage(content=res.content))


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
if st.session_state.mode_key is None:
    render_mode_picker()
else:
    render_chat()