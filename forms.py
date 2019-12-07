from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from facetoonblog.models import User, Post, Comment
from flask_login import current_user


class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=10)])
	confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign up')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('This username has already been taken')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('This email has already been taken')


class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=10)])
	remember = BooleanField('Remember me')
	submit = SubmitField('Login')


class CommentForm(FlaskForm):
	comment = StringField('Comment', validators=[DataRequired()])
	submit = SubmitField('Add')

class UpdateAccountForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	picture = FileField('Profile picture', validators=[FileAllowed(['png', 'jpg'])])
	submit = SubmitField('Update')

	def validate_username(self, username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('This username has already been taken')

	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('This email has already been taken')


class NewPostForm(FlaskForm):
	description = StringField('Title', validators=[DataRequired()])
	content = TextAreaField('Contents', validators=[DataRequired(), Length(max=250)])
	post_pic = FileField('Profile picture', validators=[FileAllowed(['png', 'jpg'])])
	submit = SubmitField('Post')


class UpdatePostForm(FlaskForm):
	description = StringField('Title', validators=[DataRequired()])
	content = TextAreaField('Contents', validators=[DataRequired(), Length(max=250)])
	post_pic = FileField('Profile picture', validators=[FileAllowed(['png', 'jpg'])])
	submit = SubmitField('Post')

class RequestResetForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Request')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError('This user email is not recorded in our database.')

class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=10)])
	confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Change')