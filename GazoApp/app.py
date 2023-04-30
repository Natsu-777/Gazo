from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random
import string
from werkzeug.utils import secure_filename
import re
import subprocess
from random import sample


def is_valid(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True
    else:
        return False


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['UPLOAD_FOLDER'] = 'static/public'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'webp', 'avif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(characters, k=length))
    return random_string


login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    bio = db.Column(db.String(120), nullable=False,
                    default='Write something about yourself')
    profession = db.Column(db.String(120), nullable=False,
                           default='Your profession')
    profile_pic = db.Column(db.String(120), nullable=False,
                            default='public/unknown.png')
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    postrows = db.relationship('Post', backref='user', lazy=True)
    starrows = db.relationship('Star', backref='user', lazy=True)
    commentrows = db.relationship('Comment', backref='user', lazy=True)
    resharerows = db.relationship('Reshare', backref='user', lazy=True)
    notificationrows = db.relationship(
        'Notification', backref='user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.id

    def get_followers(self):
        results = Connection.query.filter_by(otherperson_id=self.id).all()
        oup = []
        for result in results:
            oup.append(User.query.filter_by(id=result.user_id).first())
        return oup

    def get_following(self):
        results = Connection.query.filter_by(user_id=self.id).all()
        oup = []
        for result in results:
            oup.append(User.query.filter_by(id=result.otherperson_id).first())
        return oup

    def is_following(self, id):
        var = Connection.query.filter_by(
            user_id=self.id, otherperson_id=id).all()
        return len(var)

    def is_starred(self, id):
        var = Star.query.filter_by(user_id=self.id, post_id=id).all()
        return len(var)

    def is_reshared(self, id):
        var = Reshare.query.filter_by(user_id=self.id, post_id=id).all()
        return len(var)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    originalpost_id = db.Column(db.Integer, nullable=False, default=-1)
    description = db.Column(db.Text, nullable=True)
    post_type = db.Column(db.String(120), nullable=True)
    photo_path = db.Column(db.String(120), nullable=True)
    ml_text = db.Column(db.Text, default="")
    is_reshare = db.Column(db.String(120), default="False")
    starrows = db.relationship('Star', backref='post', lazy=True)
    commentrows = db.relationship('Comment', backref='post', lazy=True)
    resharerows = db.relationship('Reshare', backref='post', lazy=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Post %r>' % self.id

    def get_original_post(self):
        if self.is_reshare == "True":
            return Post.query.filter_by(id=self.originalpost_id).first()
        else:
            return self


class Star(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<star %r>' % self.id


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Comment %r>' % self.id

    def to_dict(self):
        # Calculate the time difference between now and the comment's date
        time_diff = datetime.utcnow() - self.date_created
        days, seconds = time_diff.days, time_diff.seconds
        hours = days * 24 + seconds // 3600

        if hours == 0:
            minutes = seconds//60
            if minutes == 0:
                time_string = "Just now"
            else:
                time_string = f"{minutes} minutes ago"
        elif hours < 24:
            time_string = f"{hours} hours ago"
        else:
            time_string = self.date_created.strftime('%d/%m/%Y')

        return {
            'id': self.id,
            'description': self.comment,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'date_created': time_string,
            'current_user': {
                'id': current_user.id
            },
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'profile_pic_url': url_for('static', filename=self.user.profile_pic)
            }
        }


class Reshare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<reshare %r>' % self.id


class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    otherperson_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Connection %r>' % self.id


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'post.id'), nullable=False, default=-1)
    user_id = db.Column(db.Integer, nullable=False)
    user_to_be_notified_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    notif_type = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def _repr_(self):
        return f'<Notification {self.id}>'

    def get_user(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        return user


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# ----------------------------------Index--------------------------------#
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('index.html', email='')
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user is not None and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('home', user_id=user.id))
        else:
            return render_template('index.html', error='Invalid credentials', email=email)


# ----------------------------------SignUp--------------------------------#
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        form_data = {'email': '', 'username': ''}
        return render_template("signup.html", form_data=form_data)
    else:
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password')
        password2 = request.form.get('cfpassword')
        form_data = {'email': email, 'username': username}
        cemail = User.query.filter_by(email=email).first()
        cuser = User.query.filter_by(username=username).first()
        if cemail:
            return render_template("signup.html", error='Email already exists.', form_data=form_data)
        elif not is_valid(email):
            return render_template("signup.html", error='Invalid email', form_data=form_data)
        elif cuser:
            return render_template("signup.html", error='Username already exists.', form_data=form_data)
        elif len(email) < 4:
            return render_template("signup.html", error='Email must be greater than 3 characters.', form_data=form_data)
        elif len(username) < 2:
            return render_template("signup.html", error='User name must be greater than 1 character.', form_data=form_data)
        elif password1 != password2:
            return render_template("signup.html", error='Passwords don\'t match.', form_data=form_data)
        elif len(password1) < 7:
            return render_template("signup.html", error='Password must be at least 7 characters.', form_data=form_data)
        else:
            password_hash = generate_password_hash(password1)
            new_user = User(email=email, username=username,
                            password_hash=password_hash)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home', user_id=new_user.id))
        
# ----------------------------------Logout--------------------------------#
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


#------------------------------------AboutUS------------------------------#
@app.route('/aboutus', methods=['GET'])
def aboutus():
    if request.method == 'GET':
        return render_template('aboutus.html')


# ----------------------------------Home--------------------------------#
@app.route('/home/<int:user_id>', methods=['GET', 'POST'])
@login_required
def home(user_id):
    if request.method == 'GET':
        user = User.query.filter_by(id=user_id).first()
        followers = user.get_followers()
        following = user.get_following()
        posts = []
        post_ids = set()
        for user in following:
            for post in user.postrows:
                if post.id not in post_ids:
                    posts.append(post)
                    post_ids.add(post.id)
        for user in followers:
            for post in user.postrows:
                if post.id not in post_ids:
                    posts.append(post)
                    post_ids.add(post.id)
        posts = sorted(posts, key=lambda p: p.date_created, reverse=True)
        return render_template('home.html', user=user, posts=posts)


# ----------------------------------Profile--------------------------------#
@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    user = User.query.filter_by(id=user_id).first()
    if request.method == 'GET':
        if user_id == current_user.id:
            return render_template('profile.html', user=user)
        else:
            return render_template('otherprofile.html', user=user)
    else:
        if request.form.get('form_type') == 'profile_update':
            username = request.form.get('username')
            email = request.form.get('email')
            bio = request.form.get('bio')
            profession = request.form.get('profession')
            password = request.form.get('password')

            cemail = User.query.filter_by(email=email).first()
            cuser = User.query.filter_by(username=username).first()
            if cemail and cemail.id != user.id:
                return render_template('profile.html', user=user, error='Email already exists.')
            elif cuser and cuser.id != user.id:
                return render_template('profile.html', user=user, error='Username already exists.')
            elif len(email) < 4:
                return render_template('profile.html', user=user, error='Email must be greater than 3 characters.')
            elif len(username) < 2:
                return render_template('profile.html', user=user, error='User name must be greater than 1 character.')
            else:
                user.username = username
                user.email = email
                user.bio = bio
                user.profession = profession
                if len(password) == 0:
                    pass
                elif len(password) > 6:
                    user.password_hash = generate_password_hash(password)
                else:
                    return render_template('profile.html', user=user, error='Password must be at least 7 characters.')
                db.session.commit()
                return render_template('profile.html', user=user, message='Profile updated successfully.')
        elif request.form.get('form_type') == 'photo_update':
            if request.form.get('delete_profile_pic') == 'yes':
                prev_profile_pic = user.profile_pic
                if prev_profile_pic != 'public/unknown.png':
                    os.remove(os.path.join(
                        app.config['UPLOAD_FOLDER'], prev_profile_pic.rsplit('/', 1)[1]))
                user.profile_pic = 'public/unknown.png'
                db.session.commit()
                return render_template('profile.html', user=user, message='Profile picture deleted successfully.')
            else:
                file = request.files['profile_pic']
                if file.filename == '':
                    return render_template('profile.html', user=user, error='No file selected.')
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    ext = filename.rsplit('.', 1)[1].lower()
                    while True:
                        random_string = generate_random_string(10)
                        filename = random_string + '.' + ext
                        filepath = os.path.join(
                            app.config['UPLOAD_FOLDER'], filename)
                        if not os.path.exists(filepath):
                            break
                    file.save(filepath)
                    prev_profile_pic = user.profile_pic
                    if prev_profile_pic != 'public/unknown.png':
                        os.remove(os.path.join(
                            app.config['UPLOAD_FOLDER'], prev_profile_pic.rsplit('/', 1)[1]))
                    user.profile_pic = 'public/' + filename
                    db.session.commit()
                    return render_template('profile.html', user=user, message='Profile picture updated successfully.')
                else:
                    return render_template('profile.html', user=user, error='Invalid file type.')


# ----------------------------------Post--------------------------------#
@app.route('/post/<int:user_id>', methods=['GET', 'POST'])
@login_required
def post(user_id):
    user = User.query.filter_by(id=user_id).first()
    if request.method == 'GET':
        return render_template('post.html', user=user)
    else:
        description = request.form.get('description')
        post_type = request.form.get('post_type')
        file = request.files['image']
        if file.filename == '':
            return render_template('post.html', user=user, error='No file selected.')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = generate_random_string(
                10) + '.' + filename.rsplit('.', 1)[1].lower()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            path = 'public/' + filename
            
            new_post = Post(user_id=user.id, description=description,
                            post_type=post_type, photo_path=path)
            db.session.add(new_post)
            db.session.commit()
            
            post_ml = Post.query.filter_by(id=new_post.id).first()
            response = ai_analysis(post_ml.id)
            text = ''
            for key, value in response.items():
                text += str(value) + ' '
            post_ml.ml_text = text.strip()
            db.session.commit()

            return render_template('post.html', user=user, message='Post created successfully.')
        else:
            return render_template('post.html', user=user, error='Invalid file type.')


# ----------------------------------Explore--------------------------------#
@app.route('/explore/<int:user_id>', methods=['GET', 'POST'])
@login_required
def explore(user_id):
    user = User.query.filter_by(id=user_id).first()
    if request.method == 'GET':
        posts = Post.query.filter_by(is_reshare="False").all()
        scores = {}
        for post in posts:
            score = len(post.starrows) + 5 * len(post.commentrows) + 2 * len(post.resharerows)
            scores[post] = score
        sorted_posts = [p[0] for p in sorted(scores.items(), key=lambda x: x[1], reverse=True)]
        top_posts = sorted_posts[:50]
        if len(top_posts) > 10:
            random_posts = sample(top_posts, 10)
        else:
            random_posts = top_posts
        return render_template('explore.html', user=user, search_type="NONE",results=random_posts)
    else:
        search_type = request.form.get('search_type')
        search_query = request.form.get('search_query')
        if search_type == "users":
            results = User.query.filter(
                User.username.ilike(f'%{search_query}%')).all()
        else:
            results = Post.query.filter((Post.description.ilike(
                f'%{search_query}%') | Post.post_type.ilike(f'%{search_query}%') | Post.ml_text.ilike(f'%{search_query}%')) & Post.is_reshare.like("False")).all()
        return render_template('explore.html', user=user, search_type=search_type, search_query=search_query, results=results)


# ----------------------------------Followers/Following----------------------------------#
@app.route('/followers/<int:user_id>', methods=['GET', 'POST'])
@login_required
def followers(user_id):
    user = User.query.filter_by(id=user_id).first()
    if request.method == 'GET':
        results = user.get_followers()
        if user_id == current_user.id:
            return render_template('followers.html', user=user, results=results)
        else:
            return render_template('otherfollowers.html', user=user, results=results)
    else:
        search_content = request.form.get('search_content')
        allfollowers = user.get_followers()
        results = [follower for follower in allfollowers if search_content.lower(
        ) in follower.username.lower()]
        if user_id == current_user.id:
            return render_template('followers.html', user=user, results=results)
        else:
            return render_template('otherfollowers.html', user=user, results=results)


@app.route('/following/<int:user_id>', methods=['GET', 'POST'])
@login_required
def following(user_id):
    user = User.query.filter_by(id=user_id).first()
    if request.method == 'GET':
        results = user.get_following()
        if user_id == current_user.id:
            return render_template('following.html', user=user, results=results)
        else:
            return render_template('otherfollowing.html', user=user, results=results)
    else:
        search_content = request.form.get('search_content')
        allfollowers = user.get_following()
        results = [follower for follower in allfollowers if search_content.lower(
        ) in follower.username.lower()]
        if user_id == current_user.id:
            return render_template('following.html', user=user, results=results)
        else:
            return render_template('otherfollowing.html', user=user, results=results)


# ----------------------------------Follow/Unfollow--------------------------#
@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
    user = User.query.filter_by(id=user_id).first()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if user:
            conn = Connection(user_id=current_user.id, otherperson_id=user_id)
            db.session.add(conn)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False})
    else:
        conn = Connection(user_id=current_user.id, otherperson_id=user_id)
        db.session.add(conn)
        db.session.commit()
        return redirect(url_for('profile', user_id=user_id))


