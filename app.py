import streamlit as st
from gtts import gTTS
import speech_recognition as sr
import time
from openai import OpenAI
from io import BytesIO

# -------------------------------
# API SETUP
# -------------------------------
client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

st.set_page_config(page_title="Talking Angela AI", layout="centered")

st.title("🐱 Talking Angela AI")

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
# AUDIO PLAYER (FIXED)
# -------------------------------
if st.session_state.latest_audio:
    st.markdown("### 🔊 Angela Voice")
    st.audio(st.session_state.latest_audio, format="audio/mp3")

# -------------------------------
# VOICE INPUT BUTTON
# -------------------------------
if st.button("🎤 Talk to me"):

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        st.info("🎤 Speak now...")

        try:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)

            text = recognizer.recognize_google(audio)

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
            # VOICE OUTPUT (FIXED)
            # -------------------------------
            tts = gTTS(text=reply, lang='en', tld='co.in')

            # CLEAR old audio
            st.session_state.latest_audio = None

            # STORE in memory (NO FILE → NO BUG)
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            st.session_state.latest_audio = audio_buffer.read()

            time.sleep(1)

            st.rerun()

        except sr.WaitTimeoutError:
            st.warning("⏱️ You didn’t speak in time")

        except sr.UnknownValueError:
            st.warning("😕 Couldn't understand")

        except Exception as e:
            st.error(f"Error: {str(e)}")