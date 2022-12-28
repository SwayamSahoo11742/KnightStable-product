var drawBar = document.querySelectorAll(".draw-bar")
var lossBar = document.querySelectorAll(".loss-bar")
var winBar = document.querySelectorAll(".win-bar")
// Making the bars
for (var i = 0; i < drawBar.length; i++){
    drawBar[i].style.backgroundColor = "gray"
    var percent = parseInt(drawBar[i].innerText.replace("Draw", "").replace("%").trim())
    percent -= 0.5
    percent = percent.toString()
    drawBar[i].style.width = percent + "%"

    winBar[i].style.backgroundColor = "#d8d8d8"
    var percent = parseInt(winBar[i].innerText.replace("Win", "").replace("%").trim())
    percent -= 0.5
    percent = percent.toString() 
    winBar[i].style.width = percent + "%"

    lossBar[i].style.backgroundColor = "black"
    var percent = parseInt(lossBar[i].innerText.replace("Loss", "").replace("%").trim())
    percent -= 0.5
    percent = percent.toString()
    lossBar[i].style.width = percent + "%"
}
