// Declaring elements
var table = document.querySelector(".table")
var opponentTimer = document.querySelector("#opponent-timer")
var userTimer = document.querySelector("#user-timer")
// adding move count to keep track of the moves in a side table
var moveCount = 0

// determining whose move it is to update timers
var whoseMove = "white"
//Making Board
var board = null
var game = new Chess()
var whiteSquareGrey = '#a9a9a9'
var blackSquareGrey = '#696969'
// Chess Board Functions
function removeGreySquares() {
  $('#myBoard .square-55d63').css('background', '')
}

function greySquare(square) {
  var $square = $('#myBoard .square-' + square)

  var background = whiteSquareGrey
  if ($square.hasClass('black-3c85d')) {
    background = blackSquareGrey
  }

  $square.css('background', background)
}

function onDragStart(source, piece) {
  // do not pick up pieces if the game is over
  if (game.game_over()) return false

  // or if it's not that side's turn
  if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
    (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
    return false
  }
}

function onDrop(source, target, piece) {
  removeGreySquares()
  // see if the move is legal
  var move = game.move({
    from: source,
    to: target,
    promotion: 'q' // NOTE: always promote to a queen for example simplicity
  })

  // illegal move
  if (move === null) return 'snapback'

  // Getting pgn for notation
  var pgn = game.pgn()
  pgn = pgn.split(".")
  console.log()

  // Notation


  // If white moved
  if (piece[0] == "w") {
    // updating whose move it is
    whoseMove = "black"

    // Updating moveCount
    moveCount++

    // inserting notation
    var notation = pgn[moveCount].split(" ")[1]
    $(table).find('tbody').append("<tr><td>" + moveCount.toString() + "." + "</td> <td>" + notation + "</tr>");

    //ticking Black's timer with an interval of 1 second
    var blackTimer = setInterval(function () {
      var time = countdown(opponentTimer.innerText)
      
      // If white's time should be ticking
      if (whoseMove === "white" || time === "00:00") {

        // Stop black's time from ticking
        clearInterval(blackTimer)
      }
      // Update the htmlText
      opponentTimer.innerText = time
    }, 1000);
  }
  // If black moved
  else {
    // Updating whose move it is
    whoseMove = "white"
    // inserting Moves
    // Getting the all rows
    var rows = document.querySelectorAll("tr")
    
    //Getting last row
    var row = rows[rows.length - 1]

    // Adding a cell to the last row
    var newCell = row.insertCell(-1)

    // Joining the notationm to the last row
    var notation = pgn[moveCount].split(" ")[2]
    newCell.appendChild(document.createTextNode(notation));
    console.log(row)

    // ticking white's timer
    var whiteTimer = setInterval(function () {
      var time = countdown(userTimer.innerText)

      // if Black's time should be ticking
      if (whoseMove === "black" || time === "00:00") {

        // Stop this timer
        clearInterval(whiteTimer)
      }

      // Updating timer
      userTimer.innerText = time
    }, 1000);
  }

}

function onMouseoverSquare(square, piece) {
  // get list of possible moves for this square
  var moves = game.moves({
    square: square,
    verbose: true
  })

  // exit if there are no moves available for this square
  if (moves.length === 0) return

  // highlight the square they moused over
  greySquare(square)

  // highlight the possible squares for this piece
  for (var i = 0; i < moves.length; i++) {
    greySquare(moves[i].to)
  }
}

function onMouseoutSquare(square, piece) {
  removeGreySquares()
}

function onSnapEnd() {
  board.position(game.fen())
}

// Timer Updating Functions

// Counting down
function countdown(time) {
  // Getting the mins
  var min = parseInt(time.split(":")[0])

  // Getting the secs
  var sec = parseInt(time.split(":")[1])

  // Calculating total seconds
  var totalSecs = min * 60 + sec

  // Looping total seconds amount of time
  for (var elapsed = 0; elapsed < totalSecs; elapsed++) {
    // If seconds less than 1
    if (sec < 1) {
      // Substract from min instead
      min -= 1
      // Set sec to 59
      sec = 59
    }
    // If sec can still be decremented
    else {
      // do it
      sec -= 1
    }
    // If reached the end
    if (timefy(min.toString()) + ":" + timefy(sec.toString()) == "00:00") {
      // return the end
      return "00:00"
    }
    // Return formatted time-string
    return timefy(min.toString()) + ":" + timefy(sec.toString())
  }
}
// Formatting time numbers
function timefy(number) {
  // If single digit 
  if (number.length === 1) {
    // Add a "0" in front and return
    return "0" + number
  }
  // If greater than single digit
  else {
    // return as is
    return number
  }
}

// Game Config

var config = {
  draggable: true,
  position: 'start',
  onDragStart: onDragStart,
  onDrop: onDrop,
  onMouseoutSquare: onMouseoutSquare,
  onMouseoverSquare: onMouseoverSquare,
  onSnapEnd: onSnapEnd
}
board = Chessboard('board', config)

