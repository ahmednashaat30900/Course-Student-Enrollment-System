# Course-Student-Enrollment-System

## Database course Project

## Team Contributers

|Name                 | 
|---------------------|
|Ahmed Nashaat Mohamed|    
|Mohamed Sherif       |  
|Kariem Alaa          |   

## System Capabilities
The sysyem has two modes of operations admin mode and user mode, admin mode resbonsible for managing the system
by adding new courses or update already existing course, also he can delete any course or user from the system.
User mode can register in the system and browse courses and select the desired courses to enroll and also he can update his profile information

## System interface 
System designed to be responsive at all screens
![landing_Page](https://user-images.githubusercontent.com/65959637/236645226-e6610dca-146d-4147-940a-0cf653b25374.png)




## System implementation 
In the backend part of implementation Flask framework is used.
Flask is a micro web framework written in Python. It is
classified as a microframework because it does not require
particular tools or libraries. It has no database abstraction layer,
form validation, or any other components where pre-existing
third-party libraries provide common functions. However, Flask
supports extensions that can add application features as if they
were implemented in Flask itself. Extensions exist for objectrelational mappers, form validation, upload handling, various
open authentication technologies and several common
framework related tools.

## Third-party libraries used to provide some functions:
1. SQLAlchemy
SQLAlchemy is a library that facilitates the communication
between Python programs and databases. Most of the times,
this library is used as an Object Relational Mapper (ORM)
tool that translates Python classes to tables on relational
databases and automatically converts function calls to SQL
statements.
2. Flask-Login
 provides user session management for Flask. It
handles the common tasks of logging in, logging out, and
remembering your users' sessions over extended periods of
time.

3. WTForms
 is a Python library that provides flexible web
form rendering. It can used to render text fields, text areas,
password fields, radio buttons, and others. WTForms also
provides powerful data validation using different
validators, which validate that the data the user submits
meets certain criteria you define.
4. Flask-bcrypt
 is a flask extension that enables users with
utilities related to bcrypt hashing. The bcrypt is a hashing
function for password that is based on the Blowfish cipher
and incorporates salt for protecting the application against
any rainbow table attacks. We know, too many new
terminologies.

## Website Link
https://akmcourses.pythonanywhere.com/
