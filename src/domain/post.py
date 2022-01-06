
class Post:

    def __init__(self, id, text, poster, time, file, thread):
        self.id = id
        self.content = text
        self.poster = poster
        self.thread = thread
        self.time = time
        self.file = file
        self.can_delete = False

