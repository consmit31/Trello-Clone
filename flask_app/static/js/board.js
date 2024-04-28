let isEditing = false;
var socket;
$(document).ready(function() {
    const queryString = window.location.search;
    const params = new URLSearchParams(queryString);
    const boardId = params.get('board_id');

    socket = io.connect('http://' + document.domain + ':' + location.port + '/board?board_id=' + boardId);

    socket.on('connect', function() {
        console.log('(S)Connected to server');
        socket.emit('joined', {});
    });

    socket.on('cardUpdated', function(data) {
        console.log('(S) Card updated: ' + data.id);

        var card_div = $('#' + data['id'] + '.card')
        var card_content_div = card_div.find('.card-content');
        card_content_div.text(data['content']);
    });

    socket.on('cardRemoved', function(data) {
        console.log('(S) Card removed: ' + data.id);
        var card_div = $('#' + data['id'] + '.card')

        card_div.remove();
    });

    socket.on('cardMoved', function(data) {
        console.log(data);
        console.log('(S) Card moved: ' + data.card_id);

        var list = document.getElementById(data.new_list_id);
        console.log("(S) target: " + list);
        list.appendChild(document.getElementById(data.card_id));
    });

    socket.on('message', function(data) {
        console.log('(S)Message: ' + data.msg);

        var tag = document.createElement("p");
        var text = document.createTextNode(data.sender + ": " + data.msg);
        
        var chat = document.querySelector('#' + data.chat_id);
        var element = chat.querySelector("#chat-content")
        tag.appendChild(text);
        element.appendChild(tag);
        $('#chat-content').scrollTop($('#chat-content')[0].scrollHeight);
    });

    socket.on('cardAdded', function(data) {
        console.log('(S)Card added: ' + data.card_id + " with content: " + data.card_content);

        var existing_card = document.getElementById("card-"+data.card_id)
        if (existing_card!= null) {
            return;
        }

        switch (data.list_type) {
            case 1:
                var list_name = "to-do-list";
                break;
            case 2:
                var list_name = "doing-list";
                break;
            case 3:
                var list_name = "completed-list";
                break;
        }
    
        var list_container = document.getElementsByClassName('list-container')[0]; 
        var list = list_container.querySelector('#' + list_name);
    
        var new_card = document.createElement('div');
        new_card.className = 'card';
    
        var card_content = document.createElement('div');
        card_content.className = 'card-content';
        card_content.contentEditable = "true";
        card_content.innerText = data.card_content;
        
        var buttons = document.createElement('div');
        buttons.className = 'card-buttons';
    
        var delete_button = document.createElement('input');
        delete_button.type = "button";
        delete_button.id = "deletecard";
        delete_button.value = "remove card";
        delete_button.addEventListener("click", function() {
            removeCard(this, data.card_id);
        });
    
        var edit_button = document.createElement('input');
        edit_button.type = "button";
        edit_button.id = "editcard";
        edit_button.value = "edit card";
        edit_button.addEventListener("click", function() {
            editCard(this, data.card_id);
        });
    
        buttons.appendChild(delete_button);
        buttons.appendChild(edit_button);
    
        new_card.appendChild(card_content);
        new_card.appendChild(buttons);
        list.appendChild(new_card);
    });

});

function editCard(button, card_id) {
    console.log("Editing card: " + card_id);

    var card_content_div = button.parentNode.parentNode.querySelectorAll('.card-content')[0];

    if (card_content_div.contentEditable === "false") {
        card_content_div.contentEditable = "true";
        card_content_div.focus();
        button.value = "confirm";
        console.log("Editing card from: " + card_content_div.innerText);

    } else {
        card_content_div.contentEditable = "false";
        button.value = "edit card";
        const newContent = card_content_div.innerText;

        console.log("Confirming card edit: " + newContent);
        $.ajax({
            url: '/processEditCard',
            type: 'POST',
            data: { id: card_id, content: card_content_div.innerText }
        });

        socket.emit("editCard", { id: button.parentNode.parentNode.id, content: newContent });
    }
}

