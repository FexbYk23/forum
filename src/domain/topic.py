class Topic:
    def __init__(self, id, name, description="", thread_count=0):
        self.id = id
        self.name = name
        self.thread_count = thread_count
        self.desc = description

    def get_url(self):
        return "/topics/" + str(self.id)
