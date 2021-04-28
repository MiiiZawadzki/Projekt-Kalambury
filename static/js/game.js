var color = 'black', thickness = 16;

$(function() {
  var flag, dot_flag = false,
	prevX, prevY, currX, currY = 0;
  var $canvas = $('#gameCanvas');
  var ctx = $canvas[0].getContext('2d');

  $canvas.on('mousemove mousedown mouseup mouseout', function(e) {
    prevX = currX;
    prevY = currY;
    currX = e.clientX - $canvas.offset().left;
    currY = e.clientY - $canvas.offset().top;

    if (e.type == 'mousedown') {
        flag = true;

    }
    if (e.type == 'mouseup' || e.type == 'mouseout') {
      flag = false;
    }
    if (e.type == 'mousemove') {
      if (flag) {
        socketIO.emit('draw', {'draw_data': [{"prevX":prevX, "prevY":prevY}, {"currX":currX, "currY":currY}], 'color': color, 'thickness': thickness});
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
  });

  // switch color [green, blue, red, yellow, black, white]
  $(".color-button").on('click', function(){
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
    var $canvas = $('#gameCanvas');
    var ctx = $canvas[0].getContext('2d');
    ctx.clearRect(0, 0, 1000, 700);
    socketIO.emit('clear',"clear")
});

$(".pencil-button").on('click', function(){
    var t = $(this).attr("id");
    switch (t) {
        case "max-width":
            thickness = 22;
            break;
        case "medium-width":
            thickness = 16;
            break;
        case "small-width":
            thickness = 12;
            break;
    }
});

    // get username set in index.html
    user = sessionStorage.getItem("username");

    // connect with socket.io
//    var socketIO = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    var socketIO = io.connect("http://" + document.domain + ':' + location.port);

    //join to this room
    socketIO.emit('join',"");

    // receive messages
    socketIO.on('message', data => {
        // display alerts
        if (data.alert) {
            const p = document.createElement('p');
            p.innerHTML = data.alert;
            p.classList.add("alertP");
            document.querySelector('#messageContainer').append(p);
        }
        // display incoming messages
        if (data.message_data) {
            const p = document.createElement('p');
            // display own messages
            if (data.username == user){
                p.classList.add("ownMessage");
                p.innerHTML = decodeURIComponent("<b>You</b> (" +data.time+"): "+ data.message_data);
                document.querySelector('#messageContainer').append(p);
            }
            // display others messages
            else{
                p.classList.add("otherMessage");
                p.innerHTML = decodeURIComponent(data.username + " (" +data.time+"): "+ data.message_data);
                document.querySelector('#messageContainer').append(p);
            }
        }

        //move scrollbar while sending/receiving messages
        var messageWindow = document.querySelector("#messageContainer");
        messageWindow.scrollTop = messageWindow.scrollHeight;
    });

    socketIO.on('clear', data => {
        ctx.clearRect(0, 0, 1000, 700);   
    });

    socketIO.on('draw', data => {
        if(data.draw_data){
            ctx.beginPath();
            ctx.moveTo(data.draw_data[0].prevX ,  data.draw_data[0].prevY );
            ctx.lineTo(data.draw_data[1].currX, data.draw_data[1].currY);
            ctx.strokeStyle = data.color;
            ctx.lineWidth = data.thickness;
            ctx.lineCap = "round";
            ctx.stroke();
            ctx.closePath();
        }
    });

    socketIO.on('correct', data => {
            const p = document.createElement('p');
            p.innerHTML = "Brawo! użytkownik " + data["username"] + " odgadł hasło: "+ data["word"];
            p.classList.add("alertP");
            document.querySelector('#messageContainer').append(p);
    });


    // leave room
    $( "#backToApp" ).click(function() {
        var c = confirm("Are you sure you want to leave the room?");
        if (c == true) {
          socketIO.emit('leave',"leave");
          location.href='/exit';
        }
    });
    $('#startGame').on('click', function(e) {
        e.preventDefault()
        $.getJSON('/start_game',{
            room_id: $('#room_id').text(),
          }, function(data) {
            $('#word').text(data.word);
        });
        return false;
    });



    // emit leave when closing tab
    window.addEventListener("beforeunload", function (e) {
        socketIO.emit('leave',"leave");
    });

    // send message after click on button
    $( "#sendButton" ).click(function() {
        sendMessage();
    });

    // send message on enter hit
    var inputField = document.getElementById('typedMessage');
    inputField.addEventListener("keyup", function(event) {
        // keyCode 13 == Enter
        if (event.keyCode === 13) {
            sendMessage();
        }
    });

    function sendMessage(){
        // if message don't contain < or > character send normal message
        if (/^[^<>]*$/.test($('#typedMessage').val())){
            socketIO.emit('message', {'message_data': encodeURIComponent($('#typedMessage').val())});
            $('#typedMessage').val("")
        }
        // if message contain < or > character send alert (prevent html injection)
        else{
            const p = document.createElement('p');
            p.innerHTML = "Użyto nieprawidłowych znaków: '<' lub '>' !";
            p.classList.add("alertMessage");
            document.querySelector('#messageContainer').append(p);
            $('#typedMessage').val("")
        }
    }
});


