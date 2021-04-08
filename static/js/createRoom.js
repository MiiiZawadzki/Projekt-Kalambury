function changeTurnLength(value) {
    $("#turn_length_p").text(value);
}
function changeTurnCount(value) {
    $("#turn_count_p").text(value);
}
$(function() {
    $("#turn_length_p").text($("#turn_length").val());
    $("#turn_count_p").text($("#turn_count").val());
});

