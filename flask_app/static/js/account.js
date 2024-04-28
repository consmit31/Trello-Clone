function signUp() {
    var account_data = {
        'email': document.getElementById('email').value,
        'password': document.getElementById('password').value,
    }

    jQuery.ajax({
        url: '/processSignup',
        type: 'POST',
        data: account_data,
        success: function(data) {
            var Jdata = JSON.parse(data);
            console.log(Jdata);
            console.log(Jdata.success);
            if (Jdata.success === 1){
                console.log("Success");
                window.location.href = "/viewBoards";
            } else {
                console.log("Failure");
                window.location.href = "/account";
            }
        }
    });
}

function checkCredentials() {
    console.log("Checking Credentials")

    var account_data = {
        'email': document.getElementById('email').value,
        'password': document.getElementById('password').value,
    }

    jQuery.ajax({
        url: '/processLogin',
        type: 'POST',
        data: account_data,
        success: function(data) {
            var Jdata = JSON.parse(data);
            if (Jdata.success === 1) {
                console.log("Success");
                window.location.href = "/home";
            } else {
                console.log("Failure");
                window.location.href = "/account";
            }
        }
    });
}