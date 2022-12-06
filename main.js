var body = document.querySelector("body")
var offHeader = document.querySelector(".offcanvas-header")
var offBody = document.querySelector(".offcanvas-body")
var btns = document.querySelectorAll(".btn")
var modeBtn = document.querySelector("#mode-btn")
var filters = document.querySelectorAll(".search-filter-option")
var filterBar = document.querySelector(".navbar-filter")
var cards = document.querySelectorAll(".card")
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



//implementing darkmode
modeBtn.addEventListener("click",function(){
    if (modeBtn.innerText == "Dark Mode"){
            modeBtn.innerText = "Light Mode"
            modeBtn.style.backgroundColor = "white"
            modeBtn.style.color = "#131417"
            body.style.color = "white"
            body.style.backgroundColor = "#131417"
            filters.forEach(option => {
                option.style.color = "white"
                option.style.backgroundColor = "#1c1b18"
                option.style.borderColor = "white"
                option.style.borderWidth = "1px"
            })
            offBody.style.backgroundColor = "#131417"
            offHeader.style.backgroundColor = "#131417"
            filterBar.style.backgroundColor = "#131417"
            btns.forEach(btn => {
                btn.style.backgroundColor = "#292b2c"
                btn.style.color = "white"
                btn.style.borderColor = "white"
            })
            cards.forEach( card =>{
                card.style.backgroundColor = "#292b2c"
                card.style.boxShadow = "2px 2px 2px 1px rgba(255, 255, 255, 0.4)"
            })        
        }

    else {
            modeBtn.innerText = "Dark Mode"
            modeBtn.style.backgroundColor = "black"
            modeBtn.style.color = "white"
            body.style.color = "black"
            body.style.backgroundColor = "white"
            filters.forEach(option => {
                option.style.color = "black"
                option.style.backgroundColor = "white"
                option.style.borderColor = "black"
                option.style.borderWidth = "1px"
            })
            offBody.style.backgroundColor = "white"
            offHeader.style.backgroundColor = "white"
            filterBar.style.backgroundColor = "white"
            btns.forEach(btn => {
                btn.style.backgroundColor = "white"
                btn.style.color = "black"
                btn.style.borderColor = "black"
            })
            cards.forEach( card =>{
                card.style.backgroundColor = "white"
                card.style.boxShadow = "2px 2px 2px 1px rgba(0, 0, 0, 0.2)"
            })   
        }
})

