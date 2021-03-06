var color = "black",
  thickness = 8;
var timer = null;
var timeEnd = false;
let user = sessionStorage.getItem("username");
$(function () {
  var flag,
    dot_flag = false,
    prevX,
    prevY,
    currX,
    currY = 0;
  var $canvas = $("#gameCanvas");
  var ctx = $canvas[0].getContext("2d");

  $canvas.on("mousemove mousedown mouseup mouseout", function (e) {
    if (user == who_draws) {
      prevX = currX;
      prevY = currY;
      currX = e.clientX - $canvas.offset().left;
      currY = e.clientY - $canvas.offset().top;

      if (e.type == "mousedown") {
        flag = true;
      }
      if (e.type == "mouseup" || e.type == "mouseout") {
        flag = false;
      }
      if (e.type == "mousemove") {
        if (flag) {
          socketIO.emit("draw", {
            draw_data: [
              { prevX: prevX, prevY: prevY },
              { currX: currX, currY: currY },
            ],
            color: color,
            thickness: thickness,
            user: user,
            who_draws: who_draws,
          });
          ctx.beginPath();
          ctx.moveTo(prevX, prevY);
          ctx.lineTo(currX, currY);
          ctx.strokeStyle = color;
          ctx.lineWidth = thickness;
          ctx.lineCap = "round";
          ctx.stroke();
          ctx.closePath();
        }
      }
    }
  });

  // switch color [green, blue, red, yellow, black, white]
  $(".color-button").on("click", function () {
    var color_value = $(this).attr("id");
    switch (color_value) {
      case "green":
        color = "green";
        break;
      case "blue":
        color = "blue";
        break;
      case "red":
        color = "red";
        break;
      case "yellow":
        color = "yellow";
        break;
      case "black":
        color = "black";
        break;
      case "white":
        color = "white";
        break;
    }
  });

  $("#clear").click(function () {
    if (user == who_draws) {
      var $canvas = $("#gameCanvas");
      var ctx = $canvas[0].getContext("2d");
      ctx.clearRect(0, 0, 1000, 700);
      socketIO.emit("clear", {
        user: user,
        who_draws: who_draws,
      });
    }
  });

  $(".pencil-button").on("click", function () {
    var t = $(this).attr("id");
    switch (t) {
      case "max-width":
        thickness = 16;
        break;
      case "medium-width":
        thickness = 8;
        break;
      case "small-width":
        thickness = 2;
        break;
    }
  });

  // get username set in index.html

  var who_draws = "";
  // connect with socket.io
  //    var socketIO = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
  var socketIO = io.connect("http://" + document.domain + ":" + location.port);

  //join to this room
  socketIO.emit("join", "");

  // receive messages
  socketIO.on("message", (data) => {
    // display alerts
    if (data.alert) {
      const alertDiv = document.createElement("div");
      alertDiv.classList.add("alert-message-container");
      const alertInnerDiv = document.createElement("div");
      alertInnerDiv.classList.add("alert-message");
      alertInnerDiv.innerHTML = data.alert;

      alertDiv.appendChild(alertInnerDiv);
      document.querySelector("#messageContainer").append(alertDiv);
    }
    // close to guess alert
    if (data.so_close) {
      const alertDiv = document.createElement("div");
      alertDiv.classList.add("alert-message-container");
      const alertInnerDiv = document.createElement("div");
      alertInnerDiv.classList.add("alert-message");
      alertDiv.style.backgroundColor = "rgba(50, 190, 110, 0.8)";
      alertInnerDiv.innerHTML = data.so_close;
      alertDiv.appendChild(alertInnerDiv);
      document.querySelector("#messageContainer").append(alertDiv);
    }

    // display incoming messages
    if (data.message_data) {
      const outerDiv = document.createElement("div");

      // display own messages
      if (data.username == user) {
        outerDiv.classList.add("own-message-container");
        const innerOwnDiv = document.createElement("div");
        innerOwnDiv.classList.add("own-message");
        innerOwnDiv.innerHTML = decodeURIComponent(
          "(" + data.time + "): " + data.message_data
        );
        const usernameBox = document.createElement("div");
        usernameBox.classList.add("own-username-box");
        usernameBox.innerHTML = data.username;
        innerOwnDiv.appendChild(usernameBox);

        outerDiv.appendChild(innerOwnDiv);
        document.querySelector("#messageContainer").append(outerDiv);
      }
      // display others messages
      else {
        outerDiv.classList.add("other-message-container");
        const innerOtherDiv = document.createElement("div");
        innerOtherDiv.classList.add("other-message");
        innerOtherDiv.innerHTML = decodeURIComponent(
          "(" + data.time + "): " + data.message_data
        );
        const usernameBox = document.createElement("div");
        usernameBox.classList.add("other-username-box");
        usernameBox.innerHTML = data.username;
        innerOtherDiv.appendChild(usernameBox);

        outerDiv.appendChild(innerOtherDiv);
        document.querySelector("#messageContainer").append(outerDiv);
      }
    }

    //move scrollbar while sending/receiving messages
    var messageWindow = document.querySelector("#messageContainer");
    messageWindow.scrollTop = messageWindow.scrollHeight;
  });

  socketIO.on("clear", (data) => {
    if (data.user == data.who_draws) {
      ctx.clearRect(0, 0, 1000, 700);
    }
  });

  socketIO.on("draw", (data) => {
    if (data.draw_data) {
        ctx.beginPath();
        ctx.moveTo(data.draw_data[0].prevX, data.draw_data[0].prevY);
        ctx.lineTo(data.draw_data[1].currX, data.draw_data[1].currY);
        ctx.strokeStyle = data.color;
        ctx.lineWidth = data.thickness;
        ctx.lineCap = "round";
        ctx.stroke();
        ctx.closePath();
    }
  });

  socketIO.on("correct", (data) => {
    const alertDiv = document.createElement("div");
    alertDiv.classList.add("alert-message-container");
    const alertInnerDiv = document.createElement("div");
    alertInnerDiv.classList.add("alert-message");
    alertDiv.style.backgroundColor = "rgba(82, 255, 0, 0.8)";
    alertInnerDiv.innerHTML =
      "Brawo! u??ytkownik " +
      data["username"].bold() +
      " odgad?? has??o:<br>" +
      data["word"].italics();

    alertDiv.appendChild(alertInnerDiv);
    document.querySelector("#messageContainer").append(alertDiv);

    clearInterval(timer);
  });

  socketIO.on("start_timer", (data) => {
    clearInterval(timer);
    if (data.time) {
      timer = setInterval(startTimer, 1000);
      $("#timer").text(data.time);
    }
  });

  socketIO.on("time_is_over", (data) => {
    if (data.word) {
      const alertDiv = document.createElement("div");
      alertDiv.classList.add("alert-message-container");
      const alertInnerDiv = document.createElement("div");
      alertInnerDiv.classList.add("alert-message");
      alertDiv.style.backgroundColor = "rgba(255, 134, 125, 0.8)";
      alertInnerDiv.innerHTML =
        "Czas si?? sko??czy??! has??em by??o: <br>" + data.word.italics();
      alertDiv.appendChild(alertInnerDiv);
      document.querySelector("#messageContainer").append(alertDiv);
    }
  });

  socketIO.on("who_draws", (data) => {
    if (data.username) {
      $("#drawer").text(data.username);
      who_draws = data.username;
      if (user == data.username) {
        $.getJSON(
          "/get_word",
          {
            room_id: $("#room_id").text(),
          },
          function (data) {
            if (data.word == "Sko??czy??y si??") {
              socketIO.emit("end_game", {
                room: $("#room_id").text(),
                sender: user,
              });
            } else {
              $("#word").text(data.word);
            }
          }
        );
        $(".word-container").css("visibility", "visible");
        $(".colors-container").css("visibility", "visible");
        $(".pencils-container").css("visibility", "visible");
        $("#typedMessage").attr("disabled", true);
        return false;
      } else {
        $("#word").text("...");
        $(".word-container").css("visibility", "hidden");
        $(".colors-container").css("visibility", "hidden");
        $(".pencils-container").css("visibility", "hidden");
        $("#typedMessage").prop("disabled", false);
      }
    }
  });

  socketIO.on("table_update", (data) => {
    if(data.table_data){
      $('#tableBody').empty();
      for (let index = 0; index < data.table_data.length; index++) {
        if (data.table_data[index][0] == user) {
          $('#tableBody').append("<tr style='background-color: aquamarine;'><th>"+(index+1)+'</th><td>'+data.table_data[index][0]+'</td><td>'+data.table_data[index][1]+'</td></tr>');
        }
        else{
        $('#tableBody').append('<tr><th>'+(index+1)+'</th><td>'+data.table_data[index][0]+'</td><td>'+data.table_data[index][1]+'</td></tr>');
        }
      }
    }
  });
  socketIO.on("stop_game", (data) => {
    if (data.winner) {
      clearInterval(timer);
      const alertDiv = document.createElement("div");
      alertDiv.classList.add("alert-message-container");
      const alertInnerDiv = document.createElement("div");
      alertInnerDiv.classList.add("alert-message");
      alertInnerDiv.innerHTML = "Gra dobieg??a ko??ca.<br>" + data.winner.bold();

      alertDiv.appendChild(alertInnerDiv);
      document.querySelector("#messageContainer").append(alertDiv);
      $("#typedMessage").prop("disabled", false);
    }
  });

  socketIO.on("skip", (data) => {
    if (data.username) {
      const alertDiv = document.createElement("div");
      alertDiv.classList.add("alert-message-container");
      const alertInnerDiv = document.createElement("div");
      alertInnerDiv.classList.add("alert-message");
      alertInnerDiv.innerHTML = "U??ytkownik: " + data.username + " zrezygnowa?? z rysowania";

      alertDiv.appendChild(alertInnerDiv);
      document.querySelector("#messageContainer").append(alertDiv);
    }
  });

  socketIO.on("kick_all", (data) => {
    alert("admin opu??ci?? pok??j - gra zosta??a przerwana");
    location.href = "/error/admin_left_room";
  });

  socketIO.on("single_tick", (data) => {
    if(data.time){
      $("#timer").text(data.time);
    }
  });

  // leave room
  $("#backToApp").click(function () {
      location.href = "/exit";
  });

  $("#delete").click(function (e) {
    e.preventDefault();
    $.getJSON(
      "/skip_round",
      {
        room_id: $("#room_id").text(),
        username: user,
      },
      function (data) {

      }
    );
  });

  $("#startGame").on("click", function (e) {
    e.preventDefault();
    $.getJSON(
      "/start_game",
      {
        room_id: $("#room_id").text(),
        username: user,
      },
      function (data) {
        $("#word").text(data.word);
      }
    );
    return false;
  });

  // send message after click on button
  $("#sendButton").click(function () {
    sendMessage();
  });

  // send message on enter hit
  var inputField = document.getElementById("typedMessage");
  inputField.addEventListener("keyup", function (event) {
    // keyCode 13 == Enter
    if (event.keyCode === 13) {
      sendMessage();
    }
  });

  function sendMessage() {
    // if message don't contain < or > character send normal message
    if (/^[^<>]*$/.test($("#typedMessage").val())) {
      socketIO.emit("message", {
        message_data: encodeURIComponent($("#typedMessage").val()),
      });
      $("#typedMessage").val("");
    }
    // if message contain < or > character send alert (prevent html injection)
    else {
      const p = document.createElement("p");
      p.innerHTML = "U??yto nieprawid??owych znak??w: '<' lub '>' !";
      p.classList.add("alertMessage");
      document.querySelector("#messageContainer").append(p);
      $("#typedMessage").val("");
    }
  }

  function startTimer() {
    var actual = $("#timer").text()-1;
    
    socketIO.emit("timer_tick", { room: $("#room_id").text(), sender: user, time: actual});
    if (actual == 0) {
      clearInterval(timer);
      socketIO.emit("time_end", { room: $("#room_id").text(), sender: user });
    }
  }

  // function actionAfterTimerStopped() {
  //     if (timeEnd == false) {
  //         //alert("Bomba na bani??, ko??czymy balet");
  //         socketIO.emit("time_end", { room: $("#room_id").text() });
  //     }
  // }

});

$(window).on('load', function(){
  var socketIO = io.connect("http://" + document.domain + ":" + location.port);
  socketIO.emit('load', 'load');
  $.getJSON(
    "/load_data_about_room",
    {
      room_id: $("#room_id").text()
    },
    function (data) {
      if(data.drawer_username){
        $("#drawer").text(data.drawer_username);
      }
    }
  );
});

function myConfirmation() {
  var socketIO = io.connect("http://" + document.domain + ":" + location.port);
  socketIO.emit("leave", "leave");
  return "aaa";
}

window.onbeforeunload = myConfirmation;
