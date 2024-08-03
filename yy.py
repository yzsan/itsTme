from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz  # 追加(TIME)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///activities.db'
db = SQLAlchemy(app)

JST = pytz.timezone('Asia/Tokyo')  # 追加(TIME)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    last_done = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.String(500), nullable=True)
    updates = db.relationship('Update', backref='activity', lazy=True, cascade="all, delete-orphan")

class Update(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    note = db.Column(db.String(500), nullable=True)

@app.route('/')
def index():
    # 現在の日付を取得
    today = datetime.today().date()

    # アクティビティとその経過日数を取得
    activities = Activity.query.all()
    activity_with_days_passed = [
        {
            'id': activity.id,
            'name': activity.name,
            'date': activity.date,
            'days_passed': (today - activity.date).days
        } for activity in activities
    ]

    # 経過日数の多い順にソート
    sorted_activities = sorted(activity_with_days_passed, key=lambda activity: activity['days_passed'], reverse=True)

    return render_template('index.html', activities=sorted_activities)

@app.route('/add', methods=['GET', 'POST'])
def add_activity():
    if request.method == 'POST':
        name = request.form.get('name')
        details = request.form.get('details')
        new_activity = Activity(name=name, details=details)

        db.session.add(new_activity)
        db.session.commit()
        return redirect(url_for('index'))  # 抜けていたので修正
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
