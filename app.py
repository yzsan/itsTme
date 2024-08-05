from flask import Flask, render_template, request, redirect, url_for, flash  # * flashの追加
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # ** Flask-Migrateを追加
from datetime import datetime, timedelta
import pytz  ### 追加(TIME)

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

# Flaskアプリケーションの設定
# app = Flask(__name__)
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///activities.db'
# # app.config['SECRET_KEY'] = 'your_secret_key'  # *
# app.config.from_object('config.Config')  # * config.pyから上の2行をインポート

# db = SQLAlchemy(app)
# # db = SQLAlchemy()  # **
# # db.init_app(app)  # ** # appをdbに渡して初期化
# migrate = Migrate(app, db)  # ** マイグレーションの設定 
# login_manager = LoginManager(app)  # *
# bcrypt = Bcrypt(app)  # *

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'login'

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    migrate = Migrate(app, db)  # 追加

    with app.app_context():
        # from .models import User, Activity, Update  # ここでインポート
        from models import User, Activity, Update  # 相対インポートを絶対インポートに変更
        db.create_all()

    # from .routes import main as main_blueprint
    from routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

app = create_app()

# # モデルのインポート
# from models import User, Activity, Update

# # ユーザー認証の設定
# login_manager.login_view = 'login'  # *

JST = pytz.timezone('Asia/Tokyo')  ### 追加(TIME)

# class Activity(db.Model):  ## not db.model
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(200), nullable=False)
#     last_done = db.Column(db.DateTime, default=datetime.utcnow)
#     details = db.Column(db.String(500), nullable=True)
#     updates = db.relationship('Update', backref='activity', lazy=True, cascade="all, delete-orphan")

# class Update(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)
#     note = db.Column(db.String(500), nullable=True)

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))



# @app.route('/login', methods=['GET', 'POST'])  # *
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = User.query.filter_by(username=username).first()
#         if user and bcrypt.check_password_hash(user.password, password):
#             login_user(user)
#             return redirect(url_for('index'))
#         else:
#             flash('Login Unsuccessful. Check username and password', 'danger')
#     return render_template('login.html')

# @app.route('/logout')  # *
# def logout():
#     logout_user()
#     return redirect(url_for('index'))

# @app.route('/register', methods=['GET', 'POST'])  # *
# def register():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
#         new_user = User(username=username, password=hashed_password)
#         db.session.add(new_user)
#         db.session.commit()
#         return redirect(url_for('login'))
#     return render_template('register.html')

# @app.route('/')
# @login_required  # *
# def index():
#     # activities = Activity.query.all()
#     activities = Activity.query.filter_by(user_id=current_user.id).all()  # *
#     current_time = datetime.now(pytz.utc).astimezone(JST)
#     activities_with_elapsed = []
#     for activity in activities:
#         if activity.last_done.tzinfo is None:
#             activity.last_done = pytz.utc.localize(activity.last_done)
#         activity.last_done = activity.last_done.astimezone(JST)  ## この1行でUTCからJST表示
#         elapsed_days = (current_time - activity.last_done).days
#         activities_with_elapsed.append({
#             'activity': activity,
#             'elapsed_days': elapsed_days
#         })


#     # 経過日数の多い順にソート
#     sorted_activities = sorted(activities_with_elapsed, key=lambda activity: activity['elapsed_days'], reverse=True)
#     return render_template('index.html', activities=sorted_activities)

    


# @app.route('/add', methods=['GET', 'POST'])
# @login_required  # ** migration修正の際に追加
# def add_activity():
#     if request.method == 'POST':
#         # name = request.form.get('details')  ## これ1行だけだったので修正
#         name = request.form.get('name')
#         details = request.form.get('details')
#         # new_activity = Activity(name=name)  ## これを修正
#         last_done = datetime.strptime(request.form['last_done'], '%Y-%m-%dT%H:%M')
#         last_done = JST.localize(last_done)  ## 強制追加
#         last_done = last_done.astimezone(pytz.utc)  ## 強制追加
#         new_activity = Activity(name=name, details=details, last_done=last_done, user_id=current_user.id)  # ** migration修正の際にuser_id記載を追加

