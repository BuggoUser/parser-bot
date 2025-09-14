import sqlite3

db, c = None, None

def start_db():
    global db, c
    db = sqlite3.connect('user_data.db')
    c = db.cursor()

def close_db():
    global db, c
    db.close()

def create_table():
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL UNIQUE, 
    active INTEGER NOT NULL DEFAULT 1, user_price INTEGER NOT NULL DEFAULT 0)''')
    db.commit()

def user_validate(user_id):
    result = c.execute('''SELECT active FROM users WHERE user_id = ?''', (user_id,)).fetchmany(1)
    return result[0][0]

def add_user(user_id):
    c.execute('''INSERT INTO users (user_id) VALUES (?)''', (user_id,))
    db.commit()

def update_users(user_id, active):
    c.execute('''UPDATE users SET active = ? WHERE user_id = ?''', (active, user_id, ))
    db.commit()

def get_user_id():
    all_users = c.execute('''SELECT user_id FROM users''').fetchall()
    return all_users

def get_all_users():
    users = c.execute('''SELECT user_id, active FROM users''').fetchall()
    return users

def get_price(user_id):
    c.execute("""SELECT user_price FROM users WHERE user_id = ?""", (user_id,))
    price_data = c.fetchmany()
    return price_data

if __name__ == '__main__':
    start_db()
    create_table()
    close_db()