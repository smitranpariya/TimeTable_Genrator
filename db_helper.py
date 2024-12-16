import sqlite3


class DatabaseHelper:
    def __init__(self, db_name="timetable.db"):
        """
        Initialize the DatabaseHelper class by connecting to the SQLite database.
        If the database file does not exist, it will be created.
        """
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """
        Create the required tables if they do not already exist.
        """
        # Table for general information
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS GeneralInfo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            academic_year TEXT,
            semester TEXT,
            class_name TEXT,
            start_end_time TEXT
        )
        """)
        
        # Table for classroom details
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ClassroomDetails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            num_classrooms INTEGER,
            classroom_numbers TEXT,
            lab_details TEXT,
            classroom_capacity INTEGER
        )
        """)
        
        self.conn.commit()

    def insert_general_info(self, academic_year, semester, class_name, start_end_time):
        """
        Insert a record into the GeneralInfo table.
        """
        try:
            self.cursor.execute("""
            INSERT INTO GeneralInfo (academic_year, semester, class_name, start_end_time)
            VALUES (?, ?, ?, ?)
            """, (academic_year, semester, class_name, start_end_time))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while inserting into GeneralInfo: {e}")

    def insert_classroom_details(self, num_classrooms, classroom_numbers, lab_details, classroom_capacity):
        """
        Insert a record into the ClassroomDetails table.
        """
        try:
            self.cursor.execute("""
            INSERT INTO ClassroomDetails (num_classrooms, classroom_numbers, lab_details, classroom_capacity)
            VALUES (?, ?, ?, ?)
            """, (num_classrooms, classroom_numbers, lab_details, classroom_capacity))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while inserting into ClassroomDetails: {e}")

    def fetch_general_info(self):
        """
        Retrieve all records from the GeneralInfo table.
        """
        try:
            self.cursor.execute("SELECT * FROM GeneralInfo")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred while fetching from GeneralInfo: {e}")
            return []

    def fetch_classroom_details(self):
        """
        Retrieve all records from the ClassroomDetails table.
        """
        try:
            self.cursor.execute("SELECT * FROM ClassroomDetails")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred while fetching from ClassroomDetails: {e}")
            return []

    def delete_all_records(self, table_name):
        """
        Delete all records from a given table.
        """
        try:
            self.cursor.execute(f"DELETE FROM {table_name}")
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while deleting records from {table_name}: {e}")

    def close(self):
        """
        Close the database connection.
        """
        try:
            self.conn.close()
        except sqlite3.Error as e:
            print(f"An error occurred while closing the connection: {e}")
