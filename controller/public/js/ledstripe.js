
var baseUrl = window.location.protocol + "//" + window.location.host;

function get(url) {
    console.log("Url:", url);
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", url, false);
    xhttp.send();
};

function getResponse(url, callback) {
    console.log("Url:", url);
    var xhttp = new XMLHttpRequest();
    xhttp.responseType = 'json';
    xhttp.open("GET", url, true);
    xhttp.onload  = function() {
        var jsonResponse = xhttp.response;
        console.log("RESPONSE from", url, "=", jsonResponse);
        if(jsonResponse != null){
            callback(jsonResponse);
        }
     };
    xhttp.send();
};


function brightness(value, roomName) {
    get(baseUrl + "/" + roomName + "/brightness?value=" + (value / 100.0));
};


export function togglePower(power, roomName) {
    console.log("Toggling power of room", roomName, "to:", power);
    if (power) {
        brightness(100.0, roomName);
    }
    else {
        brightness(0.0, roomName);
    }
}

export function setColor(color, roomName) {
    console.log("Setting color to", color.r, color.g, color.b);
    get(baseUrl + "/" + roomName + "/color?red=" + color.r + "&green=" + color.g + "&blue=" + color.b);
}

export function setAlarm(time, roomName){
    console.log("Activating alarm at", time);
    get(baseUrl + "/" + roomName + "/setalarm?time=" + time);
}

export function cancelAlarm(roomName){
    console.log("Cancelling alarm!");
    get(baseUrl + "/" + roomName + "/setalarm?cancel=" + 1);
}