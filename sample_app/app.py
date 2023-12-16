from flask import Flask, request, session, render_template, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError

from data_handler import DataHandler

app = Flask(__name__)
db = DataHandler(app)


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')
    def validate_username(self, username):
        return not db.check_existing_user(username.data)

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

class NoteForm(FlaskForm):
    note = StringField(validators=[
                       InputRequired(), Length(min=1, max=500)], render_kw={"placeholder": "text"})
    submit = SubmitField('Add Note')

class ShareForm(FlaskForm):
    user = StringField(validators=[
                       InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "User to share with"})
    submit = SubmitField('Share Note')
    def validate_username(self, username):
        if db.check_existing_user(username.data) is False:
            raise ValidationError(
                "That username doesn't already exists. Please enter a different one.")


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.form.get('test-mode') == 'locust' or form.validate_on_submit():
        userId = db.validate_user(form.username.data, form.password.data)
        if userId:
            session['userId'] = userId
            return redirect(url_for('dashboard', userId=userId))
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if request.form.get('test-mode') == 'locust' or form.validate_on_submit():
        if form.validate_username(form.username):
            db.add_user(form.username.data, form.password.data)
            return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/dashboard/<int:userId>', methods=['GET', 'POST'])
def dashboard(userId):

    selected_noteId = request.args.get('selected_noteId', default=-1, type=int)

    add_form = NoteForm()
    share_form = ShareForm()

    # for testing
    if request.args.get("test-mode") == "locust":
        username = request.args.get("username")
        userId = db.get_user_id(username)
    if request.form.get("test-mode") == "locust":
        username = request.form.get("username")
        userId = db.get_user_id(username)
        try:
            db.add_note(userId, request.form.get("note"))
            return redirect(url_for('dashboard', userId=userId, selected_noteId=selected_noteId))
        except:
            return error("You are not authorized to add this note.")

    if add_form.validate_on_submit():
        try:
            db.add_note(userId, add_form.note.data)
            return redirect(url_for('dashboard', userId=userId, selected_noteId=selected_noteId))
        except:
            return error("You are not authorized to add this note.")
        
    
    if share_form.validate_on_submit():
        if db.check_existing_user(share_form.user.data) is False:
            raise ValidationError(
                "That username doesn't already exists. Please enter a different one.")
        share_userId = db.get_user_id(share_form.user.data)
        try:
            db.share_note(selected_noteId, share_userId)
            return redirect(url_for('dashboard', userId=userId, selected_noteId=selected_noteId))
        except:
            return error("You are not authorized to share this note.")
        
    try:
        rendered = render_template('dashboard.html', userId=userId, selected_noteId=selected_noteId, addForm=add_form, shareForm=share_form, db=db)
    except:
        return error("You are not authorized to view this page.")
    return rendered


@app.route('/delete_note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    try:
        db.delete_note_by_id(note_id)
    except:
        return error("You are not authorized to delete this note.")
    
    return redirect(url_for('dashboard', userId=session['userId']))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('userId', None)
    return redirect(url_for('home'))

@app.route('/error')
def error(error):
    logout()
    return render_template('error.html', error=error), 401


if __name__ == "__main__":
    app.run(debug=True)