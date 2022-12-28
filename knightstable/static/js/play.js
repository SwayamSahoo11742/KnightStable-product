var playBtn = document.querySelector(".play-btn")
var settingsForm = document.querySelector(".match-settings-form")
var loadingImg = document.querySelector(".loading-img")
var fakeBoard = Chessboard("board", "start")

playBtn.addEventListener("click", function(){
    settingsForm.style.display = "none"
    loadingImg.style.display = "inline"
}) 