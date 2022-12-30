import sqlite3
import chess
import chess.pgn
import time

startTime = time.time()
games = open("games.pgn")
for i in range(102731):
    game = chess.pgn.read_game(games)

    connect = sqlite3.connect("games.db")
    cursor = connect.cursor()

    site = game.headers["Site"]
    white = game.headers["White"]
    black = game.headers["Black"]
    result = game.headers["Result"]
    whiteelo = game.headers["WhiteElo"]
    blackelo = game.headers["BlackElo"]
    moves = str(game.mainline_moves())
    opening = game.headers["Opening"]

    query = "INSERT INTO games (site, white, black, result, white_elo, black_elo, moves, opening) VALUES (?,?,?,?,?,?,?,?)"
    data_tuple = (site, white, black, result, whiteelo, blackelo, moves, opening)

    cursor.execute(query, data_tuple)
    connect.commit()
    cursor.close()

executionTime = time.time() - startTime
print("Execution time in seconds: " + str(executionTime))
