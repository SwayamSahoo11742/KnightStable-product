var trs = document.querySelectorAll("tr")

trs.forEach( tr =>{
    tr.addEventListener("mouseover", ()=>{
        var children = tr.children
        children.forEach(child =>{
            child.style.color = "#61ff5e"
        })
    })
})