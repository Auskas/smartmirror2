var widget;
var parentWidget;
var showCheckbox;
window.onload = getElements;


function getElements () {
    const widgetName = document.getElementById("widget-name").getAttribute("name")
    parentWidget = window.opener.document.getElementById('widget-' + widgetName)
    widget = parentWidget.cloneNode(true);
    document.getElementById("heading").innerHTML = widget.getAttribute("alias")


    let showStatus = widget.getAttribute('show');
    showCheckbox = document.getElementById('showCheckbox');

    if (showStatus == "True" && showCheckbox.checked == false) {
        showCheckbox.checked = true;
    }
    else if (showStatus == "False" && showCheckbox.checked == true) {
        showCheckbox.checked = false;
    }
    $('body').removeAttr('hidden');
}

function changeShowStatus() {
    if (showCheckbox.checked) {
        widget.setAttribute("show", "True");
    }
    else {
        widget.setAttribute("show", "False");
    }

}

function applyChanges() {
    parentWidget.setAttribute('show', widget.getAttribute('show'));
    window.opener.setWidgetsSizes();
    window.close();
}