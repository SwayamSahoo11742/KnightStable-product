var body = document.querySelector("body")
var offHeader = document.querySelector(".offcanvas-header")
var offBody = document.querySelector(".offcanvas-body")
var btns = document.querySelectorAll(".btn")
var modeBtn = document.querySelector("#mode-btn")
var filters = document.querySelectorAll(".search-filter-option")
var filterBar = document.querySelector(".navbar-filter")
var cards = document.querySelectorAll(".card")

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

