import datetime
from ppap.policy import Policy
from ppap.function_wrapper import Flag

class NoteFlag(Flag):
    READ = 0
    WRITE = 1
    SHARE = 2

class NotePolicy(Policy):
    def __init__(self, nodeId, noteDB, shareDB):
        self.nodeId = nodeId
        self.noteDB = noteDB
        self.shareDB = shareDB
        super().__init__("NotePolicy")

    def check_policy(self, context, flag):
        if context.user is None:
            return False
        if flag == NoteFlag.WRITE or flag == NoteFlag.SHARE:
            return context.user == self.noteDB.query.filter_by(id=self.nodeId).first().owner
        elif flag == NoteFlag.READ:
            for share in self.shareDB.query.filter_by(noteId=self.nodeId).all():
                if share.userId == context.user and share.expires > datetime.datetime.now():
                    return True
            return context.user == self.noteDB.query.filter_by(id=self.nodeId).first().owner
        return False