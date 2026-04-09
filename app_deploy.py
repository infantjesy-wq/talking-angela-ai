import streamlit as st
from gtts import gTTS
from openai import OpenAI
from io import BytesIO
import time

# -------------------------------
# API SETUP
# -------------------------------
client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://infantjesy-wq/talking-angela-ai.streamlit.app",  # REQUIRED
        "X-Title": "Talking Angela AI"  # REQUIRED
    }
)

st.set_page_config(page_title="Talking Angela AI", layout="centered")

st.title("🐱 Talking Angela AI (Web Version)")

# -------------------------------
# SESSION STATE
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "latest_audio" not in st.session_state:
    st.session_state.latest_audio = None

if "emotion" not in st.session_state:
    st.session_state.emotion = "neutral"

# -------------------------------
# EMOTION DETECTION
# -------------------------------
def detect_emotion(text):
    text = text.lower()

    if any(word in text for word in ["sad", "cry", "depressed"]):
        return "sad"
    elif any(word in text for word in ["angry", "mad", "hate"]):
        return "angry"
    elif any(word in text for word in ["happy", "great", "good", "nice"]):
        return "happy"
    else:
        return "neutral"

# -------------------------------
# AVATAR MAP
# -------------------------------
avatar_map = {
    "happy": "happy.gif",
    "sad": "sad.gif",
    "angry": "angry.gif",
    "neutral": "avatar.gif",
    "talking": "talking.gif"
}

# -------------------------------
# SHOW AVATAR (CENTER)
# -------------------------------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image(avatar_map.get(st.session_state.emotion, "avatar.gif"), width=200)

# -------------------------------
# CHAT DISPLAY
# -------------------------------
st.subheader("💬 Chat")

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"🧑 **You:** {msg['content']}")
    else:
        st.markdown(f"🐱 **Angela:** {msg['content']}")

# -------------------------------
# AUDIO PLAYER
# -------------------------------
if st.session_state.latest_audio:
    st.markdown("### 🔊 Angela Voice")
    st.audio(st.session_state.latest_audio, format="audio/mp3")

# -------------------------------
# TEXT INPUT (DEPLOY SAFE)
# -------------------------------
user_input = st.text_input("Type your message")

if st.button("Send") and user_input:

    text = user_input

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": text
    })

    # Detect emotion
    emotion = detect_emotion(text)
    st.session_state.emotion = emotion

    # Typing animation
    with st.spinner("🐱 Angela is typing..."):
        time.sleep(1)

    # -------------------------------
    # REAL AI RESPONSE
    # -------------------------------
    system_prompt = f"""
    You are a cute talking assistant like Angela.
    User emotion is: {emotion}

    Respond accordingly:
    - If sad → be supportive
    - If angry → calm politely
    - If happy → be cheerful
    - Keep responses short
    """

    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    )

    reply = response.choices[0].message.content

    # Save assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    # -------------------------------
    # TALKING ANIMATION
    # -------------------------------
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("talking.gif", width=200)

    # -------------------------------
    # VOICE OUTPUT (NO OVERLAP)
    # -------------------------------
    tts = gTTS(text=reply, lang='en', tld='co.in')

    st.session_state.latest_audio = None

    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)

    st.session_state.latest_audio = audio_buffer.read()

    time.sleep(1)

    st.rerun()