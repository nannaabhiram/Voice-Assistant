def show_tasks(db):
    cursor = db.cursor()
    cursor.execute("SELECT id, title, status, due_date FROM tasks ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    print("\n--- Tasks ---")
    print(f"{'ID':<5} {'Title':<30} {'Status':<10} {'Due Date':<20}")
    print("-"*70)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<30} {row[2]:<10} {str(row[3]):<20}")
    if not rows:
        print("No tasks found.")

def show_reminders(db):
    cursor = db.cursor()
    cursor.execute("SELECT id, message, remind_at, is_done FROM reminders ORDER BY remind_at DESC LIMIT 20")
    rows = cursor.fetchall()
    print("\n--- Reminders ---")
    print(f"{'ID':<5} {'Message':<30} {'Remind At':<20} {'Is Done':<10}")
    print("-"*80)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<30} {str(row[2]):<20} {row[3]:<10}")
    if not rows:
        print("No reminders found.")

def show_conversations(db):
    cursor = db.cursor()
    cursor.execute("SELECT id, user_input, assistant_response, timestamp FROM conversations ORDER BY timestamp DESC LIMIT 20")
    rows = cursor.fetchall()
    print("\n--- Conversations ---")
    print(f"{'ID':<5} {'User Input':<30} {'Assistant Response':<30} {'Timestamp':<20}")
    print("-"*110)
    for row in rows:
        print(f"{row[0]:<5} {row[1][:28]:<30} {row[2][:28]:<30} {str(row[3]):<20}")
    if not rows:
        print("No conversations found.")
import os
import time
import pyttsx3
import re
import datetime
from dotenv import load_dotenv

# Local imports
from speech.stt import listen_voice
from ai.brain import ask_ai
from system.control import run_system_command
from db.db_connection import get_db_connection, save_conversation, save_task

def delete_task(db, identifier):
    cursor = db.cursor()
    # Try to delete by ID first
    try:
        cursor.execute("DELETE FROM tasks WHERE id = %s", (identifier,))
        if cursor.rowcount == 0:
            # If not found by ID, try by title
            cursor.execute("DELETE FROM tasks WHERE title = %s", (identifier,))
        db.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error deleting task: {e}")
        return False

def delete_reminder(db, identifier):
    cursor = db.cursor()
    # Try to delete by ID first
    try:
        cursor.execute("DELETE FROM reminders WHERE id = %s", (identifier,))
        if cursor.rowcount == 0:
            # If not found by ID, try by message
            cursor.execute("DELETE FROM reminders WHERE message = %s", (identifier,))
        db.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error deleting reminder: {e}")
        return False

def fetch_conversation_history(db, limit=10):
    cursor = db.cursor()
    cursor.execute("SELECT user_input, assistant_response, timestamp FROM conversations ORDER BY timestamp DESC LIMIT %s", (limit,))
    return cursor.fetchall()

# Load environment variables
load_dotenv()

# Initialize text-to-speech
engine = pyttsx3.init()

def speak(text):
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def get_user_input(mode="cli"):
    if mode == "voice":
        return listen_voice()
    else:
        return input("You: ")

def save_reminder(db, text, remind_time):
    cursor = db.cursor()
    cursor.execute("INSERT INTO reminders (message, remind_at) VALUES (%s, %s)", (text, remind_time))
    db.commit()

def check_reminders(db):
    while True:
        now = datetime.datetime.now().replace(second=0, microsecond=0)
        cursor = db.cursor()
        cursor.execute("SELECT id, message, remind_at FROM reminders WHERE remind_at <= %s AND is_done = 0", (now,))
        for rid, message, remind_at in cursor.fetchall():
            speak(f"**Reminder:** {message} (scheduled for {remind_at})")
            cursor.execute("UPDATE reminders SET is_done = 1 WHERE id = %s", (rid,))
            db.commit()
        time.sleep(60)

def parse_reminder(user_input):
    match = re.match(r"remind me to (.+) at (\d{1,2})(:(\d{2}))? ?(am|pm)?", user_input, re.I)
    if match:
        text = match.group(1)
        hour = int(match.group(2))
        minute = int(match.group(4) or 0)
        ampm = match.group(5)
        now = datetime.datetime.now()
        if ampm:
            if ampm.lower() == "pm" and hour < 12:
                hour += 12
            elif ampm.lower() == "am" and hour == 12:
                hour = 0
        remind_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if remind_time < now:
            remind_time += datetime.timedelta(days=1)
        return text, remind_time

    # Support 'after <hour>(am|pm)'
    match_after = re.match(r"remind me to (.+) after (\d{1,2}) ?(am|pm)?", user_input, re.I)
    if match_after:
        text = match_after.group(1)
        hour = int(match_after.group(2))
        ampm = match_after.group(3)
        now = datetime.datetime.now()
        if ampm:
            if ampm.lower() == "pm" and hour < 12:
                hour += 12
            elif ampm.lower() == "am" and hour == 12:
                hour = 0
        remind_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if remind_time < now:
            remind_time += datetime.timedelta(days=1)
        # Set reminder 30 minutes after the specified hour
        remind_time += datetime.timedelta(minutes=30)
        return text, remind_time

    return None, None

def main():
    # Connect to MySQL
    db = get_db_connection()
    if not db:
        print("❌ Database connection failed. Exiting.")
        return
    
    speak("Hello! Your offline AI assistant is ready.")
    
    # Choose input mode
    mode = input("Choose mode (cli/voice): ").strip().lower()
    if mode not in ["cli", "voice"]:
        mode = "cli"
        
        
    while True:
        try:
            user_input = get_user_input(mode)
            
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                speak("Goodbye!")
                break
            
            # Decide action
            if user_input.lower() == "show tasks":
                show_tasks(db)
            elif user_input.lower() == "show reminders":
                show_reminders(db)
            elif user_input.lower() == "show conversations":
                show_conversations(db)
            if user_input.lower() == "show history":
                history = fetch_conversation_history(db)
                if history:
                    print("\n--- Conversation History ---")
                    for user, assistant, ts in reversed(history):
                        print(f"[{ts}] You: {user}")
                        print(f"[{ts}] Assistant: {assistant}\n")
                else:
                    print("No previous conversations found.")
            elif user_input.startswith("run "):
                result = run_system_command(user_input[4:])
                speak(result)
            elif user_input.startswith("add task "):
                task = user_input[9:]
                save_task(db, task)
                speak(f"Task '{task}' added.")

            elif user_input.lower().startswith("delete task "):
                identifier = user_input[12:].strip()
                success = delete_task(db, identifier)
                if success:
                    speak(f"Task '{identifier}' deleted.")
                else:
                    speak(f"Task '{identifier}' not found.")

            elif user_input.lower().startswith("delete reminder "):
                identifier = user_input[16:].strip()
                success = delete_reminder(db, identifier)
                if success:
                    speak(f"Reminder '{identifier}' deleted.")
                else:
                    speak(f"Reminder '{identifier}' not found.")
            elif user_input.lower().startswith("remind me to"):
                text, remind_time = parse_reminder(user_input)
                if text and remind_time:
                    save_reminder(db, text, remind_time)
                    speak(f"Reminder saved for {remind_time.strftime('%I:%M %p')}: {text}")
                else:
                    speak("Sorry, I couldn't understand the reminder time.")
            else:
                response = ask_ai(user_input)
                speak(response)
                save_conversation(db, user_input, response)
        
        except KeyboardInterrupt:
            speak("Goodbye!")
            break
        except Exception as e:
            print("⚠️ Error:", e)
            speak("Something went wrong.")
            time.sleep(1)

if __name__ == "__main__":
    main()
