// Declaring elements
var table = document.querySelector(".table")
var moveCount = 0
var moveList = {}
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

  var pgn = game.pgn()
  pgn = pgn.split(".")
  console.log()

  // Notation


  // If white moved
  if (piece[0] == "w") {
    moveCount++
    // insert notation
    var notation = pgn[moveCount].split(" ")[1]
    $(table).find('tbody').append("<tr><td>" + moveCount.toString() + "." + "</td> <td>" + notation + "</tr>");
  }
  // If black moved
  else {
    // insert
    var rows = document.querySelectorAll("tr")
    var row = rows[rows.length - 1]
    var newCell = row.insertCell(-1)
    var notation = pgn[moveCount].split(" ")[2]
    newCell.appendChild(document.createTextNode(notation));
    console.log(row)
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

// Moves Updating

