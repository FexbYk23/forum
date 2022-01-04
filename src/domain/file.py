from mimetypes import guess_type

class File:
    def __init__(self, name, data):
        self.name = name
        self.data = bytes(data)

    def get_mimetype(self):
        return guess_type(self.name)
