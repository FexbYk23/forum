from domain.post import Post
from domain.topic import Topic
from domain.thread import Thread
from domain.file import File
from user import get_user_list

class PostDAO:

    def __init__(self, db):
        self.__db = db
    
    def __create_post_object(self, db_fetched, user_list):
        post = db_fetched
        file_url = self.get_post_file_url(post["id"])
        return Post(post["id"], post["content"], user_list[post["poster"]], post["time"], file_url, post["thread"])
            
    def get_post(self, post_id):
        sql = "SELECT * FROM posts WHERE id=:post_id"
        result = self.__db.session.execute(sql, {"post_id":post_id})
        post = result.fetchone()
        user_list = get_user_list()
        return self.__create_post_object(post, user_list)

    def get_posts_by_thread(self, thread_id):
        sql = "SELECT * FROM posts WHERE thread=:thread_id and is_deleted is not TRUE"
        result = self.__db.session.execute(sql, {"thread_id":thread_id})
        posts = result.fetchall()
        post_list = []
        user_list = get_user_list()

        for post in posts:
            p = self.__create_post_object(post, user_list)
            post_list.append(p)
        return post_list

    def create_post(self, thread_id, post_text, user_id):
        sql = "INSERT INTO posts VALUES (DEFAULT, :text, :user_id, :thread_id, NOW()) RETURNING id"
        result = self.__db.session.execute(sql, {"text":post_text, "user_id":user_id, "thread_id":thread_id})
        self.__db.session.commit()
        return result.fetchone()[0] #id
    
    def create_file(self, filename, filedata):
        sql = "INSERT INTO files VALUES (DEFAULT, :name, :data, FALSE) RETURNING id"
        subst = {"name" : filename, "data":filedata}
        result = self.__db.session.execute(sql, subst)
        self.__db.session.commit()
        return result.fetchone()[0]
                
    def add_file_to_post(self, post_id, file_id):
        sql = "INSERT INTO file_to_post VALUES (:file_id, :post_id)"
        self.__db.session.execute(sql, {"file_id":file_id, "post_id":post_id})
        self.__db.session.commit()

    def create_post_with_file(self, thread_id, post_text, user_id, filename, filedata):
        post_id = self.create_post(thread_id, post_text, user_id)
        file_id = self.create_file(filename, filedata)
        self.add_file_to_post(post_id, file_id)
    
    def get_file(self, file_id):
        sql = "SELECT name,data FROM files WHERE id=:id AND is_deleted is not TRUE"
        result = self.__db.session.execute(sql, {"id":file_id}).fetchone()
        if result == None:
            return None
        return File(result[0], result[1])
    

    def get_post_file_url(self, post_id):
        file_info = self.get_post_file(post_id)
        if file_info != None:
            return f"/file/{file_info[0]}/{file_info[1]}"
        return None

    def get_post_file(self, post_id):
        sql = "SELECT A.id, A.name FROM files A, file_to_post B WHERE B.post_id=:post" \
        " AND B.file_id=A.id AND A.is_deleted is not TRUE"
        result = self.__db.session.execute(sql, {"post":post_id}).fetchone()
        if result == None:
            return None
        return (result[0], result[1])
        
    def get_topic_by_id(self, topic_id):
        sql = "SELECT id, name, is_deleted FROM topics WHERE id=:id"
        result = self.__db.session.execute(sql, {"id":topic_id})
        t = result.fetchone()
        if t == None or t[2]:    #is_deleted = 1
            return None
        return Topic(t[0], t[1])


    def create_topic(self, topic_name, topic_desc):
        sql = "INSERT INTO topics VALUES (DEFAULT, :name, :desc, FALSE)"
        self.__db.session.execute(sql, {"name":topic_name, "desc":topic_desc})
        self.__db.session.commit()

    def delete_topic(self, topic_id):
        sql = "UPDATE topics SET is_deleted=TRUE WHERE id=:id"
        self.__db.session.execute(sql, {"id":topic_id})
        self.__db.session.commit()

    def delete_post(self, post_id):
        file_info = self.get_post_file(post_id)
        sql = "UPDATE posts SET is_deleted=TRUE WHERE id=:post_id"
        sql2 = "UPDATE files SET is_deleted=TRUE WHERE id=:file_id"

        self.__db.session.execute(sql, {"post_id":post_id})
        if file_info != None:
            self.__db.session.execute(sql2, {"file_id":file_info[0]})
        self.__db.session.commit()
