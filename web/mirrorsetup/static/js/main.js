window.onload = setWidgetsSizes;

var clickedElementID;
var widgets = [];
var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
var windowWidth, windowHeight;
var areaWidth, areaHeight;
var navbarHeight;
const csrftoken = getCookie('csrftoken');

function setWidgetsSizes() {
  windowWidth = window.innerWidth;
  windowHeight = window.innerHeight; 
  console.log({windowWidth})
  console.log({windowHeight})
  navbarHeight = document.getElementById("navbar").offsetHeight; 
  let setupfield = document.getElementById("setupfield");
  // Dimensions of the area that represents the Smart Mirror Mark II
  // The shape is 16 by 9.
  areaHeight = windowHeight - navbarHeight;
  areaWidth = areaHeight * 16 / 9;
  console.log({areaWidth})
  console.log({areaHeight})
  setupfield.style.top = navbarHeight + "px";
  setupfield.style.height = areaHeight + "px";
  setupfield.style.width = areaWidth + "px";

  let widgetsNode = document.querySelectorAll('[id^="widget-"]');
    for (widgetNode of widgetsNode) {
      //console.log(widgetNode.id);
      widgets.push(widgetNode.id)
      let element = document.getElementById(widgetNode.id);
      element.style.left = Math.round(areaWidth * element.getAttribute("relx") / 100) + "px"
      element.style.top = Math.round(areaHeight * element.getAttribute("rely") / 100) + "px"
      element.style.height = Math.round(areaHeight * element.getAttribute("height") / 100) + "px"
      element.style.width = Math.round(areaWidth * element.getAttribute("width") / 100) + "px"
      console.log(element.style.left)
      console.log(element.style.top)
      console.log(element.style.height)
      console.log(element.style.width)
    }
  addListeners(); 
}

function addListeners() {
    //document.getElementById('widget-2').addEventListener('mousedown', mouseDown, false);
    window.addEventListener('mousedown', mouseDown, false);
    window.addEventListener('mouseup', mouseUp, false);
}

function mouseUp() {
    window.removeEventListener('mousemove', divMove, true);
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
  if (div.offsetLeft - pos1 > 0 && div.offsetLeft + div.offsetWidth < areaWidth) {
    let left = (div.offsetLeft - pos1);
    if (left > areaWidth - div.offsetWidth - 10) {
      div.style.left = areaWidth - div.offsetWidth - 10 + "px";
    }
    else {
      div.style.left = left + "px";
    }
  }
  if (div.offsetTop - pos2 > 0 && div.offsetTop + div.offsetHeight < areaHeight) {
    let top = (div.offsetTop - pos2);
    if (top > areaHeight - div.offsetHeight - 10) {
      div.style.top = areaHeight - div.offsetHeight - 10 + "px"
    }
    else {
      div.style.top = (div.offsetTop - pos2) + "px";
    }
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
      console.log('Настройки обновлены')
      console.log(data.status)
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

    console.log(parseInt(elem.style.left))
    console.log(parseInt(areaWidth))
    let temp = {
      "relx": Math.round(parseInt(elem.style.left) / parseInt(areaWidth) * 100),
      "rely": Math.round(parseInt(elem.style.top) / parseInt(areaHeight) * 100),
      "width": Math.round(parseInt(elem.style.width) / parseInt(areaWidth)* 100),
      "height": Math.round(parseInt(elem.style.height) / parseInt(areaHeight) * 100)
    };
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
  console.log(resizer)
  let currentWidget = resizer.parentNode.parentNode;
  let aspectRatio = currentWidget.offsetWidth / currentWidget.offsetHeight
  window.addEventListener('mousemove', resize);
  window.addEventListener('mouseup', stopResize)
    
  function resize(e) {    
    let newHeight = e.pageY - currentWidget.getBoundingClientRect().top   
    let newWidth = newHeight * aspectRatio
    console.log(currentWidget.getAttribute("minwidth"))
    if (currentWidget.offsetLeft + newWidth < areaWidth &&
        currentWidget.getAttribute("minwidth") / 100 * areaWidth < newWidth &&
        currentWidget.getAttribute("minheight") / 100 * areaHeight < newHeight && 
        currentWidget.offsetTop + newHeight < areaHeight) {
      currentWidget.style.width = newWidth + 'px';
      currentWidget.style.height = newHeight + 'px';
    }
  }

  function stopResize() {
    window.removeEventListener('mousemove', resize);
    window.removeEventListener('mouseup', stopResize)
  }
}

