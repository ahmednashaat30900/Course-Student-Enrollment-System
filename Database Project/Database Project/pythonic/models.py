from pythonic import db
from flask_login import UserMixin

# ================================================================================================================
# DB Classes
class Students(db.Model, UserMixin):
    student_id = db.Column(db.Integer, primary_key=True)
    student_username = db.Column(db.String(50), unique=True, nullable=False, )
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

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))

    def __repr__(self):
        return f"<User(username='{self.username}', password='{self.password}')>"
    
    def is_authenticated(self):
        return True
    

class lessons(db.Model):
    lesson_id = db.Column(db.Integer, primary_key=True)
    lesson_name = db.Column(db.String(120), unique=True, nullable=False)
    lesson_file =db.Column(db.String(120))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=False)


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
# END OF CLASSES
# ================================================================================================================
