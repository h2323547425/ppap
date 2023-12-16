from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from ppap.container import Container
from ppap.function_wrapper import FunctionWrapper
from ppap.policy_assertion_exception import PolicyAssertionError

from sample_app_with_ppap.ppap_extension.note_policy import NotePolicy, NoteFlag
from sample_app_with_ppap.ppap_extension.user_policy import UserPolicy, UserFlag


class DataHandler():

    def __init__(self, app):
        db = SQLAlchemy(app)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
        app.config['SECRET_KEY'] = 'thisisasecretkey'
        self.db = db
        self.app = app

        class User(self.db.Model):
            id = db.Column(db.Integer, primary_key=True, autoincrement=True)
            username = db.Column(db.String(20), nullable=False, unique=True)
            password = db.Column(db.String(80), nullable=False)

        class Note(self.db.Model):
            id = db.Column(db.Integer, primary_key=True, autoincrement=True)
            owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
            text = db.Column(db.String(500), nullable=False)

        class Share(self.db.Model):
            id = db.Column(db.Integer, primary_key=True, autoincrement=True)
            noteId = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=False)
            userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
            expires = db.Column(db.DateTime, nullable=True)

        self.db.create_all()

        self.User = User
        self.Note = Note
        self.Share = Share

        self.note_containers = {}
        for note in self.Note.query.all():
            self.note_containers[note.id] = Container(note, NotePolicy(note.id, Note, Share))

        self.user_containers = {}
        for user in self.User.query.all():
            self.user_containers[user.id] = Container(user, UserPolicy(user.id, User))

    # pre-login
    def check_existing_user(self, username):
        return self.User.query.filter_by(username=username).first() != None

    def validate_user(self, username, password):
        user = self.User.query.filter_by(username=username).first()
        if user and user.password == password:
            return user.id
        return None 
    
    def get_user_id(self, username):
        user = self.User.query.filter_by(username=username).first()
        if user:
            return user.id
        return None

    # post-login
    def get_username(self, userId):
        username = []
        def do_get_username(user):
            username.append(user.username)
        self.user_containers[userId].invoke(FunctionWrapper(do_get_username, UserFlag.USERNAME))
        return username[0]
    
    def add_user(self, username, password):
        new_user = self.User(username=username, password=password)
        self.db.session.add(new_user)
        self.db.session.commit()
        self.user_containers[new_user.id] = Container(new_user, UserPolicy(new_user.id, self.User))

    def get_notes_by_user(self):
        notes = []
        def do_get_note_by_owner(note):
            notes.append(note)
        for note_container in self.note_containers.values():
            try:
                note_container.invoke(FunctionWrapper(do_get_note_by_owner, NoteFlag.READ))
            except PolicyAssertionError:
                pass
        return notes
    
    def get_note_by_id(self, noteId):
        notes = []
        def do_get_note_by_id(note):
            notes.append(note)
        self.note_containers[noteId].invoke(FunctionWrapper(do_get_note_by_id, NoteFlag.READ))
        return notes[0]
    
    def add_note(self, ownerId, text):
        new_note = self.Note(
            owner=ownerId, text=text)
        self.db.session.add(new_note)
        self.db.session.commit()
        self.note_containers[new_note.id] = Container(new_note, NotePolicy(new_note.id, self.Note, self.Share))

    def delete_note_by_id(self, noteId):
        def do_delete_note_by_id(note):
            self.Note.query.filter_by(id=note.id).delete()
            for share in self.Share.query.filter_by(noteId=note.id).all():
                self.Share.query.filter_by(id=share.id).delete()
            self.db.session.commit()
            del self.note_containers[noteId]
        self.note_containers[noteId].invoke(FunctionWrapper(do_delete_note_by_id, NoteFlag.WRITE))

    def share_note(self, noteId, userId):
        user = self.User.query.filter_by(id=userId).first()
        if user:
            def do_share_note(note):
                # note.owner = user.id
                expiration_time = datetime.now() + timedelta(seconds=30)
                new_share = self.Share(noteId=note.id, userId=user.id, expires=expiration_time)
                self.db.session.add(new_share)
                self.db.session.commit()
            self.note_containers[noteId].invoke(FunctionWrapper(do_share_note, NoteFlag.SHARE))
        
