# Author: Conner Smith <smit3423@msu.edu>

#--------------------------------------------------
# Import Requirements
#--------------------------------------------------
import os
from flask import Flask
from flask_socketio import SocketIO
from flask_failsafe import failsafe

socketio = SocketIO()

#--------------------------------------------------
# Create a Failsafe Web Application
#--------------------------------------------------
@failsafe
def create_app(debug=False):
    app = Flask(__name__)

    # Prevents issues with cached static files
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.debug = debug
    # Key used to cryptographically-sign the cookies used for storing the session data.
    app.secret_key = os.urandom(61).hex() #'AKWNF1231082fksejfOSEHFOISEHF24142124124124124iesfhsoijsopdjf'
	
    # Initialize database object
    from .utils.database.database import database
    db = database()
    db.createTables(purge=True)

    # Set up initial data
    # USERS
    db.createUser(email='owner@email.com', password='password', role='owner')
    db.createUser(email='guest@email.com', password='password', role='guest')
    db.createUser(email='jim@email.com', password='password', role='user')
    db.createUser(email='pam@email.com', password='password', role='user')
    db.createUser(email='mike@email.com', password='password', role='user')
    db.createUser(email='andy@email.com', password='password', role='user')
    # BOARDS
    db.createNewBoard("Project 1", 'owner@email.com', ['jim@email.com', 'pam@email.com','mike@email.com'])
    db.createNewBoard("Project 2", 'jim@email.com', ['andy@email.com', 'guest@email.com','mike@email.com'])
    # CARDS 
    db.createNewCard(board_id=1, list_type=1, content='test')
    db.createNewCard(board_id=1, list_type=2, content='test')
    db.createNewCard(board_id=1, list_type=3, content='test')
    db.createNewCard(board_id=1, list_type=3, content='test')
    db.createNewCard(board_id=2, list_type=1, content='test')
    db.createNewCard(board_id=2, list_type=1, content='test')
    db.createNewCard(board_id=2, list_type=2, content='test')
    db.createNewCard(board_id=2, list_type=3, content='test')




    # board/card data for testing

    
    socketio.init_app(app)

    with app.app_context():
        from . import routes
        return app