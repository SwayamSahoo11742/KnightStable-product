
// ---------------------------------------------------------------------------PIE CHART----------------------------------------------------------------------------

// Pie Chart btns
var wBtn = document.querySelector(".white-btn")
var bBtn = document.querySelector(".black-btn")
var allBtn = document.querySelector(".all-btn")

// Values for each catagory
var wValues = JSON.parse(whiteStats);
var bValues = JSON.parse(blackStats);
var allValues = JSON.parse(allStats);

// Labels
var labels = ["Win", "Loss", "Draw"];
var barColors = [
  "#e8e8e8",
  "#292929",
  "#808080"
];

// Config
config = {type: "pie",
data: {
  labels: labels,
  datasets: [{
    backgroundColor: barColors,
    data: wValues
  }]
},
options: {
  legend: {
    labels: {
      fontColor: "#ffffff"
    }
  },
  title: {
    display: true,
    text: "Stats as White",
    fontColor: "#ffffff",
    font:{
        size: 50
    }
  }
}
}

// The chart
chart = new Chart("chart", config);


// Pie Chart Event listeners

// When Blackbtn clicked
bBtn.addEventListener('click', ()=>{
    // Get black stats and title
    config.data.datasets[0].data = bValues
    config.options.title.text = "Stats as Black"
    // Update Chart
    chart.update()
})

// When White btn clicked
wBtn.addEventListener('click', ()=>{
    // Get white vals and title
    config.data.datasets[0].data = wValues
    config.options.title.text = "Stats as White"
    // Update
    chart.update()
})

// If all btn
allBtn.addEventListener('click', ()=>{
    // Get iverall vals and titles
    config.data.datasets[0].data = allValues
    config.options.title.text = "Overall Stats"
    // Update
    chart.update()
})

// -------------------------------------------------------------------RATING LINE GRAPH-----------------------------------------------------------------------------------
// turning ratings into an array and storing it in yvals
var yValues = JSON.parse(ratings);
// Getting a range of number of games
var xValues = Array.from({length: yValues.length}, (x, i) => i+1);

// Chart (Line Graph)
new Chart("rating-graph", {
  type: "line",
  data: {
    labels: xValues,
    datasets: [{
      fill: false,
      lineTension: 0,
      backgroundColor: "rgba(255,255,255,1.0)",
      borderColor: "rgba(2,208,227,0.7)",
      data: yValues
    }]
  },
  options: {
    legend: {display: false},
    scales: {
      yAxes: [{
        ticks: {min: 100, max:xValues.lenght},
        gridLines: {
          color: "rgba(255,255,255,0.2)"
        }
      }],
      xAxes: [{
        gridLines: {
          color: "rgba(255,255,255,0.2)"
        },
      }]
    }
    
  }
});