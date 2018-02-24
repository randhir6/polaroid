from polaroid import app
from flask import Flask, render_template, request, send_file, session, flash, redirect, url_for, logging
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from forms import RegisterForm, LoginForm


app.config['SECRET_KEY'] = "lundbc"

#MySql Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'polaroid'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#init mysql
mysql = MySQL(app)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        
        #create cursor
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users (name, email, username, password) VALUES (%s, %s, %s, %s)", (name, email, username, password))

        #commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('you are registered, you can login and edit your file', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password_form = form.password.data

        #create cursor
        cur = mysql.connection.cursor()

        result = cur.execute("SELECT name, email, password FROM users WHERE username = (%s)", [username])

        if result > 0:
            data = cur.fetchone()
            password = data['password']

            if sha256_crypt.verify(password_form, password):
                app.logger.info('password matched')
            else:
                app.logger.info('password dont match')

        else:
            app.logger.info('no user')
        
    return render_template('login.html', form=form)
