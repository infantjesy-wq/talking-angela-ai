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
# SMART FALLBACK RESPONSE
# -------------------------------
def smart_reply(text, emotion):
    if emotion == "sad":
        return "I'm here for you 💙 Tell me what happened."
    elif emotion == "angry":
        return "I understand you're upset. Let's take it easy 😊"
    elif emotion == "happy":
        return "That's great to hear! 😄"
    else:
        return f"You said: {text}"

# -------------------------------
# AVATAR MAP
# -------------------------------
avatar_map = {
    "happy": "happy.gif",
    "sad": "sad.gif",
    "angry": "angry.gif",
    "neutral": "avatar.gif",
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
    # AI RESPONSE (TRY API)
    # -------------------------------
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
            json={"inputs": text},
            timeout=5
        )

        result = response.json()

        if isinstance(result, list) and "generated_text" in result[0]:
            reply = result[0]["generated_text"]
        else:
            reply = smart_reply(text, emotion)

    except:
        reply = smart_reply(text, emotion)

    # Save assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

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