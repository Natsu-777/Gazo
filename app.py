from flask import Flask, render_template, request, flash, redirect, url_for, json, jsonify
from flask_login import current_user, login_required, LoginManager, UserMixin, login_user,logout_user
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['UPLOAD_FOLDER'] = 'static/public'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    bio = db.Column(db.String(200), default="Update Bio!")
    profile_photo = db.Column(db.String(200), default="NONE")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Child relationships
    posts = db.relationship('Post', backref='user', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

    # Parent relationships
    followers = db.relationship('Follow',
                                foreign_keys='Follow.follower_id',
                                backref='follower', lazy=True)
    following = db.relationship('Follow',
                                foreign_keys='Follow.user_id',
                                backref='user', lazy=True)
    
class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_url = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Child relationships
    likes = db.relationship('Like', backref='post', lazy=True)
    comments = db.relationship('Comment', backref='post', lazy=True)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    text = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ------------------------------------------------------Login-----------------------------------------------

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, password=password).first()
        if user is not None:
            login_user(user)
            return redirect("/home")
        else:
            flash('Invalid credentials.', category='error')
            return redirect("/")

    return render_template("index.html")


# ------------------------------------------------------SignUp-----------------------------------------------

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password')
        password2 = request.form.get('cfpassword')

        cemail = User.query.filter_by(email=email).first()
        cuser = User.query.filter_by(username=username).first()
        if cemail:
            flash('Email already exists.', category='error')
            render_template("SignUp.html")
        elif cuser:
            flash('Username already exists.', category='error')
            render_template("SignUp.html")
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
            render_template("SignUp.html")
        elif len(username) < 2:
            flash('First name must be greater than 1 character.', category='error')
            render_template("SignUp.html")
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
            render_template("SignUp.html")
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
            render_template("SignUp.html")
        else:
            new_user = User(email=email, username=username, password=password1)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash('Account created!', category='success')
            return redirect(url_for('home'))
    return render_template("SignUp.html")


# ------------------------------------------------------Display-Home-----------------------------------------------

@app.route('/home')
def home():
    return render_template("Home.html")


# ------------------------------------------------------Display-Profile-----------------------------------------------
@app.route('/profile')
@login_required
def profile():
    user = current_user
    return render_template('Profile.html', user=user)

# ------------------------------------------------------Update-Profile-----------------------------------------------

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    data = request.get_json()

    user = User.query.get(current_user.id)
    user.username = data['username']
    user.bio = data['bio']
    db.session.commit()

    return jsonify({'username': user.username, 'bio': user.bio})

# ------------------------------------------------------Upload-Photo-----------------------------------------------

@app.route('/change_profile_pic')
@login_required
def change_profile_pic():
    return render_template('photo-form.html')
 
@app.route('/change_profile_pic', methods=['POST'])
@login_required
def upload_profile_pic():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        user = User.query.get(current_user.id)
        user.profile_photo = './static/public/'+filename
        print(user.profile_photo)
        db.session.commit()
        return redirect('/profile')
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)
 
# ------------------------------------------------------Upload-Photo-----------------------------------------------

@app.route('/post',methods=['POST','GET'])
@login_required
def post():
    if request.method == 'POST':
        pass
    return render_template('Post.html')

# ------------------------------------------------------Explore-----------------------------------------------

@app.route('/explore',methods=['GET'])
@login_required
def explore():
    return render_template('Explore.html')

# ------------------------------------------------------Followers-----------------------------------------------

@app.route('/followers',methods=['GET'])
@login_required
def followers():
    return render_template('Followers.html')

# ------------------------------------------------------Following-----------------------------------------------

@app.route('/following',methods=['GET'])
@login_required
def following():
    return render_template('Following.html')

# ------------------------------------------------------Notifications-----------------------------------------------

@app.route('/notifications',methods=['GET'])
@login_required
def notifs():
    return render_template('Notification.html')

# ------------------------------------------------------Sign-out-----------------------------------------------
@app.route('/logout',methods=['GET'])
@login_required
def logout():
    logout_user()
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
