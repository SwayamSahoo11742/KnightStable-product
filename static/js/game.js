// ------------------------------Declaring elements--------------------------------------------------------------
var table = document.querySelector(".table")
var timers = document.querySelectorAll(".timer")
var userName = document.querySelector("#user-name")
var opponentName = document.querySelector("#opponent-name")
var opponentPfp = document.querySelector(".opponent-pfp")
var userPfp = document.querySelector(".user-pfp")
var pfps = document.querySelectorAll(".pfp")
var userRating = document.querySelector("#user-rating")
var ratings = document.querySelectorAll(".player-rating")
var opponentRating = document.querySelector("#opponent-rating")
// adding move count to keep track of the moves in a side table
var moveCount = 0
// determining whose move it is to update timers
var whoseMove = "white"
var socket = io.connect("/play", {'sync disconnect on unload':true})
var selfColor = null
var gameData = null
// Selecting modals
var myModal = new bootstrap.Modal(document.querySelector("#MyModal"));
var resignBtn = document.querySelector("#resign")
var resignModal = new bootstrap.Modal(document.querySelector("#resign-modal"));
var resignConfirm = document.querySelector("#resign-btn")
var abort = document.querySelector("#abort")
var abortModal = new bootstrap.Modal(document.querySelector("#abort-modal"))
var timeStop = false
var userStat = document.querySelector(".user-stat")
var opponentStat = document.querySelector(".opponent-stat")
// ----------------------------------------Event Listeners-----------------------------------------------------
// If wanting to reisng
resignBtn.addEventListener("click", function() {
    // confirmation modal
    resignModal.show();
})

// If confirmed to resignation
resignConfirm.addEventListener("click", function() {
    // Preapare and and send game data
    socket.emit("resign")
    if (gameData.white === gameData.selfname) {
        var winner = "black"
        var gameInfo = getRating(gameData.black_rating, gameData.white_rating, "0-1")
        gameInfo.winner = winner
        gameInfo.data = gameData
        gameInfo.pgn = game.pgn()
        socket.emit("gameOver", gameInfo)
    } else {
        var winner = "white"
        var gameInfo = getRating(gameData.black_rating, gameData.white_rating, "1-0")
        gameInfo.winner = winner
        gameInfo.data = gameData
        gameInfo.pgn = game.pgn()
        socket.emit("gameOver", gameInfo)

    }
    // Hide resignation modal
    resignModal.hide();
})
// If wanting to abore
abort.addEventListener("click", function() {
    // Show abort modal

    // Send over empty info 
    var gameInfo = {
        "black": 0,
        "white": 0,
        "winner": "abort",
        "data": gameData,
        "pgn": game.pgn()
    }
    socket.emit("gameOver", gameInfo)
    socket.emit("abort")
})
//------------------------------------------Making Board---------------------------------------------------------
var board = null
var game = new Chess()
var whiteSquareGrey = '#a9a9a9'
var blackSquareGrey = '#696969'
// --------------------------------- Socketio -------------------------------------------------------------------
// When resigned
socket.on('resign', ()=>{
    // Stop clock
    timeStop = true
})

// When aborted
socket.on('abort', ()=>{
    // show abort modal
    abortModal.show()
    // stop timers
    timeStop = true
})

// When player connected
socket.on("connect", ()=>{

    // On abandonement
    socket.on("disconnect", () =>{
        // Send appropriate data
        // if White
        if (gameData.white === gameData.selfname) {
            // Black is winner
            var winner = "black"
            var gameInfo = getRating(gameData.black_rating, gameData.white_rating, "0-1")
            gameInfo.winner = winner
            gameInfo.data = gameData
            gameInfo.pgn = game.pgn()
            socket.emit("gameOver", gameInfo)
        // If black
        } else {
            // White is winner
            var winner = "white"
            var gameInfo = getRating(gameData.black_rating, gameData.white_rating, "1-0")
            gameInfo.winner = winner
            gameInfo.data = gameData
            gameInfo.pgn = game.pgn()
            socket.emit("gameOver", gameInfo)
        }
    })

})

