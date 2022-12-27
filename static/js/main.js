// Color pallete
var pallete = {"nav": "#8D72E1", "bg": "#F1F6F5", "font": "#000000", "cards": "#ebfaee", "navLinks": "#252243", "btns": "#B9E0FF", "btnsFont": "#170055 "}



var options = document.getElementsByTagName("option")
var navLinks = document.querySelectorAll(".nav-link")
var navs = document.querySelectorAll(".nav-color")
var body = document.querySelector("body")
var offHeader = document.querySelector(".offcanvas-header")
var offBody = document.querySelector(".offcanvas-body")
var btns = document.querySelectorAll(".btn")
var modeBtn = document.querySelector("#mode-btn")
var filters = document.querySelectorAll(".search-filter-option")
var filterBar = document.querySelector(".navbar-filter")
var cards = document.querySelectorAll(".card")


// Table rows

var trs = document.querySelectorAll("tr")
trs.forEach(tr =>{
    tr.style.color = pallete.font
})

// Dropdown toggle

document.querySelector(".dropdown-toggle").style.backgroundColor = pallete.nav

// Coloring nav-items

navLinks.forEach(item =>{
    item.style.color = pallete.navLinks
})

// Colring nav
navs.forEach(nav =>{
    nav.style.backgroundColor = pallete.nav
})

// Coloring body
body.style.color = pallete.font
body.style.backgroundColor = pallete.bg

// Coloring filter options
filters.forEach(option => {
    option.style.color = pallete.bg
    option.style.backgroundColor = pallete.bg
    option.style.borderColor = "white"
    option.style.borderWidth = "1px"
})

// Coloring cards
cards.forEach( card =>{
    card.style.backgroundColor = pallete.cards
})        


// Colring btns
btns.forEach(btn => {
    btn.style.backgroundColor = pallete.btns
    btn.style.color = pallete.btnsFont
})
  
// Colring offbody canvas
filterBar.style.backgroundColor = pallete.bg