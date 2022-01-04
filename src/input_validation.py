import string

def is_thread_name_valid(thread_name):
    if len(thread_name) <= 0:
        return (False, "Keskusteluketjun nimi ei saa olla tyhjä")
    
    if len(thread_name) > 100:
        return (False, "Keskusteluketjun nimi on liian pitkä")

    return (True,"")
    

def is_post_valid(user_id, post_text):
    if user_id == None:
        return (False, "Viestin voi lähettää vain kirjautunut käyttäjä")

    if len(post_text) <= 0:
        return (False, "Viesti ei saa olla tyhjä")
    
    if len(post_text) > 20000:
        return (False, "Viesti on liian pitkä")

    return (True,"")
    

def is_username_valid(username):
    for letter in username:
        if letter not in string.ascii_letters and letter not in string.digits:
            return (False, "Nimi sisältää kiellettyn merkin: " + letter)
    
    if len(username) <= 0:
        return (False, "Nimi ei saa olla tyhjä")

    if len(username) > 20:
        return (False, "Nimi ei saa olla yli 20 merkkiä pitkä")
    
    return (True,"")

def is_password_valid(password):
    if len(password) <= 0:
        return (False, "Salasana ei saa olla tyhjä")
    return (True,"")

def is_registration_valid(username, password, password2):
    if password != password2:
        return (False, "Antamasi salasanat eivät täsmää")

    a = is_username_valid(username)
    if a[0]:
        return is_password_valid(password)
    return a

