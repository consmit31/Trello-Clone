import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow

class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = ['boards', 'lists', 'cards', 'users', 'user_table_access']
        
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        if purge:
            for table in self.tables[::-1]:
                self.query(f"""DROP TABLE IF EXISTS {table}""")
            
        # Execute all SQL queries in the /database/create_tables directory.
        for table in self.tables:
            
            #Create each table using the .sql file in /database/create_tables directory.
            with open(data_path + f"create_tables/{table}.sql") as read_file:
                create_statement = read_file.read()
            self.query(create_statement)

    # def createNewBoard(self)
    

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    def createUser(self, email='me@email.com', password='password', role='user') -> bool:
        exists = self.query(f"SELECT email FROM users WHERE email = '{email}'")

        if not exists:
            self.query(f"INSERT INTO users (email, password, role) VALUES ('{email}', '{self.onewayEncrypt(password)}', '{role}')")
            return {'success': 1}
        else:
            return {'success': 0}
        
    def authenticate(self, email='me@email.com', password='password') -> bool:
        # Assume the password is already encrypted
        auth = (self.query(f"SELECT email FROM users WHERE email = '{email}' AND password = '{password}'"))
        if auth:
            return {'success': 1}
        else:
            return {'success': 0}
    

    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string


    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message


################################################################################
# CARD RELATED
################################################################################

    def createNewCard(self, board_id, list_type, content):
        print(f"Creating new card in board {board_id} with list type {list_type}")
        return self.query(f"INSERT INTO cards (board_id, list_type, content) VALUES ('{board_id}', '{list_type}', '{content}')")

    def editCard(self, card_id, content):
        self.query(f"UPDATE cards SET content = '{content}' WHERE card_id = '{card_id}'")

    def deleteCard(self, card_id):
        self.query(f"DELETE FROM cards WHERE card_id = '{card_id}'")

    def moveCard(self, card_id, new_list_type):
        self.query(f"UPDATE cards SET list_type = '{new_list_type}' WHERE card_id = '{card_id}'")

    def createNewBoard(self, name, user, others):
        # Create a new board in the database and get its ID
        self.query(f"INSERT INTO boards (name) VALUES ('{name}')")
        board_id = self.query(f"SELECT board_id FROM boards WHERE name = '{name}'")[0]['board_id']

        # Get the ID of the user who created the board
        user_email = user
        user_id = self.query(f"SELECT user_id FROM users WHERE email = '{user_email}'")[0]['user_id']

        #insert initial user into user_table_access table
        self.query(f"INSERT INTO user_table_access VALUES ('{user_id}', '{board_id}')")
       
        for user in others:
            id = self.query(f"SELECT user_id FROM users WHERE email = '{user}'")
            if id:
                id = id[0]['user_id']
                self.query(f"INSERT INTO user_table_access VALUES ('{id}', '{board_id}')")
            else:
                print(f"User {user} does not exist in the database")

    def getBoardData(self, board_id):
        data = { 'id': board_id, 'to_do': [], 'doing': [], 'completed': []}
        cards = self.query(f"SELECT * FROM cards WHERE board_id = '{board_id}'")

        data['name'] = self.query(f"SELECT name FROM boards WHERE board_id = '{board_id}'")[0]['name']

        for card in cards:
            type = card['list_type']
            if type == 1: # To do
                data['to_do'].append({'id': card['card_id'], 'content': card['content']})
            if type == 2: # In progress
                data['doing'].append({'id': card['card_id'], 'content': card['content']})
            if type == 3: # Done
                data['completed'].append({'id': card['card_id'], 'content': card['content']})

        return data