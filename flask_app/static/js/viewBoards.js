function displayBoard(board) {
    console.log("Displaying Board: " + board)
    var board_data = {
        'board_id': board
    }

    jQuery.ajax({
        url: '/navigateToBoard',
        type: 'POST',
        data: board_data,
        success: function(response) {
            // Redirect to the board page
            window.location.href = '/board?board_id=' + board;
        },
    });
}