function removeCard(button, card_id) {
    var card_div = button.parentNode.parentNode;

    console.log("Removing card: " + card_id);

    $.ajax({
        url : '/processRemoveCard',
        type: 'POST',
        data: {id: card_id}
    });

    card_div.remove();

    socket.emit("removeCard", { id: button.parentNode.parentNode.id });
}

function addNewCard(board_id, list_type) {
    console.log("Adding card to list: " + list_type + " on board: " + board_id);
    var list_data = {
        'list_type': list_type,
        'board_id': +board_id
    }

    switch (list_type) {
        case 1:
            var list_name = "to-do-list";
            break;
        case 2:
            var list_name = "doing-list";
            break;
        case 3:
            var list_name = "completed-list";
            break;
    }

    var list_container = document.getElementsByClassName('list-container')[0]; 
    var list = list_container.querySelector('#' + list_name);

    var new_card = document.createElement('div');
    new_card.className = 'card';
    new_card.draggable = true;
    new_card.ondragstart = drag(event);

    var card_content = document.createElement('div');
    card_content.className = 'card-content';
    card_content.contentEditable = "true";
    card_content.innerText = "";
    
    var buttons = document.createElement('div');
    buttons.className = 'card-buttons';

    var delete_button = document.createElement('input');
    delete_button.type = "button";
    delete_button.id = "deletecard";
    delete_button.value = "remove card";

    var edit_button = document.createElement('input');
    edit_button.type = "button";
    edit_button.id = "editcard";
    edit_button.value = "edit card";

    buttons.appendChild(delete_button);
    buttons.appendChild(edit_button);

    new_card.appendChild(card_content);
    new_card.appendChild(buttons);
    list.appendChild(new_card);

    card_content.focus();

    card_content.addEventListener('keypress', function(e){
        if (e.key === 'Enter'){
            card_content.contentEditable = "false";
            card_content.innerText = card_content.textContent;
            card_content.blur();

            $.ajax({
                url: '/processCardCreation',
                type: 'POST',
                data: {'list_type': +list_type,
                       'board_id': board_id, 
                       'card_content': card_content.textContent},
                success: function(data) {
                    var Jdata = JSON.parse(data);
                    var card_id = Jdata.card_id;
                    new_card.id = "card-" + card_id;

                    delete_button.addEventListener("click", function() {
                        removeCard(this, card_id);
                    });

                    edit_button.addEventListener("click", function() {
                        editCard(this, card_id);
                    });

                    socket.emit("addCard", {card_id: card_id, card_content: card_content.textContent, list_type: list_type});
                }
            });    
        }
    });
}

function allowDrop(event){
    event.preventDefault();
}

function drag(event){
    event.dataTransfer.setData("text", event.target.id);
}

function drop(event){
    event.preventDefault();
    var card_id = event.dataTransfer.getData('text');
    console.log("Target: " + event.target);
    event.target.appendChild(document.getElementById(card_id));

    var target_list = event.target.id;    
    switch (target_list) {
        case "to-do-list":
            list_type = 1;
            break;
        case "doing-list":
            list_type = 2;
            break;
        case "completed-list":
            list_type = 3;
            break;
    }

    var card_id_num = card_id.slice(5);
    $.ajax({
        url: '/processCardMove',
        type: 'POST',
        data: {'new_list_type': +list_type,
               'card_id': card_id_num}
    });

    socket.emit('moveCard', {'card_id': card_id, 'new_list_id': target_list});
}

function closeChat(closeButton){
var chatBox = document.getElementsByClassName('chat-box')[0];
chatBox.style.display = 'none';
}

function openChat(){
var chatBox = document.getElementsByClassName('chat-box')[0];
chatBox.style.display = 'block';
}

function sendMessage(sendButton){
var message = $('#message-input').val();
var chat_id = sendButton.parentNode.parentNode.id;
if (message.trim() !== '') {
    socket.emit('message', { 'msg': message, 'chat_id': chat_id });
    $('#message-input').val('');
}
}