import sqlite3

def upgrade_db():
    conn = sqlite3.connect('museum.db')
    cursor = conn.cursor()

    # Check columns
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]

    if 'phone_number' not in columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN phone_number VARCHAR")
            cursor.execute("CREATE UNIQUE INDEX ix_users_phone_number ON users (phone_number)")
            print("Added phone_number column")
        except Exception as e:
            print(f"phone_number error: {e}")
    else:
        print("phone_number already exists")

    if 'openid' not in columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN openid VARCHAR")
            cursor.execute("CREATE UNIQUE INDEX ix_users_openid ON users (openid)")
            print("Added openid column")
        except Exception as e:
            print(f"openid error: {e}")
    else:
        print("openid already exists")

    # Check bookings table
    cursor.execute("PRAGMA table_info(bookings)")
    booking_columns = [info[1] for info in cursor.fetchall()]

    if 'user_id' not in booking_columns:
        try:
            cursor.execute("ALTER TABLE bookings ADD COLUMN user_id INTEGER REFERENCES users(id)")
            cursor.execute("CREATE INDEX ix_bookings_user_id ON bookings (user_id)")
            print("Added user_id column to bookings")
        except Exception as e:
            print(f"user_id error: {e}")
    else:
        print("user_id already exists in bookings")

    cursor.execute("PRAGMA table_info(consultation)")
    consultation_columns = [info[1] for info in cursor.fetchall()]

    if 'cover' not in consultation_columns:
        try:
            cursor.execute("ALTER TABLE consultation ADD COLUMN cover VARCHAR(1024) NOT NULL DEFAULT ''")
            print("Added cover column to consultation")
        except Exception as e:
            print(f"cover error: {e}")
    else:
        print("cover already exists in consultation")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS volunteers (
            volunteer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            name VARCHAR(30) NOT NULL,
            phone VARCHAR(11) NOT NULL,
            email VARCHAR(100),
            status VARCHAR(20) NOT NULL DEFAULT '未审核',
            note TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )

    cursor.execute("PRAGMA table_info(volunteers)")
    volunteer_columns = [info[1] for info in cursor.fetchall()]

    if "created_at" not in volunteer_columns:
        try:
            cursor.execute("ALTER TABLE volunteers ADD COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP")
            print("Added created_at column to volunteers")
        except Exception as e:
            print(f"created_at error: {e}")

    if "updated_at" not in volunteer_columns:
        try:
            cursor.execute("ALTER TABLE volunteers ADD COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP")
            print("Added updated_at column to volunteers")
        except Exception as e:
            print(f"updated_at error: {e}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    upgrade_db()
