from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
import secrets
from PIL import Image
from sqlalchemy import func, or_
import os
from pythonic import app, db, bcrypt
from pythonic.forms import RegistrationForm, LoginForm, UpdateAccountForm
from pythonic.models import Students, User, lessons, courses, Enrollment

# App routes
# Homepage route

@app.route('/')
def homepage():
   if current_user.is_authenticated:
        student_image= url_for('static', filename='profile_pics/' + current_user.student_image)
        return render_template("homepage.html",student_image=student_image)
   return render_template("homepage.html")

# Register route
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("courses"))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Students(student_username=form.username.data, student_email=form.email.data, student_password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')    
        return redirect('login')

    return render_template('register.html', pagetitle='Register', form=form)

# Admin route
@app.route('/admin', methods=['GET', 'POST'])
def admin():
        all_students = Students.query.all()
        all_courses = courses.query.all()
        total_students = Students.query.count()
        total_courses = courses.query.count()
        return render_template('admin.html' ,pagetitle='Admin', all_students=all_students, all_courses=all_courses, total_students=total_students, total_courses=total_courses)


    
# Login route
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = LoginForm()
    if form.validate_on_submit():
        admin = User.query.filter_by(username=form.email.data).first()
        # hashed_password = bcrypt.generate_password_hash(form.password.data)
        if admin and bcrypt.check_password_hash(admin.password, form.password.data):
            return redirect("admin")
        else:
            user = Students.query.filter_by(student_email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.student_password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                if next_page != "%2fadmin":
                    return redirect(next_page) if next_page else redirect(url_for('viewcourses'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
          
    return render_template('login.html', pagetitle='Login', form=form)

# Logout route
@app.route('/logout')
def logout():
    logout_user()
    return render_template("homepage.html")

# Add course route
@app.route('/formaddcourse')
def formaddcourse():
   return render_template("addcourse.html")


@app.route('/addcourse', methods=[ 'POST'])
def addcourse():
   
    course_category = request.form['course_category']
    course_name = request.form['course_name']
    course_description = request.form['course_description']
    total_course_hours = request.form['total_course_hours']
    course_instructor = request.form['course_instructor']
    course_syllabus = request.form['course_syllabus']
    course_image = request.files['course_image']
    course_image= save_picture_course(course_image)

    course = courses(course_category=course_category, course_name=course_name, course_description=course_description,
                     total_course_hours=total_course_hours, course_instructor=course_instructor , course_image=course_image, course_syllabus=course_syllabus )
    db.session.add(course)
    db.session.commit()

    return redirect(url_for('admin'))

# # Add lesson route
# @app.route('/addlessonform/<int:course_id>')
# def addlessonform(course_id):
#     course = courses.query.get(course_id)
#     return render_template("addlesson.html", course=course)


# @app.route('/addlesson/<int:course_id>', methods=['GET','POST'])
# def addlesson(course_id):   
#     course = courses.query.get(course_id)
#     lesson_name= request.form.get('lesson_name')
#     new_lesson = lessons(lesson_name=lesson_name ,course_id=course_id)
#     db.session.add(new_lesson)
#     db.session.commit()
#     return redirect(url_for('updatecourse', course_id=course_id))
# View course route
@app.route('/viewcourses')
def viewcourses():
    all = courses.query.all()
    if current_user.is_authenticated:
       student_image= url_for('static', filename='profile_pics/' + current_user.student_image)
       return render_template('viewcourses.html' , all=all, student_image=student_image)
    return render_template('viewcourses.html' , all=all)
        
# Acount route
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
    return render_template('acount.html', pagetitle='Account', student_image=student_image, Courses=Courses, enrollments=enrollments, enrollment_count=enrollment_count)

# Update acount route
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

# view student route
@app.route('/viewstudents')
def viewstudents():
    all = Students.query.all()
    al = courses.query.all()
    return render_template('admin.html' , all=all, al=al)

#course route
@app.route("/course/<int:course_id>")
def course(course_id):    
    course = courses.query.get_or_404(course_id)
    students = db.session.query(Students).join(Enrollment).filter(Enrollment.course_enrolled_id == course_id).all()
    Lessons = db.session.query(lessons).filter(lessons.course_id == course_id).all()
    enrollment_count = Enrollment.query.filter_by(course_enrolled_id=course.course_id).count()
    student_image= url_for('static', filename='profile_pics/' + current_user.student_image)
    return render_template('course.html', course=course, students=students, enrollment_count=enrollment_count, Lessons=Lessons, student_image=student_image)

# update course route
@app.route("/updatecourse/<int:course_id>")
def updatecourse(course_id):  
    course = courses.query.get_or_404(course_id)
    students = db.session.query(Students).join(Enrollment).filter(Enrollment.course_enrolled_id == course_id).all()
    Lessons = db.session.query(lessons).filter(lessons.course_id == course_id).all()
    enrollment_count = Enrollment.query.filter_by(course_enrolled_id=course.course_id).count()
    return render_template('updatecourse.html', course=course, students=students, enrollment_count=enrollment_count, Lessons=Lessons)


# Delete course route
@app.route("/course/<int:course_id>/delete", methods=['POST'])
def delete_course(course_id):
    course= courses.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()

    return redirect(url_for('admin'))


# Delete student route
@app.route("/student/<int:student_id>/delete", methods=['POST'])
def delete_student(student_id):
    student= Students.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()

    return redirect(url_for('admin'))

# Enroll route
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
        flash('You are already enrolled in this course!', 'warning')
        return redirect(url_for('course', course_id=course.course_id))
    
    enrollment = Enrollment(student_enrolled_id=student_enrolled_id, course_enrolled_id=course_erolled_id)
    db.session.add(enrollment)
    db.session.commit()
    
    flash('Successfully enrolled in course!')
    return redirect(url_for('acount'))


# Search route
@app.route('/search', methods=['GET', 'POST'])
def search():
    
        search_term = request.form['search']
        results = db.session.query(courses).filter(or_(func.lower(courses.course_name).like('%' + search_term.lower() + '%'),func.lower(courses.course_category).like('%' + search_term.lower() + '%'))).all()
        print(results)
        return render_template('search.html', results=results, search_term=search_term)



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
    picture_path = os.path.join(app.root_path, 'static/courses_pics', picture_fn)
    output_size = (530, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


with app.app_context():
    try:
        # db.drop_all()
        db.create_all()
        # new_user = User(username = "admin123@admin.com", password = bcrypt.generate_password_hash("#2468Kariem").decode('utf-8'))
        # db.session.add(new_user)
        # db.session.commit()
    except Exception as e:
        print(f"Error creating database tables: {e}")


app.run(debug=True)
