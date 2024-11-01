from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key for sessions

# In-memory storage for users, alarms, and reminders
users = {}
alarms = {}
reminders = {}

# Demotivational Quotes List
quotes = [
    "The future is bright, but your future is a bit dim.",
    "Every time you open your mouth, you make me want to stop talking.",
    "You're unique, just like everyone else.",
    "Success is not the key to happiness. Happiness is the key to success. If you love what you are doing, you will be happy.",
    "Your life is your own. You can make it a mess if you want."
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
        return render_template('home.html', username=session['username'], quote=random_quote)
    return redirect(url_for('login'))

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Wakeup Alarm functionality route
@app.route('/wakeup_alarm', methods=['GET', 'POST'])
def wakeup_alarm():
    if 'username' in session:
        if request.method == 'POST':
            alarm_time = request.form['alarm_time']
            alarms[session['username']] = alarm_time  # Saving the alarm to user-specific dictionary
            flash(f'Alarm set for {alarm_time}')
        return render_template('wakeup_alarm.html')
    return redirect(url_for('login'))

# Assignment Submission functionality route
@app.route('/assignment_submission', methods=['GET', 'POST'])
def assignment_submission():
    if 'username' in session:
        if request.method == 'POST':
            assignment = request.form['assignment']
            flash(f'Assignment "{assignment}" submitted!')
        return render_template('assignment_submission.html')
    return redirect(url_for('login'))

# Record Submission functionality route
@app.route('/record_submission', methods=['GET', 'POST'])
def record_submission():
    if 'username' in session:
        if request.method == 'POST':
            record = request.form['record']
            flash(f'Record "{record}" submitted!')
        return render_template('record_submission.html')
    return redirect(url_for('login'))

# Workout Reminder functionality route
@app.route('/workout_reminder', methods=['GET', 'POST'])
def workout_reminder():
    if 'username' in session:
        if request.method == 'POST':
            reminder = request.form['reminder']
            reminders[session['username']] = reminder  # Saving the reminder
            flash('Workout reminder set!')
        return render_template('workout_reminder.html')
    return redirect(url_for('login'))

# Study Timetable Setting functionality route
@app.route('/study_timetable', methods=['GET', 'POST'])
def study_timetable():
    if 'username' in session:
        if request.method == 'POST':
            timetable = request.form['timetable']
            flash('Study timetable saved!')
        return render_template('study_timetable.html')
    return redirect(url_for('login'))

# Exam Reminder functionality route
@app.route('/exam_reminder', methods=['GET', 'POST'])
def exam_reminder():
    if 'username' in session:
        if request.method == 'POST':
            exam = request.form['exam']
            flash('Exam reminder set!')
        return render_template('exam_reminder.html')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
