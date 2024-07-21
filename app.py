from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz  ### 追加(TIME)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///activities.db'
db = SQLAlchemy(app)

JST = pytz.timezone('Asia/Tokyo')  ### 追加(TIME)

class Activity(db.Model):  ## not db.model
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    last_done = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.String(500), nullable=True)

@app.route('/')
def index():
    activities = Activity.query.all()
    for activity in activities:
        if activity.last_done.tzinfo is None:  #### 追加の追加(TIME)
            activity.last_done = pytz.utc.localize(activity.last_done)
        print(f"Before: {activity.last_done}")  # 追加
        activity.last_done = activity.last_done.astimezone(JST)
        print(f"After: {activity.last_done}")  # 追加
    return render_template('index.html', activities=activities)


@app.route('/add', methods=['GET', 'POST'])
def add_activity():
    if request.method == 'POST':
        # name = request.form.get('details')  ## これ1行だけだったので修正
        name = request.form.get('name')
        details = request.form.get('details')
        # new_activity = Activity(name=name)  ## これを修正
        new_activity = Activity(name=name, details=details)

        db.session.add(new_activity)
        db.session.commit()
        return redirect(url_for('index'))  ## 抜けていたので修正
    return render_template('add_activity.html')

@app.route('/activity/<int:id>')  ## ここからの4行が抜けていたので追加
def activity_detail(id):
    activity = Activity.query.get(id)
    if activity.last_done.tzinfo is None:  #### 追加の追加(TIME)
        activity.last_done = pytz.utc.localize(activity.last_done)
    print(f"Before: {activity.last_done}")  # 追加
    activity.last_done = activity.last_done.astimezone(JST)  ### 追加(TIME) 日本時間に変換
    print(f"After: {activity.last_done}")  # 追加
    return render_template('activity_detail.html', activity=activity)

## この行はFlaskのデコレーターで、特定のURLパス（/update/<int:id>）と
## HTTPメソッド（POST）にマッチするリクエストが来た場合に、
## 次に定義するupdate_activity関数が実行されることを示します。

@app.route('/update/<int:id>', methods=['POST'])  # ##not method=['POST'] この行は、Flaskのルートデコレーターです。
# '/update/<int:id>'というURLパスに対して、POSTリクエストを受け取るエンドポイントを定義します。
# '<int:id>'はURLパスの一部で、整数型のIDを動的に受け取ります。
def update_activity(id):  # この関数は、エンドポイントにマッピングされた処理を行います。
    activity = Activity.query.get(id)  # Activityモデルを使って、指定されたIDのレコードをデータベースから取得します。
    # Activity.query.get(id)は、SQLAlchemyを使って IDでアクティビティを検索します。
    
    activity.last_done = datetime.utcnow()  # 取得したアクティビティの'last_done'フィールドを現在のUTC時間に更新します。
   
    """update_activity関数で、UTC時間で設定し、その後テンプレートでJSTに変換して表示するようにするため、以下の4行取りやめ、元の上の1行を復活させる!"""
    # if activity.last_done.tzinfo is None:  #### 追加の追加(TIME)
    #     activity.last_done = pytz.utc.localize(activity.last_done)
    # activity.last_done = datetime.now(pytz.utc).astimezone(JST)  # 日本時間に変換して保存  ### ---- 追加(TIME) ---- 
    # print(f"Updated datetime: {activity.last_done}")  #### 追加
    # datetime.utcnow()は、現在のUTC時間を取得する関数です。


    db.session.commit()  # データベースセッションの変更を確定させます。
    # この操作により、データベースに対する変更が保存されます。

    return redirect(url_for('activity_detail', id=id))  # 指定されたIDのアクティビティ詳細ページにリダイレクトします。
    # 'url_for('activity_detail', id=id)'は、'activity_detail'という名前のルートに対するURLを生成します。
    # リダイレクトは、ブラウザに新しいページへの遷移を指示します。


@app.route('/delete/<int:id>', methods=['POST'])
def delete_activity(id):
    activity = Activity.query.get(id)
    db.session.delete(activity)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    with app.app_context():  # データベースの全てのテーブルを作成します。SQLAlchemyで定義したモデルに基づいて、必要なテーブルがデータベースに作成されます。
        db.create_all()

    app.run(debug=True)  # Flaskアプリケーションを実行します。'debug=True'はデバッグモードを有効にし、コードの変更を自動的に反映させたり、エラーメッセージを詳しく表示したりします。
    ## ただし、本番環境では通常、debug=Falseに設定します。

