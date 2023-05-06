from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
app = Flask(__name__)

# App configration
app.config['SECRET_KEY'] = 'gfhkfuu774nmdgtsjhf765tgj7yrgfjkjgt'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'static/course_images'


db = SQLAlchemy(app)
from pythonic.forms import RegistrationForm, LoginForm, AddLessonForm, UpdateAccountForm
from pythonic.models import Students, User, lessons, courses, Enrollment
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='info'

@login_manager.user_loader
def load_user(student_id):
    return Students.query.get(int(student_id))