@app.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow(user_id):
    user = User.query.filter_by(id=user_id).first()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if user:
            conn = Connection.query.filter_by(
                user_id=current_user.id, otherperson_id=user_id).first()
            db.session.delete(conn)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False})
    else:
        conn = Connection.query.filter_by(
            user_id=current_user.id, otherperson_id=user_id).first()
        db.session.delete(conn)
        db.session.commit()
        return redirect(url_for('profile', user_id=user_id))


# ----------------------------------star/Unstar--------------------------#
@app.route('/star/<int:post_id>', methods=['POST'])
@login_required
def star(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post:
        star = Star.query.filter_by(
            user_id=current_user.id, post_id=post_id).first()
        if star:
            db.session.delete(star)
            db.session.commit()
            return jsonify({'success': True})
        else:
            star = Star(user_id=current_user.id, post_id=post_id)
            db.session.add(star)
            db.session.commit()
            return jsonify({'success': True})
    return jsonify({'success': False})


# ---------------------------------Reshare-----------------------------#
@app.route('/reshare/<int:post_id>', methods=['POST'])
@login_required
def reshare(post_id):
    post = Post.query.filter_by(id=post_id).first()
    post = post.get_original_post()
    if post:
        reshare = Reshare.query.filter_by(
            user_id=current_user.id, post_id=post.id).first()
        if reshare:
            reshared_post = Post.query.filter_by(
                is_reshare="True", user_id=current_user.id, originalpost_id=post.id).first()
            db.session.delete(reshare)
            db.session.delete(reshared_post)
            db.session.commit()
            return jsonify({'success': True})
        else:
            reshare = Reshare(user_id=current_user.id, post_id=post.id)
            reshared_post = Post(user_id=current_user.id, is_reshare="True", originalpost_id=post.id,
                                 post_type=post.post_type, description=post.description, photo_path=post.photo_path)
            db.session.add(reshare)
            db.session.add(reshared_post)
            db.session.commit()
            return jsonify({'success': True})
    return jsonify({'success': False})


# --------------------------------comments------------------------------#
@app.route('/comment/<int:post_id>', methods=['GET', 'POST'])
@login_required
def comments(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if request.method == 'GET':
        if post:
            commentsList = post.commentrows[::-1]
            return jsonify([comment.to_dict() for comment in commentsList])
    else:
        if post:
            description = request.json['commentBody']
            user_id = current_user.id
            comment = Comment(comment=description,
                              user_id=user_id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
            commentsList = [comment]
            return jsonify([comment.to_dict() for comment in commentsList])
        else:
            return jsonify({'message': 'Post not found.'}), 404


@app.route('/comment/<int:comment_id>/delete', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    if comment:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'message': f'Comment {comment_id} deleted successfully'})
    else:
        return jsonify({'message': f'Comment {comment_id} not found'})


# ---------------------------------deletePost-----------------------------#
@app.route('/deletepost/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post:
        post_photo_path = post.photo_path
        if post_photo_path != 'public/unknown.png':
            os.remove(os.path.join(
                app.config['UPLOAD_FOLDER'], post_photo_path.rsplit('/', 1)[1]))
        if post.originalpost_id == -1:
            Star.query.filter_by(post_id=post.id).delete()
            Post.query.filter_by(originalpost_id=post.id).delete()
            Reshare.query.filter_by(post_id=post.id).delete()
            Comment.query.filter_by(post_id=post.id).delete()
            Post.query.filter_by(id=post.id).delete()
            db.session.commit()
            return jsonify({'message': f'Post {post_id} deleted successfully'})
        else:
            Post.query.filter_by(id=post.id).delete()
            Reshare.query.filter_by(
                post_id=post.originalpost_id, user_id=current_user.id).delete()
            db.session.commit()
            return jsonify({'message': f'Post {post_id} deleted successfully'})

    else:
        return jsonify({'message': f'Post {post_id} not found'})



# --------------------------------Notifications---------------------------#
@app.route('/notification', methods=['POST'])
@login_required
def send_notification():
    data = request.get_json()
    notif_type = data['notif_type']
    user_to_be_notified_id = data['user_to_be_notified_id']
    post_id = data['post_id']

    notification = Notification(
        notif_type=notif_type,
        user_to_be_notified_id=user_to_be_notified_id,
        post_id=post_id,
        user_id=current_user.id
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({'message': 'Notification sent successfully'}), 200


@app.route('/notifications/<int:user_id>', methods=['GET', 'DELETE'])
@login_required
def notifications(user_id):
    if request.method == 'GET':
        user = User.query.filter_by(id=user_id)
        notifications = Notification.query.filter_by(
            user_to_be_notified_id=user_id).all()
        return render_template('notifications.html', notifications=notifications, user=user)
    elif request.method == 'DELETE':
        user = User.query.filter_by(id=user_id)
        notifications = Notification.query.filter_by(
            user_to_be_notified_id=user_id).all()
        for notification in notifications:
            db.session.delete(notification)
        db.session.commit()
        return '', 204


# --------------------------------Delete Account--------------------#
@app.route('/deleteacc/<int:user_id>')
@login_required
def deleteacc(user_id):
    user = User.query.filter_by(id=user_id).first()
    posts = user.postrows
    for post in posts:
        delete_post(post.id)
    Connection.query.filter_by(user_id=user_id).delete()
    Connection.query.filter_by(otherperson_id=user_id).delete()
    Notification.query.filter_by(user_id=user_id).delete()
    Notification.query.filter_by(user_to_be_notified_id=user_id).delete()
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    return render_template('signup.html', message="Create an account", form_data={'email': '', 'username': ''})


# ---------------------------------AI analysis-----------------------------#
@app.route('/ai/<int:post_id>', methods=['GET'])
@login_required
def ai(post_id):
    post = Post.query.filter_by(id=post_id).first()
    post = post.get_original_post()
    if post:
        response = ai_analysis(post.id)
        return jsonify(response), 200
    
def ai_analysis(post_id):
    post = Post.query.filter_by(id=post_id).first()
    response = {}
    labelsCommand = f"python3 vision.py labels ./static/{post.photo_path}"
    labelsOup = subprocess.run(labelsCommand.split(), capture_output=True, text=True)
    if labelsOup.returncode == 0:
        oup = labelsOup.stdout.splitlines()
        if(len(oup)==1):
            response['labels'] = "No labels found"
        else:
            response['labels'] = oup[1:]
    else:
        response['labels'] = "No labels found"

    facesCommand = f"python3 vision.py faces ./static/{post.photo_path}"
    facesOup = subprocess.run(facesCommand.split(), capture_output=True, text=True)
    if facesOup.returncode == 0:
        oup = facesOup.stdout.splitlines()
        if(len(oup)==1):
            response['expressions'] = "No expressions found"
        else:
            response['expressions'] = oup[1:]
    else:
        response['expressions'] = "No expressions found"

    landmarksCommand = f"python3 vision.py landmarks ./static/{post.photo_path}"
    landmarksOup = subprocess.run(landmarksCommand.split(), capture_output=True, text=True)
    if landmarksOup.returncode == 0:
        oup = landmarksOup.stdout.splitlines()
        if(len(oup)==1):
            response['landmarks'] = "No landmarks found"
        else:
            response['landmarks'] = oup[1:]
    else:
        response['landmarks'] = "No landmarks found"

    logosCommand = f"python3 vision.py logos ./static/{post.photo_path}"
    logosOup = subprocess.run(logosCommand.split(), capture_output=True, text=True)
    if logosOup.returncode == 0:
        oup = logosOup.stdout.splitlines()
        if(len(oup)==1):
            response['logos'] = "No logos found"
        else:
            response['logos'] = oup[1:]
    else:
        response['logos'] = "No logos found"

    safeSearchCommand = f"python3 vision.py safe-search ./static/{post.photo_path}"
    safeSearchOup = subprocess.run(safeSearchCommand.split(), capture_output=True, text=True)
    if safeSearchOup.returncode == 0:
        oup = safeSearchOup.stdout.splitlines()
        response['safeSearch'] = oup[1:]
    else:
        response['safeSearch'] = "Can't determine safe search"

    textCommand = f"python3 vision.py text ./static/{post.photo_path}"
    textOup = subprocess.run(textCommand.split(), capture_output=True, text=True)
    if textOup.returncode == 0:
        oup = textOup.stdout.splitlines()
        if(len(oup)==1):
            response['text'] = "No text found"
        else:
            response['text'] = oup[1:]
    else:
        response['text'] = "No text found"

    localizedObjectCommand = f"python3 vision.py object-localization ./static/{post.photo_path}"
    localizedObjectOup = subprocess.run(localizedObjectCommand.split(), capture_output=True, text=True)
    if localizedObjectOup.returncode == 0:
        oup = localizedObjectOup.stdout.splitlines()
        if(len(oup)==1):
            response['localizedObject'] = "No objects found"
        else:
            response['localizedObject'] = oup[1:]
    else:
        response['localizedObject'] = "No objects found"
    
    return response

if __name__ == "__main__":
    app.run(debug=False)
