window.onload = setWidgetsSizes;

var clickedElementID;
var widgets = [];
var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
var windowWidth, windowHeight;
var areaWidth, areaHeight;
var navbarHeight; // height of the navbar located at the top of the page
var borderSize = 5; // width of the border of the setupfield
var widgetsListCount;
var initialization = true;
const csrftoken = getCookie('csrftoken');

function setWidgetsSizes() {
  widgetsListCount = 0;

  windowWidth = window.innerWidth;
  windowHeight = window.innerHeight; 

  navbarHeight = document.getElementById("navbar").offsetHeight; 
  let setupfield = document.getElementById("setupfield");

  // Dimensions of the area that represents the Smart Mirror Mark II
  // The shape is 16 by 9.
  areaHeight = windowHeight - navbarHeight;
  areaWidth = areaHeight * 16 / 9;

  setupfield.style.top = navbarHeight + "px";
  setupfield.style.height = areaHeight + "px";
  setupfield.style.width = areaWidth + "px";

  let widgetsList = document.getElementById("widgetsList");
  widgetsList.style.top = navbarHeight + "px";
  widgetsList.style.height = areaHeight + "px";
  widgetsList.style.width = windowWidth - areaWidth + "px";
  widgetsList.style.left = areaWidth + "px";
  let widgetsNode = document.querySelectorAll('[id^="widget-"]');
    for (widgetNode of widgetsNode) {
      let element = document.getElementById(widgetNode.id);
      if (initialization) {
        widgets.push(element.id)
      }
      if (widgetNode.getAttribute("show") == "True") {
        element.style.left = setupfield.offsetLeft + areaWidth * parseFloat(element.getAttribute("relx").replace(',', '.')) / 100 + "px"
        element.style.top = navbarHeight + areaHeight * parseFloat(element.getAttribute("rely").replace(',', '.')) / 100 + "px"
        element.style.height = areaHeight * parseFloat(element.getAttribute("height").replace(',', '.')) / 100 + "px"
        element.style.width = areaWidth * parseFloat(element.getAttribute("width").replace(',', '.')) / 100 + "px"
      }
      else {
        element.className = "widget-not-shown"
        element.style.left = setupfield.offsetLeft + setupfield.offsetWidth + "px";
        element.style.top = navbarHeight + 50 + widgetsListCount * 50 + "px";
        element.style.width = widgetsList.getBoundingClientRect().width - borderSize * 2 + "px";
        element.style.height = 30 + "px"
        //document.getElementById("widgetsList").appendChild(element);
        widgetsListCount += 1;
      }
    }
    initialization = false;
  addListeners(); 
}

function addListeners() {
    //document.getElementById('widget-2').addEventListener('mousedown', mouseDown, false);
    window.addEventListener('mousedown', mouseDown, false);
    window.addEventListener('mouseup', mouseUp, false);
}

function mouseUp(e) {
    window.removeEventListener('mousemove', divMove, true);
    let div = document.getElementById(clickedElementID);
    if (div == null) {
      return null
    }
    let elemAbsolutePosition = div.getBoundingClientRect();
    // If an element is released inside the setup field.
    if (e.clientX > setupfield.offsetLeft && 
        e.clientX < setupfield.offsetLeft + setupfield.offsetWidth &&
        e.clientY > navbarHeight  && 
        e.clientY  < windowHeight) {
      if (div.className == "widget-not-shown") {
        div.className = "widget";
        div.style.left = setupfield.offsetLeft + areaWidth * parseFloat(div.getAttribute("relx").replace(',', '.')) / 100 + "px"
        div.style.top = 0 + navbarHeight + areaHeight * parseFloat(div.getAttribute("rely").replace(',', '.')) / 100 + "px"
        div.style.height = areaHeight * parseFloat(div.getAttribute("height").replace(',', '.')) / 100 + "px"
        div.style.width = areaWidth * parseFloat(div.getAttribute("width").replace(',', '.')) / 100 + "px"
        div.setAttribute("show", "True")
        widgetsListCount -= 1;
      }
    }
    // If an element is released inside the widgets list field.
    else if (e.clientX > setupfield.offsetLeft + setupfield.offsetWidth && 
        e.clientX < windowWidth &&
        e.clientY > navbarHeight && 
        e.clientY < windowHeight) {
      if (div.className == "widget") {
        div.className = "widget-not-shown";  
        div.style.left = setupfield.offsetLeft + setupfield.offsetWidth + "px";
        div.style.top = navbarHeight + 50 + widgetsListCount * 50 + "px";
        div.style.width = widgetsList.getBoundingClientRect().width - borderSize * 2 + "px";
        div.style.height = 30 + "px"       
        div.setAttribute("show", "False")
        widgetsListCount += 1;  
      }
    }
}

