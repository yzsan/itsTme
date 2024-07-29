from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///activities.db'
db = SQLAlchemy(app)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    last_done = db.Column(db.DateTime, nullable=False)

@app.route('/')
def index():
    activities = Activity.query.order_by(Activity.last_done).all()
    return render_template('index.html', activities=activities)

@app.route('/add', methods=['GET', 'POST'])
def add_activity():
    if request.method == 'POST':
        name = request.form['name']
        details = request.form['details']
        last_done = datetime.strptime(request.form['last_done'], '%Y-%m-%dT%H:%M')
        new_activity = Activity(name=name, details=details, last_done=last_done)
        db.session.add(new_activity)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_activity.html')

if __name__ == "__main__":
    app.run(debug=True)
