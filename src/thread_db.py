from db import db
from domain.thread import Thread
from domain.topic import Topic

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

def get_thread_post_count(thread_id):
    sql = "SELECT COUNT(B.id) FROM threads A, posts B WHERE B.is_deleted IS NOT TRUE AND B.thread=A.id AND A.id=:id"
    return db.session.execute(sql, {"id":thread_id}).fetchone()[0]

def get_thread(thread_id):
    sql = "SELECT id, name, is_deleted FROM threads WHERE id=:id"
    result = db.session.execute(sql, {"id":thread_id}).fetchone()
    if result == None:
        return None
    return Thread(result[0], result[1], 0, result[2])

def get_thread_list(topic_id):
    sql = "SELECT T.id, T.name, T.is_deleted, "\
    "(SELECT COUNT(P.id) FROM posts P WHERE P.thread=T.id AND P.is_deleted IS NOT TRUE)"\
    "FROM threads T WHERE topic=:topic AND T.is_deleted IS NOT TRUE"
    result = db.session.execute(sql, {"topic":topic_id}).fetchall()
    return [Thread(x[0], x[1], x[3], x[2]) for x in result if x[3] > 0]

def delete_thread(thread_id):
    sql = "UPDATE threads SET is_deleted=TRUE WHERE id=:tid"
    db.session.execute(sql, {"tid":thread_id})
    db.session.commit()

