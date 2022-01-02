
class Post:

    def __init__(self, text, poster, time):
        self.content = text
        self.poster = poster
        self.time = time

    def get_text(self):
        return self.__text

    def get_poster(self):
        return self.__poster
