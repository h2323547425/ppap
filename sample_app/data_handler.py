from datetime import datetime, timedelta
from flask import session
from flask_sqlalchemy import SQLAlchemy


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
        if userId == session['userId']:
            return self.User.query.filter_by(id=userId).first().username
        raise Exception('Unauthorized')
    
    def add_user(self, username, password):
        new_user = self.User(username=username, password=password)
        self.db.session.add(new_user)
        self.db.session.commit()

    def get_notes_by_user(self):
        notes = []
        # extra work for not using ppap
        for note in self.Note.query.filter_by(owner=session['userId']).all():
            notes.append(note)
        for share in self.Share.query.filter_by(userId=session['userId']).all():
            notes.append(self.Note.query.filter_by(id=share.noteId).first())
        return notes
    
    def get_note_by_id(self, noteId):
        note = self.Note.query.filter_by(id=noteId).first()
        if note.owner == session['userId']:
            return note
        for share in self.Share.query.filter_by(noteId=noteId).all():
            if share.userId == session['userId']:
                return note
        raise Exception('Unauthorized')
    
    def add_note(self, ownerId, text):
        new_note = self.Note(
            owner=ownerId, text=text)
        self.db.session.add(new_note)
        self.db.session.commit()

    def delete_note_by_id(self, noteId):
        if self.Note.query.filter_by(id=noteId).first().owner != session['userId']:
            raise Exception('Unauthorized')
        self.Note.query.filter_by(id=noteId).delete()
        for share in self.Share.query.filter_by(noteId=noteId).all():
            self.Share.query.filter_by(id=share.id).delete()
        self.db.session.commit()

    def share_note(self, noteId, userId):
        if self.Note.query.filter_by(id=noteId).first().owner != session['userId']:
            raise Exception('Unauthorized')
        user = self.User.query.filter_by(id=userId).first()
        if user:
            expiration_time = datetime.now() + timedelta(seconds=30)
            new_share = self.Share(noteId=noteId, userId=user.id, expires=expiration_time)
            self.db.session.add(new_share)
            self.db.session.commit()

