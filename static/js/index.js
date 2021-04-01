$(function() {
    $("#submit").click(function() {
        sessionStorage.setItem('username', $("#username").val());
    });
});