#         db.session.add(new_activity)
#         db.session.commit()
#         return redirect(url_for('index'))  ## 抜けていたので修正
#     return render_template('add_activity.html')

# @app.route('/activity/<int:id>')  ## ここからの4行が抜けていたので追加
# def activity_detail(id):
#     activity = Activity.query.get(id)
#     if activity.last_done.tzinfo is None:  #### 追加の追加(TIME)
#         activity.last_done = pytz.utc.localize(activity.last_done)
#     print(f"Before: {activity.last_done}")  # 追加
#     activity.last_done = activity.last_done.astimezone(JST)  ### 追加(TIME) 日本時間に変換
#     updates = Update.query.filter_by(activity_id=id).order_by(Update.timestamp.desc()).all()
#     print(f"After: {activity.last_done}")  # 追加
#     for update in updates:
#         if update.timestamp.tzinfo is None:
#             update.timestamp = pytz.utc.localize(update.timestamp)
#         update.timestamp = update.timestamp.astimezone(JST)

#     return render_template('activity_detail.html', activity=activity, updates=updates)
#     # return render_template('activity_detail.html', activity=activity, update=update)

# ## この行はFlaskのデコレーターで、特定のURLパス（/update/<int:id>）と
# ## HTTPメソッド（POST）にマッチするリクエストが来た場合に、
# ## 次に定義するupdate_activity関数が実行されることを示します。

# @app.route('/update/<int:id>', methods=['POST'])  # ##not method=['POST'] この行は、Flaskのルートデコレーターです。
# # '/update/<int:id>'というURLパスに対して、POSTリクエストを受け取るエンドポイントを定義します。
# # '<int:id>'はURLパスの一部で、整数型のIDを動的に受け取ります。
# def update_activity(id):  # この関数は、エンドポイントにマッピングされた処理を行います。
#     activity = Activity.query.get(id)  # Activityモデルを使って、指定されたIDのレコードをデータベースから取得します。
#     note = request.form.get('note')
#     new_update = Update(activity_id=id, note=note)

#     # Activity.query.get(id)は、SQLAlchemyを使って IDでアクティビティを検索します。
    
#     activity.last_done = datetime.utcnow()  # 取得したアクティビティの'last_done'フィールドを現在のUTC時間に更新します。
   
#     """update_activity関数で、UTC時間で設定し、その後テンプレートでJSTに変換して表示するようにするため、以下の4行取りやめ、元の上の1行を復活させる!"""
#     # if activity.last_done.tzinfo is None:  #### 追加の追加(TIME)
#     #     activity.last_done = pytz.utc.localize(activity.last_done)
#     # activity.last_done = datetime.now(pytz.utc).astimezone(JST)  # 日本時間に変換して保存  ### ---- 追加(TIME) ---- 
#     # print(f"Updated datetime: {activity.last_done}")  #### 追加
#     # datetime.utcnow()は、現在のUTC時間を取得する関数です。

#     db.session.add(new_update)
#     db.session.commit()  # データベースセッションの変更を確定させます。
#     # この操作により、データベースに対する変更が保存されます。

#     return redirect(url_for('activity_detail', id=id))  # 指定されたIDのアクティビティ詳細ページにリダイレクトします。
#     # 'url_for('activity_detail', id=id)'は、'activity_detail'という名前のルートに対するURLを生成します。
#     # リダイレクトは、ブラウザに新しいページへの遷移を指示します。


# @app.route('/delete/<int:id>', methods=['POST'])
# def delete_activity(id):
#     activity = Activity.query.get(id)
#     db.session.delete(activity)
#     db.session.commit()
#     return redirect(url_for('index'))

# if __name__ == "__main__":
#     with app.app_context():  # データベースの全てのテーブルを作成します。SQLAlchemyで定義したモデルに基づいて、必要なテーブルがデータベースに作成されます。
#         db.create_all()

#     app.run(debug=True)  # Flaskアプリケーションを実行します。'debug=True'はデバッグモードを有効にし、コードの変更を自動的に反映させたり、エラーメッセージを詳しく表示したりします。
#     ## ただし、本番環境では通常、debug=Falseに設定します。

if __name__ == '__main__':
    app.run(debug=True)