# db_setup.py
import sqlite3

def create_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create the users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # NEW: Create the comments table if it doesn't exist
    # PASTE THE CODE FOR COMMENTS TABLE HERE:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL, -- Storing username directly for simplicity
            comment_text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    # END OF NEW CODE

    conn.commit()
    conn.close()
    print("Database 'users.db' and tables 'users' and 'comments' created successfully.") # UPDATED MESSAGE

if __name__ == '__main__':
    create_db()