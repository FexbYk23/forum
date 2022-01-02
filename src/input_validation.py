import string

def is_thread_name_valid(thread_name):
    return 0 < len(thread_name) < 100

def is_post_valid(post_text):
    return 0 < len(post_text) < 20000

def is_username_valid(username):
    for letter in username:
        if letter not in string.ascii_letters and letter not in string.digits:
            return False

    return 0 < len(username) < 20

def is_password_valid(password):
    return len(password) > 0

