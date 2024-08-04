from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Flask-Migrateを追加
from datetime import datetime, timedelta
import pytz

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

# Flaskアプリケーションの設定
app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # マイグレーションの設定
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

# モデルのインポート
from models import User, Activity, Update

# ユーザー認証の設定
login_manager.login_view = 'login'

JST = pytz.timezone('Asia/Tokyo')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Check username and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/')
@login_required
def index():
    activities = Activity.query.filter_by(user_id=current_user.id).all()
    current_time = datetime.now(pytz.utc).astimezone(JST)
    activities_with_elapsed = []
    for activity in activities:
        if activity.last_done.tzinfo is None:
            activity.last_done = pytz.utc.localize(activity.last_done)
        activity.last_done = activity.last_done.astimezone(JST)
        elapsed_days = (current_time - activity.last_done).days
        activities_with_elapsed.append({
            'activity': activity,
            'elapsed_days': elapsed_days
        })
    sorted_activities = sorted(activities_with_elapsed, key=lambda activity: activity['elapsed_days'], reverse=True)
    return render_template('index.html', activities=sorted_activities)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_activity():
    if request.method == 'POST':
        name = request.form.get('name')
        details = request.form.get('details')
        last_done = datetime.strptime(request.form['last_done'], '%Y-%m-%dT%H:%M')
        last_done = JST.localize(last_done)
        last_done = last_done.astimezone(pytz.utc)
        new_activity = Activity(name=name, details=details, last_done=last_done, user_id=current_user.id)
        db.session.add(new_activity)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_activity.html')

@app.route('/activity/<int:id>')
def activity_detail(id):
    activity = Activity.query.get(id)
    if activity.last_done.tzinfo is None:
        activity.last_done = pytz.utc.localize(activity.last_done)
    activity.last_done = activity.last_done.astimezone(JST)
    updates = Update.query.filter_by(activity_id=id).order_by(Update.timestamp.desc()).all()
    for update in updates:
        if update.timestamp.tzinfo is None:
            update.timestamp = pytz.utc.localize(update.timestamp)
        update.timestamp = update.timestamp.astimezone(JST)
    return render_template('activity_detail.html', activity=activity, updates=updates)

@app.route('/update/<int:id>', methods=['POST'])
def update_activity(id):
    activity = Activity.query.get(id)
    note = request.form.get('note')
    new_update = Update(activity_id=id, note=note)
    activity.last_done = datetime.utcnow()
    db.session.add(new_update)
    db.session.commit()
    return redirect(url_for('activity_detail', id=id))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_activity(id):
    activity = Activity.query.get(id)
    db.session.delete(activity)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


# if __name__ == '__main__':
#     app.run(debug=True)