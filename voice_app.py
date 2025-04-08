#importing necessary libraries
import streamlit as st
import speech_recognition as sr
import pyttsx3
import webbrowser
import schedule
import time
import smtplib
import datetime
from googlesearch import search
from plyer import notification

# Initialize Streamlit
st.title("Voice Assistant with Web Search & Reminders")

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to recognize speech
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            return text.lower()
        except sr.UnknownValueError:
            st.write("Could not understand. Try again.")
            return None
        except sr.RequestError:
            st.write("Network error.")
            return None

# Function to search the web
def search_web(query):
    st.write(f"Searching for: {query}")
    if  query:
        query = query.strip()
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        speak(f"Searching Google for {query}.")
        st.success("Opened the search results in your browser.")
        return

# Function to send email (update with your credentials)
def send_email(subject, body, recipient_email="faustinah.tubo1@gmail.com"):
    sender_email = "faustinah.tubo1@gmail.com"
    sender_password = "sygy jmxn ifwg mxwi"

    message = f"Subject: {subject}\n\n{body}"
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message)
        server.quit()
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Function to schedule a reminder
def schedule_reminder(event, event_time):
    now = datetime.datetime.now()
    reminder_time = datetime.datetime.strptime(event_time, "%I:%M %p") - datetime.timedelta(minutes=30)

    if now.time() > reminder_time.time():
        st.error("Cannot set a reminder for a past time.")
        return

    def notify():
        notification.notify(
            title="Reminder!",
            message=f"Upcoming event: {event} in 30 minutes.",
            timeout=10
        )
        speak(f"Reminder! {event} is in 30 minutes.")
    
    schedule.every().day.at(reminder_time.strftime("%H:%M")).do(notify)
    st.success(f"Reminder for {event} set at {event_time}. You will be notified 30 minutes before.")

    send_email("Reminder Notification", f"Upcoming event: {event} at {event_time}")

# Streamlit UI
st.subheader("Web Search")
if st.button("Start Voice Search"):
    query = recognize_speech()
    if query:
        search_web(query)

# Initialize session_state to avoid KeyError
if "reminder_list" not in st.session_state:
    st.session_state.reminder_list = []  # Store reminders here

st.subheader("Schedule a Meeting / Reminder")
event = st.text_input("Event Name")
event_time = st.text_input("Event Time (e.g., 3:30 PM)")

if st.button("Set Reminder"):
    if event and event_time:
        # Store reminder in session_state
        st.session_state.reminder_list.append((event, event_time))
        schedule_reminder(event, event_time)
    else:
        st.error("Please enter both event name and time.")

# Run scheduled tasks in the background
while True:
    schedule.run_pending()
    time.sleep(1)
