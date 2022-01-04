from db import db
from domain.thread import Thread
from domain.topic import Topic
from post_dao import PostDAO

def get_thread_name(thread_id):
    sql = "SELECT name FROM threads WHERE id=:id"
    result = db.session.execute(sql, {"id":thread_id}).fetchone()
    if result == None:
        return ""
    return result[0]
    
def get_thread_topic(thread_id):
    sql = "SELECT A.id, A.name FROM topics A, threads B WHERE B.topic=A.id AND B.id=:thread_id"
    result = db.session.execute(sql, {"thread_id":thread_id})
    t = result.fetchone()
    return Topic(t[0], t[1])

def create_thread(topic_id, thread_name):
    sql = "INSERT INTO threads VALUES (DEFAULT, :thread_name, :topic_id) RETURNING id"
    result = db.session.execute(sql, {"thread_name":thread_name, "topic_id":topic_id})
    db.session.commit()
    return result.fetchone()[0] #ID

def create_thread_with_post(thread_name, post_text, user_id, topic_id):
    thread_id = create_thread(topic_id, thread_name)
    PostDAO(db).create_post(thread_id, post_text, user_id)
    return thread_id

def get_thread_post_count(thread_id):
    sql = "SELECT COUNT(B.id) FROM threads A, posts B WHERE B.is_deleted=FALSE AND B.thread=A.id AND A.id=:id"
    return db.session.execute(sql, {"id":thread_id}).fetchone()[0]

def get_thread_list(topic_id):
    sql = "SELECT T.id, T.name, "\
    "(SELECT COUNT(P.id) FROM posts P WHERE P.thread=T.id)"\
    "FROM threads T WHERE topic=:topic"
    result = db.session.execute(sql, {"topic":topic_id}).fetchall()
    return [Thread(x[0],x[1],x[2]) for x in result]
