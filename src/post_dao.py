from domain.post import Post
from domain.topic import Topic
from domain.thread import Thread
from user import get_user_list

class PostDAO:

    def __init__(self, db):
        self.__db = db
   
    def is_post_valid(self, post_text):
        return len(post_text) > 0

    def get_posts_by_thread(self, thread_id):
        """Returns a list of Post objects in thread"""

        sql = "SELECT * FROM posts WHERE thread=:thread_id"
        result = self.__db.session.execute(sql, {"thread_id":thread_id})
        posts = result.fetchall()
        post_list = []
        user_list = get_user_list()

        for post in posts:
            p = Post(post["content"], user_list[post["poster"]], post["time"])
            post_list.append(p)
        return post_list

    
    def get_thread_name(self, thread_id):
        sql = "SELECT name FROM threads WHERE id=:id"
        result = self.__db.session.execute(sql, {"id":thread_id}).fetchone()
        if result == None:
            return ""
        return result[0]
    
    def get_thread_topic(self, thread_id):
        sql = "SELECT A.id, A.name FROM topics A, threads B WHERE B.topic=A.id AND B.id=:thread_id"
        result = self.__db.session.execute(sql, {"thread_id":thread_id})
        t = result.fetchone()
        return Topic(t[0], t[1])

    def create_thread(self, topic_id, thread_name):
        """Returns thread id"""
        sql = "INSERT INTO threads VALUES (DEFAULT, :thread_name, :topic_id) RETURNING id"
        result = self.__db.session.execute(sql, {"thread_name":thread_name, "topic_id":topic_id})
        self.__db.session.commit()
        return result.fetchone()[0] #ID

    def create_post(self, thread_id, post_text, user_id):
        sql = "INSERT INTO posts VALUES (DEFAULT, :text, :user_id, :thread_id, NOW())"
        self.__db.session.execute(sql, {"text":post_text, "user_id":user_id, "thread_id":thread_id})
        self.__db.session.commit()


    def create_thread_with_post(self, thread_name, post_text, user_id, topic_id):
        thread_id = self.create_thread(topic_id, thread_name)
        self.create_post(thread_id, post_text, user_id)
        return thread_id

    def get_topic_by_id(self, topic_id):
        sql = "SELECT id, name FROM topics WHERE id=:id"
        result = self.__db.session.execute(sql, {"id":topic_id})
        t = result.fetchone()
        return Topic(t[0], t[1])

    def get_thread_post_count(self, thread_id):
        sql = "SELECT COUNT(B.id) FROM threads A, posts B WHERE B.is_deleted=FALSE AND B.thread=A.id AND A.id=:id"
        return self.__db.session.execute(sql, {"id":thread_id}).fetchone()[0]

    def get_thread_list(self, topic_id):
        sql = "SELECT T.id, T.name, "\
        "(SELECT COUNT(P.id) FROM posts P WHERE P.thread=T.id)"\
        "FROM threads T WHERE topic=:topic"
        result = self.__db.session.execute(sql, {"topic":topic_id}).fetchall()
        print(result)
        return [Thread(x[0],x[1],x[2]) for x in result]

    def create_topic(self, topic_name, topic_desc):
        sql = "INSERT INTO topics VALUES (DEFAULT, :name, :desc, FALSE)"
        self.__db.session.execute(sql, {"name":topic_name, "desc":topic_desc})
        self.__db.session.commit()

    def delete_topic(self, topic_id):
        sql = "UPDATE topics SET is_deleted=TRUE WHERE id=:id"
        self.__db.session.execute(sql, {"id":topic_id})
        self.__db.session.commit()
