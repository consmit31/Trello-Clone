document.addEventListener("DOMContentLoaded", function() {
    const chatTab = document.getElementById("chat-tab");
    const chatBox = document.getElementById("chat-box");
    const chatClose = document.getElementById("chat-close");
    const chatInput = document.getElementById("message-input");
    const chatSend = document.getElementById("send-button");
  
    // Show/hide chat box when clicking on the chat tab
    chatTab.addEventListener("click", function() {
      chatBox.style.display = chatBox.style.display === "none" ? "block" : "none";
    });
  
    // Close chat box when clicking on the close button
    chatClose.addEventListener("click", function() {
      chatBox.style.display = "none";
    });

    chatSend.addEventListener("click", function() {
        var message = $('#message-input').val();
        console.log("sendMessage(): " + message)
        if (message.trim() !== '') {
            socket.emit('message', { 'msg': message });
            $('#message-input').val('');
        }
    });
  });

