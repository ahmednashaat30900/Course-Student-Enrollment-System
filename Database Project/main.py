from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, Response,jsonify
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import login_user, current_user, logout_user, login_required
import secrets
from PIL import Image
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, select, func
import cx_Oracle
import os


app = Flask(__name__)

app.config['SECRET_KEY'] = 'gfhkfuu774nmdgtsjhf765tgj7yrgfjkjgt'
app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle+cx_oracle://hr:feng@localhost:1521'
app.config['UPLOAD_FOLDER'] = 'static/course_images'
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='info'


class RegistrationForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',  validators=[DataRequired(), EqualTo('password')])
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
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[ Length(min=2, max=20)])
    email = StringField('Email', validators=[])
    headline = StringField('Headline', validators=[])
    mobil = StringField('Mobil', validators=[])
    about = TextAreaField('About', validators=[])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')




@login_manager.user_loader
def load_user(student_id):
    return Students.query.get(int(student_id))

class Students(db.Model, UserMixin):
    student_id = db.Column(db.Integer, primary_key=True)
    student_username = db.Column(db.String(50), unique=True, nullable=False)
    student_email = db.Column(db.String(120), unique=True, nullable=False)
    student_image = db.Column(db.String(20),  nullable=False, default='dd.png')
    student_mobil = db.Column(db.String(20))
    student_headline = db.Column(db.String(120))
    student_about = db.Column(db.String(1000))
    student_password = db.Column(db.String(120), unique=True, nullable=False)
   

    def __repr__(self):
        return '<User %r>' % self.username
    
    def get_id(self):
        return str(self.student_id)

    def is_authenticated(self):
        return True


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


@app.route('/')
def homepage():
  
   return render_template("homepage.html")

@app.route('/formaddcourse')
def formaddcourse():
   return render_template("addcourse.html")



@app.route('/addcourse', methods=[ 'POST'])
def addcourse():
    new_id = seq_course.nextval()
    course_category = request.form['course_category']
    course_name = request.form['course_name']
    course_description = request.form['course_description']
    total_course_hours = request.form['total_course_hours']
    course_instructor = request.form['course_instructor']
    course_syllabus = request.form['course_syllabus']
    course_image = request.files['course_image']
    course_image= save_picture_course(course_image)

    course = courses( course_id=new_id,course_category=course_category, course_name=course_name, course_description=course_description,
                     total_course_hours=total_course_hours, course_instructor=course_instructor , course_image=course_image, course_syllabus=course_syllabus )
    db.session.add(course)
    db.session.commit()

    return render_template("admin.html",  course_image= course_image)

@app.route('/viewcourses')
def courses():
    all = courses.query.all()
    
    return render_template('viewcourses.html' , all=all)

@app.route('/admin')
def admin():
    all = Students.query.all()
    al = courses.query.all()
    total_students = Students.query.count()
    total_courses = courses.query.count()
    return render_template('admin.html' , all=all, al=al, total_students=total_students, total_courses=total_courses)

   
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("courses"))
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
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data=='ahmed195148@gmail.com' and form.password.data:
            return redirect("admin")
        else:
           user = Students.query.filter_by(student_email=form.email.data).first()
           if user and bcrypt.check_password_hash(user.student_password, form.password.data):
              login_user(user, remember=form.remember.data)
              next_page = request.args.get('next')
              return redirect(next_page) if next_page else redirect(url_for('courses'))
    else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return render_template("homepage.html")

@app.route('/acount')
@login_required
def acount():
    user = Students.query.filter_by(student_id=current_user.student_id).first()
    enrollments = Enrollment.query.filter_by(student_enrolled_id=user.student_id).all()
    enrollment_count = Enrollment.query.filter_by(student_enrolled_id=current_user.student_id).count()
    Courses = []
    for e in enrollments:
        course = courses.query.get(e.course_enrolled_id)
        Courses.append(course)
    student_image= url_for('static', filename='profile_pics/' + current_user.student_image)
    return render_template('acount.html', title='Account', student_image=student_image, Courses=Courses, enrollments=enrollments, enrollment_count=enrollment_count)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

def save_picture_course(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (530, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route("/updateacount", methods=['GET', 'POST'])
@login_required
def updateacount():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.student_image = picture_file
        current_user.student_username = form.username.data
        current_user.student_email = form.email.data
        current_user.student_mobil = form.mobil.data
        current_user.student_headline = form.headline.data
        current_user.student_about = form.about.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('acount'))
    elif request.method == 'GET':
        form.username.data = current_user.student_username
        form.email.data = current_user.student_email
        form.mobil.data = current_user.student_mobil
        form.headline.data = current_user.student_headline
        form.about.data = current_user.student_about
        
    student_image = url_for('static', filename='profile_pics/' + current_user.student_image)
    return render_template('updateacount.html', title='Account', student_image=student_image,
                            form=form)





@app.route('/viewstudents')
def viewstudents():
    all = Students.query.all()
    al = courses.query.all()
    return render_template('admin.html' , all=all, al=al)


@app.route("/course/<int:course_id>")
def course(course_id):
    course = courses.query.get_or_404(course_id)

    return render_template('course.html', course=course)



@app.route("/course/<int:course_id>/delete", methods=['POST'])

def delete_course(course_id):
    course= courses.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('admin'))

@app.route('/enroll/<int:course_id>')
@login_required
def enroll(course_id):
   
    user = Students.query.filter_by(student_id=current_user.student_id).first()
    course = courses.query.get(course_id)
    if course is None:
       flash('Course not found')
       return redirect(url_for('acount'))
    student_enrolled_id = user.student_id
    course_erolled_id = course.course_id

    existing_enrollment = Enrollment.query.filter_by(course_enrolled_id=course_id, student_enrolled_id=student_enrolled_id).first()
    if existing_enrollment:
        return 'Error: Student is already enrolled in this course'
    
    enrollment = Enrollment(student_enrolled_id=student_enrolled_id, course_enrolled_id=course_erolled_id)
    db.session.add(enrollment)
    db.session.commit()
    
    flash('Successfully enrolled in course!')
    return redirect(url_for('acount'))



@app.route('/search', methods=['GET', 'POST'])
def search():
    
        search_term = request.form['search']
        results = db.session.query(courses).filter(func.lower(courses.course_name).like('%' + search_term.lower() + '%')).all()
        print(results)
        return render_template('search.html', results=results, search_term=search_term)


class courses(db.Model):
     course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
     course_category = db.Column(db.String(50),  nullable=False)
     course_name = db.Column(db.String(120), nullable=False)
     course_description = db.Column(db.String(500), nullable=False)
     course_image = db.Column(db.String(20))
     total_course_hours = db.Column(db.String(120), nullable=False)
     course_instructor = db.Column(db.String(120), nullable=False)
     course_syllabus = db.Column(db.String(2000), nullable=False)
     

 
class Enrollment(db.Model):
    course_enrolled_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), primary_key=True)
    student_enrolled_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), primary_key=True)





with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error creating database tables: {e}")


app.run(debug=True)
