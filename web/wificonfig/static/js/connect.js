// In order to send a POST query we need to insert the CSRF token into the header.
const csrftoken = getCookie('csrftoken');

function connectToSelectedSpot() {
  // This function send an AJAX request with SSID and password provided by the user.
  let ssid = document.getElementById("ssid").value;
  let password = document.getElementById("password").value;
  let credentials = {"ssid": ssid, "password": password}
  console.log(credentials)
    $.ajax({
    type: "POST",
    url: "connect/",
    dataType: "json",
    headers: {
                'X-CSRFToken': csrftoken 
              },
    data: {"credentials" : JSON.stringify(credentials)},
    success: function (data) {
        if (data.status) {
            alert('Успешное подключение к точке доступа!');
            window.close();
        }
        else {
            alert('Не удалось подключиться к точке доступа. Проверьте пароль!')
        }
    },
    error: function(data){
        alert('Невозможно подключиться к точке доступа!');
    }
  });  
};

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