import sqlite3
import hashlib

DB_PATH = "users.db"


def init_db():
    """Initialize database and create all tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table with all fields
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            national_id TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Chat history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")


def hash_password(password: str):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(full_name, email, phone, national_id, username, password, role):
    """Register a new user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        hashed_pw = hash_password(password)
        cursor.execute("""
            INSERT INTO users 
            (full_name, email, phone, national_id, username, password, role)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (full_name, email, phone, national_id, username, hashed_pw, role))
        conn.commit()
        conn.close()
        return True, "Registration successful!"
    except sqlite3.IntegrityError as e:
        if "email" in str(e):
            return False, "Email already registered!"
        elif "username" in str(e):
            return False, "Username already taken!"
        elif "national_id" in str(e):
            return False, "National ID already registered!"
        return False, str(e)
    except Exception as e:
        return False, str(e)


def login_user(username: str, password: str):
    """Verify user login"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        hashed_pw = hash_password(password)
        cursor.execute("""
            SELECT id, full_name, email, phone, role 
            FROM users 
            WHERE username = ? AND password = ?
        """, (username, hashed_pw))
        user = cursor.fetchone()
        conn.close()
        if user:
            return True, {
                "id": user[0],
                "full_name": user[1],
                "email": user[2],
                "phone": user[3],
                "role": user[4]
            }
        else:
            return False, "Invalid username or password!"
    except Exception as e:
        return False, str(e)


def save_chat(username, full_name, role, query, response):
    """Save chat history"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_history 
            (username, full_name, role, query, response)
            VALUES (?, ?, ?, ?, ?)
        """, (username, full_name, role, query, response))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving chat: {e}")


def get_all_users():
    """Get all registered users"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, full_name, email, phone, national_id, 
                   username, role, created_at 
            FROM users 
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"Error: {e}")
        return []


def get_all_chats():
    """Get all chat history"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, full_name, role, query, response, timestamp
            FROM chat_history
            ORDER BY timestamp DESC
        """)
        chats = cursor.fetchall()
        conn.close()
        return chats
    except Exception as e:
        print(f"Error: {e}")
        return []


def get_user_chats(username):
    """Get chat history for specific user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT query, response, timestamp
            FROM chat_history
            WHERE username = ?
            ORDER BY timestamp DESC
            LIMIT 20
        """, (username,))
        chats = cursor.fetchall()
        conn.close()
        return chats
    except Exception as e:
        print(f"Error: {e}")
        return []


def delete_user(username):
    """Delete a user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        return True, "User deleted successfully!"
    except Exception as e:
        return False, str(e)


def get_users_by_role(role):
    """Get users by role"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, full_name, email, phone, username, role, created_at
            FROM users WHERE role = ?
            ORDER BY created_at DESC
        """, (role,))
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        print(f"Error: {e}")
        return []


if __name__ == "__main__":
    init_db()
    print("Database ready!")