function mouseDown(e) {
  if (widgets.includes(e.target.id)) {
    clickedElementID = e.target.id;
    window.addEventListener('mousemove', divMove, true);
    // get the mouse cursor position at startup:
    pos3 = e.clientX;
    pos4 = e.clientY;
  }
  else if (widgets.includes(e.target.parentNode.id)) {
    clickedElementID = e.target.parentNode.id;  // to get the element tag name alone
    window.addEventListener('mousemove', divMove, true);
    // get the mouse cursor position at startup:
    pos3 = e.clientX;
    pos4 = e.clientY;   
  }
  else if (e.target.id.includes('widg-resizer')) {
    resizeDiv(e.target.id)
  }
  else {
    clickedElementID = null;
  }  
}

function divMove(e) {
  var div = document.getElementById(clickedElementID);
  pos1 = pos3 - e.clientX;
  pos2 = pos4 - e.clientY;
  pos3 = e.clientX;
  pos4 = e.clientY;
  let elemAbsolutePosition = div.getBoundingClientRect();

  let left = (elemAbsolutePosition.left - pos1);
  if (left > setupfield.offsetLeft + 0 && 
      left + elemAbsolutePosition.width < windowWidth - 0) {
    div.style.left = left + "px"
  }

  let top = (elemAbsolutePosition.top - pos2);   
  if (top > navbarHeight + 0 
      && top + elemAbsolutePosition.height < windowHeight - 0){
    div.style.top = top + "px"
  }
}

$("#apply").click(function () {
  $.ajax({
    type: "POST",
    url: "apply/",
    dataType: "json",
    headers: {
                'X-CSRFToken': csrftoken 
              },
    data: {"widgets" :formResponse()},
    success: function (data) {
      alert('Конфигурация успешно применена!');
    },
    error: function(data){
      alert('Невозможно применить конфигурацию!');
    }
  });
});

$("#cancel").click(function () {
  $.ajax({
    type: "GET",
    url: "cancel/",
    success: function (data) {
      console.log('Применение настроек отменено')
    }
  });
});

function formResponse() {
  let response = {};
  for (widget of widgets) {
    let elem = document.getElementById(widget);
    let temp;
    if (elem.getAttribute("show") == "True") {
      let relx = ((parseFloat(elem.style.left) - setupfield.offsetLeft) / parseFloat(areaWidth) * 100).toPrecision(10)
      let rely = ((parseFloat(elem.style.top) - navbarHeight) / parseFloat(areaHeight) * 100).toPrecision(10)
      let width = (parseFloat(elem.style.width) / parseFloat(areaWidth)* 100).toPrecision(10)
      let height = (parseFloat(elem.style.height) / parseFloat(areaHeight) * 100).toPrecision(10)
      temp = {
        "relx": relx,
        "rely": rely,
        "width": width,
        "height": height,
        "show": true
      };
    }
    else {
      temp = {
        "relx": false,
        "rely": false,
        "width": false,
        "height": false,
        "show": false
      };
    }

    response[widget] = temp;
    console.log(JSON.stringify(response))
  }
  return JSON.stringify(response);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function resizeDiv(id) {
  let resizer = document.getElementById(id);
  let currentWidget = resizer.parentNode.parentNode;
  let aspectRatio = currentWidget.offsetWidth / currentWidget.offsetHeight
  window.addEventListener('mousemove', resize);
  window.addEventListener('mouseup', stopResize)
    
  function resize(e) {    
    let newHeight = e.pageY - currentWidget.getBoundingClientRect().top
    let newWidth;
    if (currentWidget.getAttribute("keepAspectRatio") == "True") {   
      newWidth = newHeight * aspectRatio
    }

    else {
      newWidth = e.pageX - currentWidget.getBoundingClientRect().left
    }

    if (currentWidget.offsetLeft + newWidth < areaWidth &&
        currentWidget.getAttribute("minwidth") / 100 * areaWidth < newWidth &&
        currentWidget.getAttribute("minheight") / 100 * areaHeight < newHeight && 
        currentWidget.offsetTop + newHeight < areaHeight + navbarHeight) {
      currentWidget.style.width = newWidth + 'px';
      currentWidget.style.height = newHeight + 'px';
    }
    else {
      console.log('Nope')
    }
  }

  function stopResize() {
    window.removeEventListener('mousemove', resize);
    window.removeEventListener('mouseup', stopResize)
  }
}

function openSettingsWindow(widgetName) {  
    let settingsWindowWidth = windowWidth * 0.5
    let settingsWindowHeight = windowHeight * 0.5
    let settingsWindow = window.open(
      "widget-settings?widget=" + widgetName, 
      "toolbar=no,location=no,directories=no,status=no,menubar=no,scrollbars=yes,resizable=yes",
      "width=1024,height=576"
      )
    //settingsWindow.console.log('This window has been opened!')
}