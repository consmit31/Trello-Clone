# Author: Conner Smith <smit3423@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect # type: ignore
from .utils.database.database  import database
from werkzeug.datastructures   import ImmutableMultiDict
from pprint import pprint
import json
import functools
from . import socketio
db = database()

######################################################################################
# ACCOUNT RELATED
#######################################################################################
def login_required(func):
    @functools.wraps(func)
    def secure_func(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("account", next=request.url))
        return func(*args, **kwargs)
    return secure_func
  

@app.route('/processSignup', methods=['POST', 'GET'])
def processSignup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = 'user'

        if email and password:  # Make sure the email and password are not empty
            # print(db.createUser(email, password, role)['success'])
            if db.createUser(email, password, role)['success']: # Check if the user already exists
                print('success')
                session['email'] = db.reversibleEncrypt('encrypt', email)
                status = {'success' : 1} # If user does not exist, redirect to the home page
            else:
                print('failure')
                status = {'success' : 0} # If user already exists, redirect to the account page

    return json.dumps(status)

@app.route('/processLogin', methods=['POST', 'GET'])
def processLogin():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))

    auth = db.authenticate(form_fields['email'], password=db.onewayEncrypt(form_fields['password']))

    if auth['success']:
        print(f"Authenticated: {form_fields['email']}")
        session['email'] = db.reversibleEncrypt('encrypt', form_fields['email'])
        status = {'success': 1}
    else:
        status = {'success': 0}

    return json.dumps(status)

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')

def getUser():
    return db.reversibleEncrypt('decrypt', session['email']) if 'email' in session else None

################################################################################################
# SOCKET RELATED
################################################################################################
@socketio.on('joined', namespace='/board')
def joined(message):
    print('Joined')
    join_room('main')

@socketio.on('editCard', namespace='/board')
def handle_edit_card(data):
    print(f"Handling edit card: {data}")
    print(data['id'])
    print(data['content'])

    emit('cardUpdated', data, room='main')

@socketio.on('removeCard', namespace='/board')
def handle_remove_card(data):
    print(f"Handling remove card: {data}")

    emit('cardRemoved', data, room='main')

@socketio.on('addCard', namespace='/board')
def handle_add_card(data):
    print(f"Handling add card: {data}")

    emit('cardAdded', data, room='main', broadcast=True)

@socketio.on('moveCard', namespace='/board')
def handle_move_card(data):
    print(f"Handling move card: {data}")

    emit('cardMoved', data, room='main', broadcast=True)

@socketio.on('message', namespace='/board')
def handle_move_card(data):
    data['sender'] = getUser()
    
    print(f"Handling message sent: {data}")

    emit('message', data, room='main', broadcast=True)

#######################################################################################
# BOARD RELATED
#######################################################################################

@app.route('/processBoardCreation', methods=['POST', 'GET'])
@login_required
def processBoardCreation():
        name = request.form['Name']
        others = request.form['users'].split(', ')
        user = getUser()

        db.createNewBoard(name, user, others)

        return json.dumps({'success' : 1})

@app.route('/processCardCreation', methods=['POST'])
@login_required
def processCardCreation():
    list_type = request.form['list_type']
    board_id = request.form['board_id']
    card_content = request.form['card_content']

    card_data = int(db.createNewCard(board_id, list_type, card_content)[0]['LAST_INSERT_ID()'])
    print(f"CARD DATA: {card_data}")   

    return json.dumps({'success' : 1, 'card_id': card_data})


@app.route('/processEditCard', methods=['POST'])
@login_required
def processEditCard():
    card_id = request.form['id']
    content = request.form['content']

    print(f"Editing card {card_id} with content {content}")

    db.editCard(card_id, content)

    return json.dumps({'success' : 1})

@app.route('/processRemoveCard', methods=['POST'])
@login_required
def processRemoveCard():
    card_id = request.form['id']
    print(f"Deleting card {card_id}")

    db.deleteCard(card_id)

    return json.dumps({'success' : 1})

@app.route('/processCardMove', methods=['POST'])
@login_required
def processCardMove():
    card_id = request.form['card_id']
    new_list_type = request.form['new_list_type']

    print(f"Moving card {card_id} to list {new_list_type}")

    db.moveCard(card_id, new_list_type)
   
    return json.dumps({'success' : 1})

@app.route('/navigateToBoard', methods=['POST'])
@login_required
def navigateToBoard():
    board_id = request.form['board_id']
    print(f"Navigating to board {board_id}")

    return json.dumps({'success' : 1, 'board_id' : board_id})

# Move this to database.py
def getBoardsForUser(user_email):
    user_id = db.query(f"SELECT user_id FROM users WHERE email = '{user_email}'")
    boards = []

    if user_id:
        user_id = user_id[0]['user_id']
        board_ids = db.query(f"SELECT board_id FROM user_table_access WHERE user_id = '{user_id}'")
        if board_ids:
            for board_id in board_ids:
                board_id = board_id['board_id']
                name = db.query(f"SELECT name FROM boards WHERE board_id = '{board_id}'")
                boards.append({'name' : name[0]['name'], 'id' : board_id})
        else:
            return None
    else:
        return None
    
    return(boards)

#######################################################################################
# OTHER 
#######################################################################################

@app.route('/')
def root():
    return redirect('/home')

@app.route('/home')
@login_required
def home():
    user = getUser()

    if user:
        return render_template('home.html', user = user)
    else:
        return render_template('account.html')

@app.route('/account')
def account():
    user = getUser()

    return render_template('account.html', user = user)

@app.route('/createBoard')
@login_required
def createBoard():
    user = getUser()

    return render_template('createBoard.html', user = user)

@app.route('/viewBoards')
@login_required
def viewBoards():
    user = getUser()
    boards = getBoardsForUser(user) # List of boards in the form of [{'name': name, 'id': 1}]
    if boards == None:
        return redirect('/createBoard') 

    return render_template('viewBoards.html', user = user, boards = boards)

@app.route('/board')
@login_required
def board():
    board_id = request.args.get('board_id')  # Get board_id from query parameter
    user = getUser()
    board_data = db.getBoardData(board_id)

    return render_template('board.html', user = user, board_data = board_data)

@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r