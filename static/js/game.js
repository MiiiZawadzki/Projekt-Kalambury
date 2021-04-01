$(function() {
var flag, dot_flag = false,
	prevX, prevY, currX, currY = 0,
	color = 'black', thickness = 20;
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
        socketIO.emit('draw', {'draw_data': [{"prevX":prevX, "prevY":prevY}, {"currX":currX, "currY":currY}]});
        ctx.beginPath();
        ctx.moveTo(prevX, prevY);
        ctx.lineTo(currX, currY);
        ctx.strokeStyle = color;
        ctx.lineWidth = thickness;
        ctx.stroke();
        ctx.closePath();
      }
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

    socketIO.on('draw', data => {
        if(data.draw_data){
            console.log(data.draw_data[0].prevX + ", "+ data.draw_data[0].prevY + " | " + data.draw_data[1].currX + ", "+ data.draw_data[1].currY);
            ctx.beginPath();
            ctx.moveTo(data.draw_data[0].prevX ,  data.draw_data[0].prevY );
            ctx.lineTo(data.draw_data[1].currX, data.draw_data[1].currY);
            ctx.strokeStyle = color;
            ctx.lineWidth = thickness;
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
        $.getJSON('/start_game',
            function(data) {
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
            p.innerHTML = "An illegal characters '<' or '>' were used!";
            p.classList.add("alertMessage");
            document.querySelector('#messageContainer').append(p);
            $('#typedMessage').val("")
        }
    }


});


