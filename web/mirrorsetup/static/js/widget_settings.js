var widget;
var parentWidget;
var showCheckbox;
var showText;
var anchorCheckbox;
var anchorText;
var widgetName;
console.log('Settings window')
document.addEventListener("DOMContentLoaded", function(event) {
    widgetName = document.getElementById("widget-name").getAttribute("name")
    parentWidget = window.opener.document.getElementById('widget-' + widgetName)
    widget = parentWidget.cloneNode(true);
    document.getElementById("heading").innerHTML = widget.getAttribute("alias")

    let showStatus = widget.getAttribute('show');
    showCheckbox = document.getElementById('showCheckbox');
    showText = document.getElementById('showText')

    let anchorStatus = widget.getAttribute('anchor')
    anchorCheckbox = document.getElementById('anchorCheckbox');
    anchorText = document.getElementById('anchorText')

    if (showStatus == "True" && showCheckbox.checked == false) {
        showCheckbox.checked = true;
        showText.innerHTML = "Виджет показывается"
    }
    else if (showStatus == "False" && showCheckbox.checked == false) {
        showCheckbox.checked = false;
        showText.innerHTML = "Виджет не показывается"
    }

    if (anchorStatus == "ne") {
        anchorCheckbox.checked = true;
        anchorText.innerHTML = "Выравнивание по правому краю"
    }
    else {
        anchorCheckbox.checked = false;
        anchorText.innerHTML = "Выравнивание по левому краю"
    }
    $('body').removeAttr('hidden');
});

function changeShowStatus() {
    if (showCheckbox.checked) {
        widget.setAttribute("show", "True");
        showText.innerHTML = "Виджет показывается"
    }
    else {
        widget.setAttribute("show", "False");
        showText.innerHTML = "Виджет не показывается"
    }
}

function changeAnchorStatus() {
    if (anchorCheckbox.checked) {
        widget.setAttribute("anchor", "ne");
        anchorText.innerHTML = "Выравнивание по правому краю"
    }
    else {
        widget.setAttribute("anchor", "nw");
        anchorText.innerHTML = "Выравнивание по левому краю"
    }
}

function applyChanges() {
    parentWidget.setAttribute('show', widget.getAttribute('show'));
    parentWidget.setAttribute('anchor', widget.getAttribute('anchor'));
    // If it is the Youtube widget configuration window, updates the widget
    // element of the main settings using the value of the input field.
    if (widgetName == "youtube") {
        parentWidget.setAttribute('defaultVideo', document.getElementById('defaultVideoField').value)
    }
    window.opener.updateShowStatus(widget.getAttribute('id'));
    window.close();
}