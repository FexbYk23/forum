
class Post:

    def __init__(self, id, text, poster, time, file):
        self.id = id
        self.content = text
        self.poster = poster
        self.time = time
        self.file = file
        self.can_delete = False

