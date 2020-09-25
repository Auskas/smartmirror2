$("#navbar").hide();
$("#footer").hide();
// Wrap every letter in a span
var textWrapper = document.querySelector('.introHeader');
textWrapper.innerHTML = textWrapper.textContent.replace(/\S/g, "<span class='letter'>$&</span>");

anime.timeline()
  .add({
    targets: '.introHeader .letter',
    opacity: [0,1],
    easing: "easeInOutQuad",
    duration: 3000,
    delay: (el, i) => 250 * (i+1)
  })

videoElement = document.getElementById('introVideo');
videoElement.addEventListener('ended', function() {
    setTimeout(function(){ 
        videoElement.style.display = 'none';
        let url = videoElement.getAttribute("redirect")
        window.location.href = url;
    }, 500);


});