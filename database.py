import os
import sqlite3


class Highscore_Table():
    conn = None
    cursor = None
    db_file = 'highscore.db'
    isFile = os.path.isfile(db_file)

    def __init__(self):
        self.init_table()


    def open_conn_db(self):
        # open connection with the database
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

    def close_conn_db(self):
        # save database and close the connection
        self.conn.commit()
        self.conn.close()   

    def init_table(self):
        '''
        create the database file
        if it doesn't exist
        '''

        if self.isFile == False:

            self.open_conn_db()

            # Create a Table
            self.cursor.execute("""CREATE TABLE players (

                player_name text,
                highest_score integer

            )
            """)

            self.close_conn_db()

    def add_score(self, name, score):
        check_name = self.check_name_in_DB(name)
        self.open_conn_db()

        score_d = [
                (name,score)
            ]

        if check_name[0] == False:

            self.cursor.executemany("INSERT INTO players VALUES (?,?)", score_d)

        elif check_name[0] == True and check_name[1] < score:
            
            self.cursor.execute(f"DELETE FROM players WHERE highest_score = {check_name[1]}")
            self.cursor.executemany("INSERT INTO players VALUES (?,?)", score_d)


        self.close_conn_db()

    def del_record(self, name):
        self.open_conn_db()
        self.cursor.execute("DELETE FROM players WHERE player_name = (?)",name)
        self.close_conn_db()

    def order_table(self):
        self.open_conn_db()
        self.cursor.execute("SELECT * FROM players ORDER BY highest_score DESC")
        data = self.cursor.fetchall()
        self.close_conn_db()
        return data

    def check_name_in_DB(self, p_name):
        '''
        check if the name already exist in the database
        it return a tuble of False and 0 if the name is
        new, and it return True and the old score if the
        name already exist in the table
        
        '''

        self.open_conn_db()
        self.cursor.execute("SELECT * FROM players")

        items = self.cursor.fetchall()

        for item in items:

            if item[0] == p_name:
                self.close_conn_db()
                return True, item[1]

        self.close_conn_db()
        return False , 0
        

    def get_data(self):
        '''
        just a function to test
        '''
        self.open_conn_db()
        self.cursor.execute("SELECT * FROM players")
        data = self.cursor.fetchall()
        self.close_conn_db()

        return data

class Questions_Table():
    conn = None
    cursor = None
    db_file = 'questions.db'
    isFile = os.path.isfile(db_file)
    def __init__(self):
        self.init_table()

    def open_conn_db(self):
        # open connection with the database
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

    def close_conn_db(self):
        # save database and close the connection
        self.conn.commit()
        self.conn.close()  

    def init_table(self):
        '''
        create the database file
        if it doesn't exist
        '''

        if self.isFile == False:

            self.open_conn_db()

            # Create a Table
            self.cursor.execute("""CREATE TABLE questions (

                question text,
                right_ans text,
                ans_1 text,
                ans_2 text,
                ans_3 text,
                points integer

            )
            """)

            self.close_conn_db()
    
    def add_question(self, q, rans, ans1, ans2, ans3, p):

        question_d = [
            (q,rans,ans1,ans2,ans3,p)
        ]
        self.open_conn_db()

        self.cursor.executemany("""INSERT INTO questions VALUES (?,?,?,?,?,?)""", question_d)

        self.close_conn_db()

    def get_data(self):
        '''
        get data from database in form of tuble inside list
        '''
        self.open_conn_db()
        self.cursor.execute("SELECT * FROM questions")
        d = self.cursor.fetchall()
        self.close_conn_db()
        return d

    def s_get_data(self):
        '''
        get data from database in form of tuble inside list but with table id
        '''
        self.open_conn_db()
        self.cursor.execute("SELECT rowid, * FROM questions")
        d = self.cursor.fetchall()
        self.close_conn_db()
        return d

    def del_record(self):
        self.open_conn_db()
        self.cursor.execute("DELETE from questions WHERE rowid")
        self.close_conn_db()

