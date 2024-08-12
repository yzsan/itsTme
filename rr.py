from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Activity, Update
from app import db, bcrypt

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')


# def register():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
#         new_user = User(username=username, password=hashed_password)
#         db.session.add(new_user)
#         db.session.commit()
#         flash('Account created successfully!', 'success')
#         return redirect(url_for('main.login'))
#     return render_template('register.html')

# 以下 try-exceptの導入
from flask import Flask, render_template, request, redirect, url_for, flash
from your_application import db, User

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # フォームからデータを取得
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')

            # 新しいユーザーのインスタンスを作成
            new_user = User(username=username, password=password, email=email)

            # データベースにユーザーを追加
            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful!', 'success')
            return redirect(url_for('login'))

        # except Exception as e:
        #     # エラーが発生した場合、フラッシュメッセージを表示し、再度register.htmlをレンダリング
        #     db.session.rollback()  # トランザクションをロールバック
        #     flash(f'An error occurred: {str(e)}', 'danger')
        #     return render_template('register.html')

        # 表示の改善
        except IntegrityError as e:
            db.session.rollback()
            # ログに詳細なエラーメッセージを記録
            app.logger.error(f"IntegrityError: {e}")
            flash('Username already exists. Please choose a different username.', 'danger')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Unexpected error: {e}")
            flash('An unexpected error occurred. Please try again.', 'danger')

    return render_template('register.html')



@main.route('/login', methods=['GET', 'POST'])
def login():
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

