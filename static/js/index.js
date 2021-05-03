$(function() {
    $("#submitCreate").click(function() {
        sessionStorage.setItem('username', $("#username").val());
    });
    $("#submitJoin").click(function() {
        sessionStorage.setItem('username', $("#username").val());
    });
});


