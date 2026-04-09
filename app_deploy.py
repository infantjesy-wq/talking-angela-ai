import streamlit as st
from gtts import gTTS
from io import BytesIO
import time
import requests

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
# SHOW AVATAR
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
# TEXT INPUT
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

    # Typing effect
    with st.spinner("🐱 Angela is typing..."):
        time.sleep(1)

    # -------------------------------
    # AI RESPONSE (NO API KEY)
    # -------------------------------
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/google/flan-t5-large",
            json={"inputs": text},
        )

        result = response.json()

        if isinstance(result, list):
            reply = result[0]["generated_text"]
        else:
            reply = "Sorry, I couldn't respond right now."

    except:
        reply = "Error connecting to AI service."

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
    # VOICE OUTPUT
    # -------------------------------
    tts = gTTS(text=reply, lang='en')

    st.session_state.latest_audio = None

    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)

    st.session_state.latest_audio = audio_buffer.read()

    time.sleep(1)

    st.rerun()