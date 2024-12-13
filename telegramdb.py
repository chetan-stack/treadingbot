import sqlite3
from datetime import datetime


# Step 1: Connect to SQLite Database (or create it if it doesn't exist)
connection = sqlite3.connect('telegramdb.db')  # Creates a file named 'example.db'

# Step 2: Create a Cursor Object
cursor = connection.cursor()

# Step 3: Define SQL to Create a Table
create_table_query = """
CREATE TABLE IF NOT EXISTS userdata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incremented unique ID
    first_name TEXT NOT NULL,              -- First name (required)
    username TEXT,                  -- Username (must be unique)
    chat_id INTEGER NOT NULL UNIQUE,              -- Telegram chat ID (required)
    payment TEXT NOT NULL,                 -- Payment information (required)
    request TEXT NOT NULL,                 -- Request details (required)
    created_date_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Creation date with default value
);

"""

create_table_query_suggestion = """
CREATE TABLE IF NOT EXISTS suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incremented unique ID
    first_name TEXT NOT NULL,              -- First name (required)
    username TEXT,                  -- Username (must be unique)
    chat_id INTEGER NOT NULL UNIQUE,              -- Telegram chat ID (required)
    suggest TEXT NOT NULL,                         -- Request details (required)
    created_date_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Creation date with default value
);

"""

# Function to create a database connection
def create_connection(db_name):
    try:
        conn = sqlite3.connect(db_name)
        print("Connection successful!")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return None
# Step 4: Execute the Query
cursor.execute(create_table_query)
cursor.execute(create_table_query_suggestion)
# Function to insert data into the table
def insert_user_data(first_name, username, chat_id, payment, request):
    try:
        db_name = "telegramdb.db"
        conn = create_connection(db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO userdata (first_name, username, chat_id, payment, request) 
            VALUES (?, ?, ?, ?, ?)
        ''', (first_name, username, chat_id, payment, request))
        conn.commit()
        print("Data inserted successfully!")
    except sqlite3.IntegrityError as e:
        print(f"Error inserting data: {e}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

def insert_user_suggestion(first_name, username, chat_id, suggestion):
    try:
        db_name = "telegramdb.db"
        conn = create_connection(db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO suggestions (first_name, username, chat_id, suggest) 
            VALUES (?, ?, ?, ?)
        ''', (first_name, username, chat_id, suggestion))
        conn.commit()
        print("Data inserted successfully!")
    except sqlite3.IntegrityError as e:
        print(f"Error inserting data: {e}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
# Step 5: Commit the Changes and Close the Connection

#updatedata(1,'2')
def fetchdata():
    db_name = "telegramdb.db"
    conn = create_connection(db_name)
    fetch = conn.execute('SELECT * FROM userdata')
    data = []
    for row in fetch:
        data.append(row)
        # print(data)
    return data

def crate_fetch_suggestion():
    db_name = "telegramdb.db"
    conn = create_connection(db_name)
    fetch = conn.execute('SELECT * FROM suggestions')
    data = []
    for row in fetch:
        data.append(row)
        # print(data)
    return data



def fetch_user_by_username(id):
    try:
        db_name = "telegramdb.db"
        conn = create_connection(db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM userdata WHERE chat_id = ?
        ''', (id,))
        result = cursor.fetchone()
        if result:
            print("User data:", result)
            data = []
            for row in result:
                data.append(row)
            return data
        else:
            data = []
            print("No user found with that username.")
        return data
    except sqlite3.Error as e:
        print(f"Error fetching data: {e}")
        return None

def updateuser(id,data):
    db_name = "telegramdb.db"
    today_date = str(datetime.now().strftime('%Y-%m-%d'))
    conn = create_connection(db_name)
    query = 'UPDATE userdata SET request = ?, todate = ? WHERE id = ?'
    conn.execute(query,(data,today_date,id))
    conn.commit()

print("Database and table created successfully.")
if __name__ == "__main__":
    db_name = "telegramdb.db"
    conn = create_connection(db_name)
    if conn:
        # conn.execute('''ALTER TABLE userdata ADD COLUMN todate TEXT;''')

        # Insert sample data
        # insert_user_data(conn, "sohn", "sohn_doe", 12345678, "Paid", 1)
        conn.close()


connection.commit()
connection.close()
print(fetchdata())
print(crate_fetch_suggestion())
# print(fetch_user_by_username(1))
#
# def updaterequest():
#     data = fetchdata()
#     # print(data[0])
#     for item in data:
#         updateuser(item[0],0)
#     print(data)
# updaterequest()
# updateuser(1,0)

# updateuser(2027669179,0)