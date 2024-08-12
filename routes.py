from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, current_user, logout_user, login_required
from models import User, Activity, Update
from app import db, bcrypt

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError  # ここでIntegrityErrorをインポート

main = Blueprint('main', __name__)

# @main.route('/')
# def index():
#     return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    # if current_user.is_authenticated:
    #     return redirect(url_for('main.index'))
    if request.method == 'POST':
        try:
            # フォームからデータを取得
            username = request.form.get('username')
            password = request.form.get('password')
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            # 新しいユーザーのインスタンスを作成
            new_user = User(username=username, password=hashed_password)
            # データベースにユーザーを追加
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('main.login'))
        
        except IntegrityError as e:
            db.session.rollback()
            # ログに詳細なエラーメッセージを記録
            current_app.logger.error(f"IntegrityError: {e}")
            flash('Username already exists. Please choose a different username.', 'danger')
        
        except Exception as e:
            # エラーが発生した場合、フラッシュメッセージを表示し、再度register.htmlをレンダリング
            db.session.rollback()  # トランザクションをロールバック
            # flash(f'An error occurred: {str(e)}', 'danger')

            current_app.logger.error(f"Unexpected error: {e}")
            flash('An unexpected error occurred. Please try again.', 'danger')

            
            # return render_template('register.html')

    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

# 以下はapp.pyから移動
from datetime import datetime, timedelta
import pytz  ### 追加(TIME)

JST = pytz.timezone('Asia/Tokyo')  ### 追加(TIME)

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# @app.route('/logout')  # *
@main.route('/logout')  # *
def logout():
    # logout_user()
    session.clear()
    # return redirect(url_for('main.index'))
    return redirect(url_for('main.login'))

# @app.route('/')
@main.route('/')
@login_required  # *
def index():
    # activities = Activity.query.all()
    activities = Activity.query.filter_by(user_id=current_user.id).all()  # *
    current_time = datetime.now(pytz.utc).astimezone(JST)
    activities_with_elapsed = []
    for activity in activities:
        if activity.last_done.tzinfo is None:
            activity.last_done = pytz.utc.localize(activity.last_done)
        activity.last_done = activity.last_done.astimezone(JST)  ## この1行でUTCからJST表示
        elapsed_days = (current_time - activity.last_done).days
        activities_with_elapsed.append({
            'activity': activity,
            'elapsed_days': elapsed_days
        })


    # 経過日数の多い順にソート
    sorted_activities = sorted(activities_with_elapsed, key=lambda activity: activity['elapsed_days'], reverse=True)
    return render_template('index.html', activities=sorted_activities)


# @app.route('/add', methods=['GET', 'POST'])
# @main.route('/add', methods=['GET', 'POST'])
@main.route('/add_activity', methods=['GET', 'POST'])
@login_required  # ** migration修正の際に追加
def add_activity():
    if request.method == 'POST':
        # name = request.form.get('details')  ## これ1行だけだったので修正
        name = request.form.get('name')
        details = request.form.get('details')
        # new_activity = Activity(name=name)  ## これを修正
        last_done = datetime.strptime(request.form['last_done'], '%Y-%m-%dT%H:%M')
        last_done = JST.localize(last_done)  ## 強制追加
        last_done = last_done.astimezone(pytz.utc)  ## 強制追加
        new_activity = Activity(name=name, details=details, last_done=last_done, user_id=current_user.id)  # ** migration修正の際にuser_id記載を追加

        db.session.add(new_activity)
        db.session.commit()
        return redirect(url_for('main.index'))  ## 抜けていたので修正
    return render_template('add_activity.html')

# @app.route('/activity/<int:id>')  ## ここからの4行が抜けていたので追加
@main.route('/activity/<int:id>')  ## ここからの4行が抜けていたので追加
def activity_detail(id):
    activity = Activity.query.get(id)
    if activity.last_done.tzinfo is None:  #### 追加の追加(TIME)
        activity.last_done = pytz.utc.localize(activity.last_done)
    print(f"Before: {activity.last_done}")  # 追加
    activity.last_done = activity.last_done.astimezone(JST)  ### 追加(TIME) 日本時間に変換
    updates = Update.query.filter_by(activity_id=id).order_by(Update.timestamp.desc()).all()
    print(f"After: {activity.last_done}")  # 追加
    for update in updates:
        if update.timestamp.tzinfo is None:
            update.timestamp = pytz.utc.localize(update.timestamp)
        update.timestamp = update.timestamp.astimezone(JST)

    return render_template('activity_detail.html', activity=activity, updates=updates)
    # return render_template('activity_detail.html', activity=activity, update=update)

## この行はFlaskのデコレーターで、特定のURLパス（/update/<int:id>）と
## HTTPメソッド（POST）にマッチするリクエストが来た場合に、
## 次に定義するupdate_activity関数が実行されることを示します。

# @app.route('/update/<int:id>', methods=['POST'])  # ##not method=['POST'] この行は、Flaskのルートデコレーターです。
@main.route('/update/<int:id>', methods=['POST'])  # ##not method=['POST'] この行は、Flaskのルートデコレーターです。
# '/update/<int:id>'というURLパスに対して、POSTリクエストを受け取るエンドポイントを定義します。
# '<int:id>'はURLパスの一部で、整数型のIDを動的に受け取ります。
def update_activity(id):  # この関数は、エンドポイントにマッピングされた処理を行います。
    activity = Activity.query.get(id)  # Activityモデルを使って、指定されたIDのレコードをデータベースから取得します。
    note = request.form.get('note')
    new_update = Update(activity_id=id, note=note)

    # Activity.query.get(id)は、SQLAlchemyを使って IDでアクティビティを検索します。
    
    activity.last_done = datetime.utcnow()  # 取得したアクティビティの'last_done'フィールドを現在のUTC時間に更新します。
   
    """update_activity関数で、UTC時間で設定し、その後テンプレートでJSTに変換して表示するようにするため、以下の4行取りやめ、元の上の1行を復活させる!"""
    # if activity.last_done.tzinfo is None:  #### 追加の追加(TIME)
    #     activity.last_done = pytz.utc.localize(activity.last_done)
    # activity.last_done = datetime.now(pytz.utc).astimezone(JST)  # 日本時間に変換して保存  ### ---- 追加(TIME) ---- 
    # print(f"Updated datetime: {activity.last_done}")  #### 追加
    # datetime.utcnow()は、現在のUTC時間を取得する関数です。

    db.session.add(new_update)
    db.session.commit()  # データベースセッションの変更を確定させます。
    # この操作により、データベースに対する変更が保存されます。

    return redirect(url_for('main.activity_detail', id=id))  # 指定されたIDのアクティビティ詳細ページにリダイレクトします。
    # 'url_for('activity_detail', id=id)'は、'activity_detail'という名前のルートに対するURLを生成します。
    # リダイレクトは、ブラウザに新しいページへの遷移を指示します。


# @app.route('/delete/<int:id>', methods=['POST'])
@main.route('/delete/<int:id>', methods=['POST'])
def delete_activity(id):
    activity = Activity.query.get(id)
    db.session.delete(activity)
    db.session.commit()
    return redirect(url_for('main.index'))



