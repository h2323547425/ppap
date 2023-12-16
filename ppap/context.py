from datetime import datetime
from flask import session

class Context():

    def __init__(self):
        self.user = -1
        if 'userId' in session:
            self.user = session['userId']
        self.time = datetime.now()