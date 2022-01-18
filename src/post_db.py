from domain.post import Post
from domain.topic import Topic
from domain.thread import Thread
from domain.file import File
from user import get_user_list
from db import db

def __create_post_object(db_fetched, user_list):
	post = db_fetched
	file_url = get_post_file_url(post["id"])
	return Post(post["id"], post["content"], user_list[post["poster"]], post["time"], file_url, post["thread"])

def get_post(post_id):
	sql = "SELECT * FROM posts WHERE id=:post_id"
	result = db.session.execute(sql, {"post_id":post_id})
	post = result.fetchone()
	user_list = get_user_list()
	return __create_post_object(post, user_list)

def get_posts_by_thread(thread_id):
	sql = "SELECT * FROM posts WHERE thread=:thread_id and is_deleted is not TRUE"
	result = db.session.execute(sql, {"thread_id":thread_id})
	posts = result.fetchall()
	post_list = []
	user_list = get_user_list()

	for post in posts:
		p = __create_post_object(post, user_list)
		post_list.append(p)
	return post_list

def get_latest_post(thread_id):
	sql = "SELECT A.id, A.content, B.name, A.time, A.thread FROM posts A, users B"\
	" WHERE A.poster=B.id AND A.thread=:tid AND A.is_deleted is not TRUE"\
	" ORDER BY time DESC LIMIT 1"
	result = db.session.execute(sql, {"tid":thread_id}).fetchone()
	return Post(result[0], result[1], result[2], result[3], "", result[4])

def create_post(thread_id, post_text, user_id, file_id):
	sql = "INSERT INTO posts VALUES (DEFAULT, :text, :user_id, :thread_id, :file_id,  NOW()) RETURNING id"
	result = db.session.execute(sql, {"text":post_text, "user_id":user_id, "thread_id":thread_id, "file_id":file_id})
	db.session.commit()
	return result.fetchone()[0] #id

def create_file(filename, filedata):
	sql = "INSERT INTO files VALUES (DEFAULT, :name, :data, FALSE) RETURNING id"
	subst = {"name" : filename, "data":filedata}
	result = db.session.execute(sql, subst)
	db.session.commit()
	return result.fetchone()[0]

def create_post_with_file(thread_id, post_text, user_id, filename, filedata):
	file_id = create_file(filename, filedata)
	create_post(thread_id, post_text, user_id, file_id)

def get_file(file_id):
	sql = "SELECT name,data FROM files WHERE id=:id AND is_deleted is not TRUE"
	result = db.session.execute(sql, {"id":file_id}).fetchone()
	if result == None:
		return None
	return File(result[0], result[1])


def is_file_thread_deleted(file_id):
	sql = "SELECT T.is_deleted FROM " \
	"Threads T,Files F, posts P " \
	"WHERE P.file_id=F.id AND T.id=P.thread AND F.id=:file_id"
	result = db.session.execute(sql, {"file_id":file_id}).fetchone()
	return result[0] == True


def get_post_file_url(post_id):
	file_info = get_post_file(post_id)
	if file_info != None:
		return f"/file/{file_info[0]}/{file_info[1]}"
	return None

def get_post_file(post_id):
	sql = "SELECT A.id, A.name FROM files A, posts B WHERE B.id=:post" \
	" AND B.file_id=A.id AND A.is_deleted is not TRUE"
	result = db.session.execute(sql, {"post":post_id}).fetchone()
	if result == None:
		return None
	return (result[0], result[1])
	
def get_topic_by_id(topic_id):
	sql = "SELECT id, name, is_deleted FROM topics WHERE id=:id"
	result = db.session.execute(sql, {"id":topic_id})
	t = result.fetchone()
	if t == None or t[2]:    #is_deleted = 1
		return None
	return Topic(t[0], t[1])


def create_topic(topic_name, topic_desc):
	sql = "INSERT INTO topics VALUES (DEFAULT, :name, :desc, FALSE)"
	db.session.execute(sql, {"name":topic_name, "desc":topic_desc})
	db.session.commit()

def delete_topic(topic_id):
	sql = "UPDATE topics SET is_deleted=TRUE WHERE id=:id"
	db.session.execute(sql, {"id":topic_id})
	db.session.commit()

def delete_post(post_id):
	file_info = get_post_file(post_id)
	sql = "UPDATE posts SET is_deleted=TRUE WHERE id=:post_id"
	sql2 = "UPDATE files SET is_deleted=TRUE WHERE id=:file_id"

	db.session.execute(sql, {"post_id":post_id})
	if file_info != None:
		db.session.execute(sql2, {"file_id":file_info[0]})
	db.session.commit()
