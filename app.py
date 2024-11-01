from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import random
import datetime
import time
from threading import Thread
import pygame

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key for sessions

# In-memory storage for users, alarms, reminders, and assignments
users = {}
alarms = {}
reminders = {}
assignments = {}  # Store assignments with their due dates and procrastination thoughts
alarm_ringing = False  # To track if the alarm is currently ringing
records = {} 

# Demotivational Quotes List
quotes = [
    "The future is bright, but your future is a bit dim.",
    "Every time you open your mouth, you make me want to stop talking.",
    "You're unique, just like everyone else.",
    "Success is not the key to happiness. Happiness is the key to success. If you love what you are doing, you will be happy.",
    "Your life is your own. You can make it a mess if you want."
]

# Procrastination Thoughts for each assignment
procrastination_thoughts = [
    "Why do today what you can put off until tomorrow?",
    "Procrastination is the art of keeping up with yesterday.",
    "If it weren’t for the last minute, nothing would get done.",
    "You can’t finish your homework if you don’t start.",
    "Maybe you should just watch some more TV instead."
]

record_procrastination_thoughts = [
    "Why start now when you can do it later?",
    "It's just a record; no one will notice if it's late.",
    "This record can wait. I have more important things to ignore.",
    "There's always tomorrow... or next week.",
    "You don't really need to submit this, do you?"
]

exam_procrastination_thoughts = [
    "Why study today when I can cram all night before the exam?",
    "I'll start studying after I finish this episode... or maybe the next season.",
    "Who needs sleep when there's YouTube to watch?",
    "I can totally pass without studying; I have good luck.",
    "There's always tomorrow to prepare; today is for relaxing.",
    "I need to organize my notes first. Let me spend an hour doing that.",
    "Studying is overrated; I can just wing it.",
    "Maybe if I stare at the book long enough, the information will just sink in.",
    "I’ll just take a quick nap first. I’ll feel more refreshed to study after.",
    "Why not scroll through social media instead of studying? It’s so much more fun!",
]


# Load users data from a JSON file (if it exists)
def load_data():
    global users
    try:
        with open('data.json', 'r') as f:
            content = f.read().strip()
            if content:
                users = json.loads(content).get('users', {})
    except FileNotFoundError:
        print("data.json not found. Initializing empty users data.")
    except json.JSONDecodeError:
        print("JSON format error in data.json. Initializing empty users data.")

# Save user data to JSON file
def save_data():
    with open('data.json', 'w') as f:
        json.dump({'users': users}, f)

# Load data on start
load_data()

@app.route('/')
def index():
    return redirect(url_for('login'))

# Login route with credential verification
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.get(username) == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!')
    return render_template('login.html')

# Registration route with credential saving
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Username already exists!')
        else:
            users[username] = password
            save_data()
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
    return render_template('register.html')

# Home route displaying a random demotivational quote
@app.route('/home')
def home():
    if 'username' in session:
        random_quote = random.choice(quotes)
        return render_template('home.html', username=session['username'], quote=random_quote, alarm_ringing=alarm_ringing)
    return redirect(url_for('login'))

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Wakeup Alarm functionality route
@app.route('/wakeup_alarm', methods=['GET', 'POST'])
def wakeup_alarm():
    global alarm_ringing
    if 'username' in session:
        if request.method == 'POST':
            # Generate a random alarm time within the next hour
            current_time = datetime.datetime.now()
            random_minutes = random.randint(1, 59)  # Random number of minutes between 1 and 59
            random_alarm_time = (current_time + datetime.timedelta(minutes=random_minutes)).strftime("%H:%M")

            alarms[session['username']] = random_alarm_time  # Saving the alarm to user-specific dictionary
            flash(f'Alarm randomly set for {random_alarm_time}')  # Notify user of the random alarm time

            # Start the alarm thread
            alarm_thread = Thread(target=alarm, args=(random_alarm_time,))
            alarm_thread.start()  # Start the alarm in a separate thread
            
            return render_template('wakeup_alarm.html', alarm_ringing=alarm_ringing, alarm_time=random_alarm_time)

        # If the user is accessing the page via GET, retrieve the set alarm time
        alarm_time = alarms.get(session['username'])  # Get the current alarm time if set

        return render_template('wakeup_alarm.html', alarm_ringing=alarm_ringing, alarm_time=alarm_time)

    return redirect(url_for('login'))


# Updated alarm function for easier debugging and minute-level match
# Updated alarm function for easier debugging and minute-level match
def alarm(set_alarm_time):
    global alarm_ringing
    print(f"Alarm set for: {set_alarm_time}")  # For debugging
    while True:
        time.sleep(1)  # Check every second
        current_time = datetime.datetime.now().strftime("%H:%M")  # Adjusted to check only hours and minutes
        print(f"Current time: {current_time}")  # For debugging

        if current_time == set_alarm_time:  # Compare only hours and minutes
            alarm_ringing = True
            print("Useless Alarm! Time to do nothing!")
            play_alarm_sound()  # Play alarm sound
            break


