var windowWidth, windowHeight;
var navbarHeight; // height of the navbar located at the top of the page
var connectButton;
var clickedSpot;

window.onload = displayHotspots;

function displayHotspots() {
  windowWidth = window.innerWidth;
  windowHeight = window.innerHeight; 
  navbarHeight = document.getElementById("navbar").offsetHeight; 
  let wifilist = document.getElementById("wifilist");
  wifilist.style.top = navbarHeight + "px";
  let spots = document.querySelectorAll('[id^="hotspotNumber-"]');
  connectButton = document.getElementById("connect");
  setInterval(updater, 5000);
}

function clickedHotspot(id) {
  let spots = document.querySelectorAll('[id^="hotspotNumber-"]');
  for (spot of spots) {
    spot.style.background = "white";
    spot.setAttribute("chosen", "false")
  }
  clickedSpot = document.getElementById(id)
  clickedSpot.style.background = "lightblue";
  clickedSpot.setAttribute("chosen", "true")
  connectButton.removeAttribute("disabled");
}

function updater() {
  // The function sends the ajax request to obtain the latest hotspot data
  // in the JSON format.
  $.ajax({
    type: "GET",
    url: "update/",
    success: function (data) {
      console.log('Точки доступа обновлены!');
      updateTable(data);
    },
    error: function(data){
      console.log('Невозможно обновить точки доступа!');
    }
  });    
}

function updateTable(data) {
    // The function updates the rows representing the hotspots in the DOM.
    // First removes all the rows from the table except of the header.
    let chosenSpotSSID;
    currentSpots = document.querySelectorAll('[id^="hotspotNumber-"]');
    for (spot of currentSpots) {
        if (spot.getAttribute("chosen") == "true") {
            chosenSpotSSID = spot.getAttribute("ssid");
        }
        spot.remove();
    }

    // Then recreate the table using the new data.
    let table = document.getElementById('tableBody');
    if (data['status']){
        let keys = Object.keys(data['result'])
        let rowIndex = 0;
        connectButton.disabled = true;
        clickedSpot = null;
        for (key of keys) {
            let columnIndex = 0;
            // Insert next row to the table.
            let nextRow = table.insertRow(rowIndex);
            // Assign the id to the row.
            nextRow.setAttribute("id", "hotspotNumber-" + key);
            nextRow.setAttribute("ssid", data['result'][key]['SSID']);
            nextRow.setAttribute("onclick", "clickedHotspot(this.id)")
            // Insert the number of the row (hotspot)
            let nextColumn = nextRow.insertCell(columnIndex);
            nextColumn.innerHTML = key;

            if (data['result'][key]['SSID'] == chosenSpotSSID) {
                nextRow.setAttribute("chosen", "true");
                nextRow.style.background = "lightblue";
                connectButton.removeAttribute("disabled");
                clickedSpot = nextRow;
            }
            else {
                nextRow.setAttribute("chosen", "false")
            }

            let values = Object.keys(data['result'][key])
            // Populate the rest of the row.
            for (value of values) {
                columnIndex += 1;
                nextColumn = nextRow.insertCell(columnIndex);
                // Convert true or false value into the desired string.
                if (value == 'encryption') {
                    if (data['result'][key][value]) {
                        nextColumn.innerHTML = 'Да';
                    }
                    else {
                        nextColumn.innerHTML = 'Нет';
                    }
                }
                // Add the percent sign to the value of the quality cell.
                else if (value == 'quality') {
                    nextColumn.innerHTML = data['result'][key][value] + "%";
                }
                else {
                    nextColumn.innerHTML = data['result'][key][value];
                }
            }
            columnIndex += 1;
            nextColumn = nextRow.insertCell(columnIndex);
            nextColumn.innerHTML = "";
            rowIndex += 1;
        }
    }
}

$("#connect").click(function () {
  // The function sends the ajax request to connect to the chosen hotspot.
  openHotspotWindow(clickedSpot.getAttribute("ssid"));
});

function openHotspotWindow(ssid) {  
    let settingsWindowWidth = windowWidth * 0.5
    let settingsWindowHeight = windowHeight * 0.5
    let settingsWindow = window.open(
      "config?ssid=" + ssid, 
      "toolbar=no,location=no,directories=no,status=no,menubar=no,scrollbars=yes,resizable=yes",
      "width=1024,height=576"
      )
    //settingsWindow.console.log('This window has been opened!')
}

function connectToSelectedSpot() {
  $.ajax({
    type: "GET",
    url: "connect/",
    success: function (data) {
      alert('Успешное подключение к точке доступа!');
    },
    error: function(data){
      alert('Невозможно подключиться к точке доступа!');
    }
  });
};
