import random
from flask import *

app = Flask(__name__)

nRows, nCols = 7, 8
maxMosse = nRows * nCols
segnaPosto = "W"
gettoni = ("R", "Y")
nomeScript = "/script.py"
app.secret_key = "sessionSecretKey"


# Creazione dinamica della matrice
def createMatrix():
    matrix = [segnaPosto] * nRows
    for i in range(nRows):
        matrix[i] = [segnaPosto] * nCols
    return matrix


# 'R' => turno player1
# 'Y' => turno player2
def randomFirstPlayer():
    return random.choice([gettoni[0], gettoni[1]])


# Controllo se la mossa selezionata è valida
def checkMove(matrix, col):
    for i in range(nRows - 1, -1, -1):
        if (matrix[i][col] == segnaPosto):
            return i
    return -1


# Esecuzione della mossa selezionata
def moves(matrix, col, gettone):
    row = checkMove(matrix, col)
    if (row != -1):
        matrix[row][col] = gettone
        return row
    print("La mossa selezionata non è valida")
    return -1


def conditions(i, j, index):
    if (index == 0):
        return j >= 0
    elif (index == 1):
        return j < nCols
    elif (index == 2):
        return i >= 0 and j >= 0
    elif (index == 3):
        return i < nRows and j < nCols
    elif (index == 4):
        return i >= 0 and j < nCols
    return i < nRows and j >= 0


def horizontalWinRule(matrix, i, j, cond, incrJ, gettone):
    count = 0
    while (conditions(i, j, cond)):
        if (matrix[i][j] == gettone):
            count += 1
            j += incrJ
        else:
            break
    return count


# Controllo se c'è una streak orizzontale di 4 tra sinistra e destra
def horizontalWin(matrix, i, j, gettone):
    count = 1
    # Controllo se c'è una streak orizzontale di 4 verso sinistra
    count += horizontalWinRule(matrix, i, j - 1, 0, -1, gettone)
    if (count == 4):
        return True
    # Controllo se c'è una streak orizzontale di 4 verso destra
    count += horizontalWinRule(matrix, i, j + 1, 1, 1, gettone)
    return count == 4


# Controllo se c'è una streak orizzontale di 4 verso il basso
def verticalWin(matrix, i, j, gettone):
    count = 0
    while (i < nRows):
        if (matrix[i][j] == gettone):
            count += 1
            i += 1
        else:
            break
    return count == 4


def diagonalWinRule(matrix, i, j, cond, incrI, incrJ, gettone):
    count = 0
    while (conditions(i, j, cond)):
        if (matrix[i][j] == gettone):
            count += 1
            i += incrI
            j += incrJ
        else:
            break
    return count


# Controllo se c'è una streak orizzontale di 4 su una diagonale da sinistra-superiore verso destra-inferiore
def leftDiagonalWin(matrix, i, j, gettone):
    count = 1
    # Controllo se c'è una streak orizzontale di 4 verso la diagonale sinistra superiore
    count += diagonalWinRule(matrix, i - 1, j - 1, 2, -1, -1, gettone)
    if (count == 4):
        return True
    # Controllo se c'è una streak orizzontale di 4 verso la diagonale destra inferiore
    count += diagonalWinRule(matrix, i + 1, j + 1, 3, 1, 1, gettone)
    return count == 4


# Controllo se c'è una streak orizzontale di 4 su una diagonale da destra-superiore verso sinistra-inferiore
def rightDiagonalWin(matrix, i, j, gettone):
    count = 1
    # Controllo se c'è una streak orizzontale di 4 verso la diagonale destra superiore
    count += diagonalWinRule(matrix, i - 1, j + 1, 4, -1, 1, gettone)
    if (count == 4):
        return True
    # Controllo se c'è una streak orizzontale di 4 verso la diagonale sinistra inferiore
    count += diagonalWinRule(matrix, i + 1, j - 1, 5, 1, -1, gettone)
    return count == 4


# Controllo ad ogni mossa se il giocatore che ha appena eseguito la mossa, ha fatto
# una mossa vincente
def checkWin(matrix, row, col, gettone):
    return (verticalWin(matrix, row, col, gettone)
            or horizontalWin(matrix, row, col, gettone)
            or leftDiagonalWin(matrix, row, col, gettone)
            or rightDiagonalWin(matrix, row, col, gettone))


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    session.clear()
    session["matrix"] = createMatrix()
    return send_file("index.html")


@app.route(f"{nomeScript}/gioco_inizio", methods=["POST"])
def gioco_inizio():
    session["player1"] = request.form.get("player1")
    session["gettonePlayer1"] = gettoni[0]
    session["player2"] = request.form.get("player2")
    session["gettonePlayer2"] = gettoni[1]
    session["turno"] = randomFirstPlayer()
    session["messaggio"] = ""
    session["mosse"] = 0
    session["fineGioco"] = "N"
    session["nRows"] = nRows
    session["nCols"] = nCols
    return render_template("gioco.html", session=session)


@app.route(f"{nomeScript}/gioco", methods=["GET"])
def gioco():
    return render_template("gioco.html", session=session)


@app.route(f"{nomeScript}/mossa", methods=["POST"])
def mossa():
    col = int(request.form.get("mossa")) - 1
    row = moves(session["matrix"], col, session["turno"])
    if (row != -1):
        session["mosse"] = int(session["mosse"]) + 1
        if (checkWin(session["matrix"], row, col, session["turno"])):
            session["messaggio"] = f"<h1>Congratulazioni {session.get('player1') if session.get('turno') ==  gettoni[0] else session.get('player2')} per aver vinto</h1><form action='/' method='GET'><input type='submit' value='Homepage' id='button' /></form>"
            session["fineGioco"] = "Y"
        elif (int(session["mosse"]) == maxMosse):
            session["messaggio"] = "<h2>La partità è finita in pareggio</h2><form action='/' method='GET'><input type='submit' value='Homepage' id='homepage' /></form>"
            session["fineGioco"] = "Y"
        else:
            session["turno"] = gettoni[1] if session["turno"] == gettoni[0] else gettoni[0]
        return redirect(f"{nomeScript}/gioco")
    else:
        return render_template("errorMossa.html")


if __name__ == "__main__":
    app.run(debug=True)
