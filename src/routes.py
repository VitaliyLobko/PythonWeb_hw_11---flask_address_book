from src import app
from flask import render_template, request, redirect, flash, url_for, session, make_response
from src.libs.validation_file import allowed_file
from werkzeug.utils import secure_filename
import pathlib
import uuid
from _datetime import datetime, timedelta
from src.repository import users, contacts
from marshmallow import ValidationError
from src.libs.validation_schemas import LoginSchema, RegistrationSchema


@app.before_request
def before_func():
    auth = True if 'username' in session else False
    if not auth:
        token_user = request.cookies.get('username')
        if token_user:
            user = users.get_user_by_token(token_user)
            if user:
                session['username'] = {"username": user.username, "id": user.id}


@app.route('/healthcheck', strict_slashes=False)
def healthcheck():
    return 'I`m working'


@app.route('/', strict_slashes=False)
def index():
    auth = True if 'username' in session else False
    return render_template('pages/index.html', title='Address book', auth=auth)


@app.route('/add_person', methods=['GET', 'POST'], strict_slashes=False)
def add_person():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        phone = request.form.get('phone')
        email = request.form.get('email')
        description = request.form.get('description')
        print(description)
        if 'photo' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['photo']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = pathlib.Path(app.config['UPLOAD_FOLDER']) / filename
            file.save(file_path)
            contacts.upload_contact_for_user(session['username']['id'], file_path, fullname, phone, email, description)
            flash('Uploaded successfully!')
            return redirect(url_for('address_book'))
    return render_template('pages/add_person.html', auth=auth)


@app.route('/address_book/edit/<contact_id>', methods=['GET', 'POST'], strict_slashes=False)
def contact_edit(contact_id):
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    contact = contacts.get_contact_user(contact_id, session['username']['id'])
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        description = request.form.get('description')
        contacts.update_contact(contact_id, session['username']['id'], fullname, email, phone, description)
        flash('Operation successfully!')
        return redirect(url_for('address_book'))
    return render_template('pages/edit.html', auth=auth, contact=contact)


@app.route('/address_book/delete/<contact_id>', methods=['POST'], strict_slashes=False)
def delete(contact_id):
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    if request.method == 'POST':
        contacts.delete_contact(contact_id, session['username']['id'])
        flash('Operation successfully!')
    return redirect(url_for('address_book'))


@app.route('/address_book', strict_slashes=False)
def address_book():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    address_book_user = contacts.get_contacts_user(session['username']['id'])
    return render_template('pages/address_book.html', auth=auth, contacts=address_book_user)


@app.route('/registration', methods=['GET', 'POST'], strict_slashes=False)
def registration():
    auth = True if 'username' in session else False
    if request.method == 'POST':
        try:
            RegistrationSchema().load(request.form)
        except ValidationError as err:
            return render_template('pages/registration.html', messages=err.messages)
        email = request.form.get('email')
        password = request.form.get('password')
        nick = request.form.get('nick')
        user = users.create_user(email, password, nick)
        print(user)
        return redirect(url_for('login'))
    if auth:
        return redirect(url_for('index'))
    else:
        return render_template('pages/registration.html')


@app.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    auth = True if 'username' in session else False
    if request.method == 'POST':
        try:
            LoginSchema().load(request.form)
        except ValidationError as err:
            return render_template('pages/login.html', messages=err.messages)
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') == 'on' else False
        user = users.login(email, password)
        if user is None:
            return redirect(url_for('login'))
        session['username'] = {'username': user.username, 'id': user.id}
        response = make_response(redirect(url_for('index')))
        if remember:
            token = str(uuid.uuid4())
            expire_date = datetime.now() + timedelta(days=60)
            response.set_cookie('username', token, expires=expire_date)
            users.set_token(user, token)
        return response
    if auth:
        return redirect(url_for('index'))
    else:
        return render_template('pages/login.html')


@app.route('/logout', strict_slashes=False)
def logout():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    session.pop('username')
    response = make_response(redirect(url_for('index')))
    response.set_cookie('username', '', expires=-1)

    return response
