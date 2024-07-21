from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///activities.db'
db = SQLAlchemy(app)

JST = pytz.timezone('Asia/Tokyo')

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    last_done = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.String(500), nullable=True)

@app.route('/')
def index():
    activities = Activity.query.all()
    for activity in activities:
        if activity.last_done.tzinfo is None:
            activity.last_done = pytz.utc.localize(activity.last_done)
        print(f"Before: {activity.last_done}")
        activity.last_done = activity.last_done.astimezone(JST)
        print(f"After: {activity.last_done}")
    return render_template('index.html', activities=activities)

@app.route('/add', methods=['GET', 'POST'])
def add_activity():
    if request.method == 'POST':
        name = request.form.get('name')
        details = request.form.get('details')
        new_activity = Activity(name=name, details=details)
        db.session.add(new_activity)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_activity.html')

@app.route('/activity/<int:id>')
def activity_detail(id):
    activity = Activity.query.get(id)
    if activity.last_done.tzinfo is None:
        activity.last_done = pytz.utc.localize(activity.last_done)
    print(f"Before: {activity.last_done}")
    activity.last_done = activity.last_done.astimezone(JST)
    print(f"After: {activity.last_done}")
    return render_template('activity_detail.html', activity=activity)

@app.route('/update/<int:id>', methods=['POST'])
def update_activity(id):
    activity = Activity.query.get(id)
    if activity.last_done.tzinfo is None:
        activity.last_done = pytz.utc.localize(activity.last_done)
    activity.last_done = datetime.now(pytz.utc).astimezone(JST)
    print(f"Updated datetime: {activity.last_done}")  # 追加
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
