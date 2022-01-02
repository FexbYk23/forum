
CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	name TEXT UNIQUE,
	password_hash TEXT,
	is_admin BOOLEAN
);

CREATE TABLE topics (
	id SERIAL PRIMARY KEY,
	name TEXT,
	description TEXT,
	is_deleted BOOLEAN
);

CREATE TABLE threads (
	id SERIAL PRIMARY KEY,
	name TEXT,
	topic INTEGER REFERENCES topics,
	is_deleted BOOLEAN
);

CREATE TABLE posts (
	id SERIAL PRIMARY KEY,
	content TEXT,
	poster INTEGER REFERENCES users,
	thread INTEGER REFERENCES threads,
	time TIMESTAMP,
	is_deleted BOOLEAN
);

CREATE TABLE files (
	id SERIAL PRIMARY KEY,
	name TEXT,
	url TEXT,
	data BYTEA,
	is_deleted BOOLEAN
);