# Play alarm sound function
def play_alarm_sound():
    pygame.mixer.init()
    pygame.mixer.music.load("static/alarm_sound.mp3")  # Load your mp3 file
    pygame.mixer.music.play(-1)  # Play the sound indefinitely

# Stop the alarm functionality route
@app.route('/stop_alarm', methods=['POST'])
def stop_alarm():
    global alarm_ringing
    pygame.mixer.music.stop()  # Stop the alarm sound
    alarm_ringing = False  # Reset alarm status
    flash('Alarm stopped!')  # Notify user that alarm is stopped
    return redirect(url_for('home'))  # Redirect to home page

# Assignment Submission functionality route
@app.route('/assignment_submission', methods=['GET', 'POST'])
def assignment_submission():
    global assignments
    if 'username' in session:
        if request.method == 'POST':
            assignment = request.form['assignment']
            due_date = request.form['due_date']
            due_time = request.form['due_time']
            due_datetime = f"{due_date} {due_time}"

            # Store the assignment with due date and a random procrastination thought
            procrastination_thought = random.choice(procrastination_thoughts)
            assignments[session['username']] = assignments.get(session['username'], [])
            assignments[session['username']].append({
                'assignment': assignment,
                'due_datetime': due_datetime,
                'procrastination_thought': procrastination_thought
            })
            flash(f'Assignment "{assignment}" with due date "{due_datetime}" submitted!')

        # Get the assignments for the logged-in user
        user_assignments = assignments.get(session['username'], [])
        
        # Calculate remaining time for each assignment
        for assignment in user_assignments:
            due_time = datetime.datetime.strptime(assignment['due_datetime'], "%Y-%m-%d %H:%M")
            remaining_time = due_time - datetime.datetime.now()
            assignment['remaining_time'] = str(remaining_time).split('.')[0]  # Format as "HH:MM:SS"
        
        return render_template('assignment_submission.html', alarm_ringing=alarm_ringing, assignments=user_assignments)
    
    return redirect(url_for('login'))

# Record Submission functionality route
@app.route('/record_submission', methods=['GET', 'POST'])
def record_submission():
    global reminders
    if 'username' in session:
        if request.method == 'POST':
            record = request.form['record']
            due_datetime = request.form['due_datetime']  # Updated to match single datetime-local input

            # Store the record with due date and a random procrastination thought
            procrastination_thought = random.choice(record_procrastination_thoughts)
            reminders[session['username']] = reminders.get(session['username'], [])
            reminders[session['username']].append({
                'record': record,
                'due_datetime': due_datetime,
                'procrastination_thought': procrastination_thought
            })
            flash(f'Record "{record}" with due date "{due_datetime}" submitted!')

        # Get the records for the logged-in user
        user_records = reminders.get(session['username'], [])
        return render_template('record_submission.html', alarm_ringing=alarm_ringing, records=user_records)

    return redirect(url_for('login'))

# Workout Reminder functionality route
@app.route('/workout_reminder', methods=['GET', 'POST'])
def workout_reminder():
    if 'username' in session:
        if request.method == 'POST':
            reminder = request.form['reminder']
            reminders[session['username']] = reminder  # Saving the reminder
            flash('Workout reminder set!')
        return render_template('workout_reminder.html', alarm_ringing=alarm_ringing)
    return redirect(url_for('login'))

# Study Timetable Setting functionality route
@app.route('/study_timetable', methods=['GET', 'POST'])
def study_timetable():
    if 'username' in session:
        if request.method == 'POST':
            timetable = request.form['timetable']
            flash('Study timetable saved!')
        return render_template('study_timetable.html', alarm_ringing=alarm_ringing)
    return redirect(url_for('login'))

@app.route('/exam_reminder', methods=['GET', 'POST'])
def exam_reminder():
    global reminders
    if 'username' in session:
        if request.method == 'POST':
            exam = request.form['exam']
            due_datetime = request.form['due_datetime']

            # Store the exam with due date and a random procrastination thought
            procrastination_thought = random.choice(exam_procrastination_thoughts)
            reminders[session['username']] = reminders.get(session['username'], [])
            reminders[session['username']].append({
                'exam': exam,
                'due_datetime': due_datetime,
                'procrastination_thought': procrastination_thought
            })
            flash(f'Exam "{exam}" with due date "{due_datetime}" submitted!')

        # Get the exams for the logged-in user
        user_exams = reminders.get(session['username'], [])
        return render_template('exam_reminder.html', alarm_ringing=alarm_ringing, exams=user_exams)

    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
