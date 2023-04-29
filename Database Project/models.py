from main import db




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

 