// When game over
socket.on("gameOver", (data) => {
    // If game over
    // if winner is self
    if (data.winner === gameData.selfname) {
        // Modal message say you won
        document.querySelector("#result-msg").innerText = "You Won!!     Your rating increased by:  " + data.winner_mod
        // If draw
    } else if (data.winner === "none") {
        // Tie!
        document.querySelector("#result-msg").innerText = "Tie!"
        // If winner is not self (self = loser)
    } else {
        // deliver sad news
        document.querySelector("#result-msg").innerText = "You Lost :(     Your rating decreased by:  " + (-1 * (data.loser_mod))
    }
    // Show modal with modified msgs
    myModal.show();
    // Stoping Time
  
        
})

// When message sent by server
socket.on("message", (data) => {
    console.log("here o am")
    // Create game data so other functions can access
    gameData = data
    console.log(whitePfp)
    console.log(blackPfp)
    console.log(opponentPfp)
    console.log(userPfp)
    console.log(pfps)
    // Give your side you user name
    userName.innerText = data.selfname
    // if black
    if (data.selfname === data.black) {
        // orient board black 
        board.orientation('black')
        // declare sels's color as black
        selfColor = 'black'
        // opponent name white
        opponentName.innerText = data.white
        // Giving ids accordingly, keeping in mind you are black
        timers[0].setAttribute("id", "white-timer")
        timers[1].setAttribute("id", "black-timer")
        ratings[0].setAttribute("id", "white-rating")
        ratings[1].setAttribute("id", "black-rating")
        pfps[0].src = whitePfp
        pfps[1].src = blackPfp
        userStat.href = "/user/" + gameData.black
        opponentStat.href = "/user/" + gameData.white
        // if white
    } else {
        // self's color declared as white
        selfColor = 'white'
        //  Change opponent's name to that of black's
        opponentName.innerText = data.black
        // set ids accordingly, keeping in mind you are white
        timers[1].setAttribute("id", "white-timer")
        timers[0].setAttribute("id", "black-timer")
        ratings[1].setAttribute("id", "white-rating")
        ratings[0].setAttribute("id", "black-rating")
        pfps[1].src =  whitePfp
        pfps[0].src=  blackPfp
        userStat.href = "/user/" + gameData.white
        opponentStat.href = "/user/" + gameData.black
    }
    // using the ids previously set to show the player data accordingly
    document.querySelector("#black-rating").innerText = data.black_rating
    document.querySelector("#white-rating").innerHTML = data.white_rating
    timers.forEach(timer => {
        timer.innerText = data.time
    })

});
// When a move is made
socket.on("moved", (data) => {
    // into notation
    var move = data.from + "-" + data.to
    // make move on html board as well as js text board
    board.move(move)
    game.move({
        from: data.from,
        to: data.to,
        promotion: "q"
    })
    //  If white moved, change turn to black
    if (data.color === "w") {
        game.setTurn("b")
    }
    // If black moved, change turns to white
    if (data.color === "b") {
        game.setTurn("w")
    }

    // Declaring timers
    var blackPlayerTimer = document.querySelector("#black-timer")
    var whitePlayerTimer = document.querySelector("#white-timer")
    var pgn = game.pgn()

    pgn = pgn.split(".")
    // If white moved
    if (data.color == "w") {
        // updating whose move it is
        whoseMove = "black"

        // Updating moveCount
        moveCount++

        // inserting notation
        var notation = pgn[moveCount].split(" ")[1]
        $(table).find('tbody').append("<tr><td>" + moveCount.toString() + "." + "</td><td>" + notation + "</tr>");

        //ticking Black's timer with an interval of 1 second
        var blackTimer = setInterval(function() {
            var time = countdown(blackPlayerTimer.innerText)

            // If white's time should be ticking
            if (timeStop === true){
                clearInterval(blackTimer)
            }
            if (whoseMove === "white" || game.game_over()) {

                // Stop black's time from ticking
                clearInterval(blackTimer)
            }
            // If no time
            if (time === "00:00") {
                // Send info to server and stop time
                winner = "white"
                var gameInfo = getRating(gameData.black_rating, gameData.white_rating, "1-0")
                gameInfo.winner = winner
                gameInfo.data = gameData
                gameInfo.pgn = game.pgn()
                clearInterval(blackTimer)
                socket.emit("gameOver", gameInfo)
            }
            // Update the htmlText
            blackPlayerTimer.innerText = time
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

        // ticking white's timer
        var whiteTimer = setInterval(function() {
            var time = countdown(whitePlayerTimer.innerText)

            // if Black's time should be ticking
            if (timeStop === true){
                clearInterval(whiteTimer)
            }
            if (whoseMove === "black" || game.game_over()) {

                // Stop this timer
                clearInterval(whiteTimer)
            }
            // if no time
            if (time === "00:00") {
                // send into to server and stop time
                clearInterval(whiteTimer)
                winner = "black"
                var gameInfo = getRating(gameData.black_rating, gameData.white_rating, "0-1")
                gameInfo.winner = winner
                gameInfo.data = gameData
                gameInfo.pgn = game.pgn()
                socket.emit("gameOver", gameInfo)
            }

            // Updating timer
            whitePlayerTimer.innerText = time
        }, 1000);
    }

})




// ------------------------------Chess Board Functions-----------------------------------------------------------
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

    // not allowing white player to move black pieced
    if (selfColor === "white") {
        if (piece.search(/^w/) === -1) {
            return false;
        }
    }

    // not allowing white player to move black pieces
    else {
        if (piece.search(/^b/) === -1) {
            return false;
        }
    }
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
    // Checking the move count
    // if above 2
    if (moveCount >= 2) {
        // Don't allow aborting
        abort.disabled = true
        abort.setAttribute("disabled", "")
    }
    // see if the move is legal
    var move = game.move({
        from: source,
        to: target,
        promotion: 'q' // NOTE: always promote to a queen for example simplicity
    })

    // illegal move
    if (move === null) return 'snapback'
    if (game.in_checkmate()) {
        // If black in mate, winner is white
        if (game.in_checkmate() === "b") {
            var winner = "white"
            var result = "1-0"
            // if white in mate, winner is black
        } else {
            var winner = "black"
            var result = "0-1"
        }
        // Send game into to server
        var gameInfo = getRating(gameData.black_rating, gameData.white_rating, result)
        gameInfo.winner = winner
        gameInfo.data = gameData
        gameInfo.pgn = game.pgn()
        socket.emit("gameOver", gameInfo)
    }
    // If draw
    if (game.in_draw()) {
        // Winner none, send info to server
        var winner = "none"
        var gameInfo = getRating(gameData.black_rating, gameData.white_rating, "1-1")
        gameInfo.winner = winner
        gameInfo.data = gameData
        gameInfo.pgn = game.pgn()
        socket.emit("gameOver", gameInfo)
    }
    // When moved, send "moved" event to server
    socket.emit("moved", move)

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
// -----------------------------Timer Updating Functions-----------------------------------------------------
// Counting down
function countdown(time) {
    // Getting the minse
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
//-------------------------------------------------------RATING CALCULATION FUNCTION------------------------------------------------
function getRating(blackRating, whiteRating, result) {
    var change = {
        "black": null,
        "white": null
    }
    // Deciding when black wins
    if (result === "0-1") {
        var difference = whiteRating - blackRating
        if (Math.abs(difference) <= 30) {
            change.black = 8
            change.white = -8
        } else if (difference <= 100 && difference >= 30) {
            change.black = 10
            change.white = -10
        } else if (difference >= 100) {
            change.black = Math.round((difference - 100) / 30) + 10
            change.white = -1 * (Math.round((difference - 100) / 30) + 10)
        } else if (difference < 0) {
            change.black = Math.round(8 - Math.abs(difference) / 100)
            change.white = -1 * (Math.round((8 - Math.abs(difference) / 100)))
        }
    }
    // Deciding for is white wins
    else if (result === "1-0") {
        var difference = blackRating - whiteRating
        if (Math.abs(difference <= 30)) {
            change.white = 8
            change.black = -8
        } else if (difference <= 100 && difference >= 30) {
            change.white = 10
            change.black = -10
        } else if (difference >= 100) {
            change.white = Math.round((difference - 100) / 30) + 10
            change.black = -1 * (Math.round((difference - 100) / 30) + 10)
        } else if (difference < 0) {
            change.white = 8 - abs(difference) / 100
            change.black = -1 * (8 - abs(difference) / 100)
        }
    }
    // Draw case
    else {
        change.black = 0
        change.white = 0
    }
    change.black = Math.abs(change.black)
    change.white = Math.abs(change.white)
    return change;
}
// ------------------------------------------------------Game Config----------------------------------------------------

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