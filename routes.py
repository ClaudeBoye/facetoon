import os
import secrets
from PIL import Image
from flask import render_template,  redirect, url_for, flash, request, abort
from facetoonblog import app, bcrypt, db, mail
from flask_login import login_user, current_user, login_required, logout_user
from facetoonblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, CommentForm, NewPostForm, UpdatePostForm, RequestResetForm, ResetPasswordForm
from facetoonblog.models import User, Post, Comment
from flask_mail import Message


@app.route('/')
@app.route('/index')
def index():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = CommentForm()
	post = Post.query.order_by(Post.date_posted.desc()).all()
	return render_template('index.html', post=post)



@app.route('/home')
def home():
	if not current_user.is_authenticated:
		return redirect(url_for('index'))
	form = CommentForm()
	if current_user.is_authenticated:
		post = Post.query.order_by(Post.date_posted.desc()).all()
	return render_template('home.html', title='Home', post=post, form=form)


@app.route('/comments/<int:post_id>', methods=['GET', 'POST'])
@login_required
def add_comment(post_id):
	post = Post.query.get_or_404(int(post_id))
	form = CommentForm()
	if form.comment:
		if form.validate_on_submit():
			comments = Comment(comment=form.comment.data, post_id=post.id, author=current_user)
			db.session.add(comments)
			db.session.commit()
			return redirect(url_for('add_comment', post_id=post.id))
	comment = Comment.query.filter_by(post_id=post_id).order_by(Comment.id.desc()).all()
	return render_template('addcomment.html', title='Home', post=post, comment=comment, form=form)



@app.route('/register', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hash_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hash_pass)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created! You can now login', 'success')
		return redirect(url_for('home'))
	return render_template('register.html', title='Register', form=form)



@app.route('/login', methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
			flash('login successfull', 'success')
			return redirect(url_for('home'))
		else:
			flash('Unsuccessful wrong username or password please check and try again')
	return render_template('login.html', title='Login', form=form)


def save_profile(form_image):
	random_token = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_image.filename)
	picture_fn = random_token + f_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
	
	output_size = (90, 90)
	i = Image.open(form_image)
	i.thumbnail(output_size)
	i.save(picture_path)

	return picture_fn


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_profile(form.picture.data)
			current_user.profile_pic = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('You account has been updated', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename='profile_pics/' + current_user.profile_pic)
	return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route('/logout')
@login_required
def logout():
	try:
		logout_user()
		return redirect(url_for('index'))
	except:
		flash('You are not login please login')
		return redirect(url_for('login'))


def save_post(form_pict):
	random_hex = secrets.token_hex(10)
	_, f_ext = os.path.splitext(form_pict.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/post_pics', picture_fn)
	
	output_size = (500, 400)
	i = Image.open(form_pict)
	i.thumbnail(output_size)
	i.save(picture_path)

	return picture_fn


@app.route('/new/post', methods=['GET', 'POST'])
@login_required
def new_post():
	form = NewPostForm()
	if form.validate_on_submit():
		if form.post_pic:
			post_picture = save_post(form.post_pic.data)
		post = Post(description=form.description.data, content=form.content.data, post_image=post_picture, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post has been added', 'success')
		return redirect(url_for('home'))
	return render_template('new_post.html', title='New Post', legend='New Post', form=form)



@app.route('/update/<int:post_id>', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
	post = Post.query.get_or_404(int(post_id))
	if post.author != current_user:
		abort(403)
	form = UpdatePostForm()
	if form.validate_on_submit():
		if form.post_pic:
			post_picture = save_post(form.post_pic.data)
		post.description = form.description.data
		post.content = form.content.data
		post.post_image = post_picture
		db.session.commit()
		flash('Your post has been updated')
		return redirect(url_for('home'))
	elif request.method == 'GET':
		form.description.data = post.description
		form.content.data = post.content
		form.post_pic.data = post.post_image
	return render_template('new_post.html', title='Update Post', legend='Update Post', form=form)


@app.route('/delete/<int:post_id>', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(int(post_id))
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted')
	return redirect(url_for('user_post', username=current_user.username))


@app.route('/user/<string:username>')
@login_required
def user_post(username):
	if username is None:
		return redirect(url_for('home'))
	user = User.query.filter_by(username=username).first_or_404()
	post = Post.query.filter_by(author=user).order_by(Post.date_posted.desc())
	return render_template('user_post.html', title='Post', user=user, post=post)


def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('password Reset Request',
		sender='nonreply@gmail.com',
		recipients=[user.email])
	msg.body=f""" A request for your facetoon account password reset please follow the link below to reset.
Note that this link will expire after 40 minutes
{ url_for('reset_password', token=token, _external=True )}
please if you did not request for this just simply ignor this message thanks """
	
	mail.send(msg)


@app.route('/request_reset', methods=['GET', 'POST'])
def request_reset():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is None:
			flash('Sorry user was not found in our database try Registring')
			return redirect(url_for('request_reset'))
		else:
			send_reset_email(user)
			flash('An email link has been send to this email please cheak your inbox and follow the link')
			return redirect(url_for('index'))
	return render_template('reset.html', title='Request reset password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('This token is invalid or has expird')
		return redirect(url_for('request_reset'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hash_password
		db.session.commit()
		return redirect(url_for('login'))
	return render_template('reset_password.html', title='Password reset', form=form)

@app.route('/about')
def about():
	return render_template('about.html', title='about page')


@app.errorhandler(404)
def error_404(e):
	return render_template('404.html')


@app.errorhandler(403)
def error_403(e):
	return render_template('403.html')

@app.errorhandler(500)
def error_500(e):
	return render_template('500.html')