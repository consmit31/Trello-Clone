function createBoard() {
    console.log("Creating Board")
    var account_data = {
        'Name': document.getElementById('boardName').value,
        'users': document.getElementById('users').value,
    }

    console.log(account_data);

    jQuery.ajax({
        url: '/processBoardCreation',
        type: 'POST',
        data: account_data,
        success: function(data) {
            var Jdata = JSON.parse(data);
            if (Jdata.success === 1){
                console.log("Success");
                window.location.href = "/home";
            } else {
                console.log("Failure");
                window.location.href = "/createBoard";
            }
        }
    });
}