from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import login_user, current_user, logout_user, login_required

from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, select
import cx_Oracle
import os
import base64

app = Flask(__name__)

app.config['SECRET_KEY'] = 'gfhkfuu774nmdgtsjhf765tgj7yrgfjkjgt'
app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle+cx_oracle://hr:feng@localhost:1521'
bcrypt = Bcrypt(app)
app.config['UPLOAD_FOLDER'] = 'static/course_images'
db = SQLAlchemy(app)



class RegistrationForm(FlaskForm):

    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = Students.query.filter_by(student_username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = Students.query.filter_by(student_email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
        
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class Students(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    student_username = db.Column(db.String(50), unique=True, nullable=False)
    student_email = db.Column(db.String(120), unique=True, nullable=False)

    student_password = db.Column(db.String(120), unique=True, nullable=False)
  

    def __repr__(self):
        return '<User %r>' % self.username

class Sequence:
    def __init__(self, name, start=1, increment=1, max_value=None, min_value=None, cycle=False, cache_size=20):
        self.name = name
        self.start = start
        self.increment = increment
        self.max_value = max_value
        self.min_value = min_value
        self.cycle = cycle
        self.cache_size = cache_size

    def create(self):
        options = []
        if self.start:
            options.append(f"START WITH {self.start}")
        if self.increment:
            options.append(f"INCREMENT BY {self.increment}")
        if self.max_value:
            options.append(f"MAXVALUE {self.max_value}")
        if self.min_value:
            options.append(f"MINVALUE {self.min_value}")
        if self.cycle:
            options.append("CYCLE")
        else:
            options.append("NOCYCLE")
        if self.cache_size:
            options.append(f"CACHE {self.cache_size}")
        options_str = " ".join(options)
        op=text(f"SELECT {self.name}.nextval from dual")
        db.session.execute(op)

    def nextval(self):
        yp=text(f"SELECT {self.name}.nextval from dual")
        return db.session.execute(yp).scalar()


# create a sequence
with app.app_context():
    seq_course= Sequence('seq_course', start=1, increment=1, cycle=False, cache_size=20)
    seq_course.create()

with app.app_context():
    seq_student= Sequence('seq_student', start=1, increment=1, cycle=False, cache_size=20)
    seq_student.create()

# insert a new record with the next value of the sequence



@app.route('/')
def index():
   return render_template("addcourse.html")



@app.route('/addcourse', methods=[ 'POST'])
def addcourse():
    new_id = seq_course.nextval()
    
    course_category = request.form['course_category']
    course_name = request.form['course_name']
    course_description = request.form['course_description']
    total_course_hours = request.form['total_course_hours']
    course_instructor = request.form['course_instructor']
    course_image = request.files['course_image']
    filename = secure_filename(course_image.filename)
    course_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    course = courses( course_id=new_id,course_category=course_category, course_name=course_name, course_description=course_description,
                     total_course_hours=total_course_hours, course_instructor=course_instructor , course_image=filename )
    db.session.add(course)
    db.session.commit()

    return render_template("addcourse.html")

@app.route('/viewcourses')
def courses():
    all = courses.query.all()


    return render_template('viewcourses.html' , all=all)

@app.route('/images/<filename>')
def image(filename):
    send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename)
    return render_template("viewcourses.html")

   
@app.route("/register", methods=['GET', 'POST'])
def register():
    new_student = seq_student.nextval()
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Students(student_id=new_student, student_username=form.username.data, student_email=form.email.data, student_password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')

    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
  
    form = LoginForm()
    if form.validate_on_submit():
        user = Students.query.filter_by(student_email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.student_password, form.password.data):
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('register'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)






class Student(db.Model):
     student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
     student_name = db.Column(db.String(120), unique=True, nullable=False)
     student_email = db.Column(db.String(120), unique=True, nullable=False)
     student_password = db.Column(db.String(120), unique=True, nullable=False)
     student_image = db.Column(db.LargeBinary)
     student_phone = db.Column(db.String(50), unique=True)
     course_id = db.Column(db.Integer, db.ForeignKey('courses'), nullable=False)


class categories(db.Model):
     category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
     category_name = db.Column(db.String(50), unique=True, nullable=False)


class courses(db.Model):
     course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
     course_category = db.Column(db.String(50),  nullable=False)
     course_name = db.Column(db.String(120), nullable=False)
     course_description = db.Column(db.String(120), nullable=False)
     course_image = db.Column(db.LargeBinary)
     total_course_hours = db.Column(db.String(120), nullable=False)
     course_instructor = db.Column(db.String(120), nullable=False)
     students = db.relationship('Student', backref='course')

 






with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error creating database tables: {e}")




    

app.run(debug=True)
