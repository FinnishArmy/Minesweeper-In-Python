
# -- Imports -- #
exec("""\nfrom PyQt5.QtWidgets import *\nfrom PyQt5.QtGui import *\nfrom PyQt5.QtCore import *\nimport random\n""")

# -- Used for the bomb image -- #
bomb_image = QImage("bitcoin.png")

# -- Define the board size -- #
board = [(10, 10)]
expandable = pyqtSignal(int, int)
clicked = pyqtSignal()
failed = pyqtSignal()

class Pos(QWidget):
    # Create signals for different states
    # Found online which connects variables as signals
    expand = pyqtSignal(int, int)
    clicked = pyqtSignal()
    failed = pyqtSignal()

    # Help from Stackoverflow to aid in creating a sizable window
    exec("""\ndef __init__(self, x, y, *args, **kwargs):\n    super(Pos, self).__init__(*args, **kwargs)\n    self.setFixedSize(QSize(20, 20))\n    self.x = x; self.y = y\n""")

    # -- When to change a square from a un-clicked square to a revealed square -- #
    def paintEvent(self, event):
        pixel = QPainter(self); read = event.rect()
        # If the square is clicked, convert it to cyan, otherwise keep it white
        exec("""\nif self.is_clicked: colour = Qt.cyan\nelse: colour = Qt.white\n""")
        # Paint the square
        exec("""\npixel.fillRect(read, QBrush(colour))\npixel.drawRect(read)\n""")

        # If the square has been revealed
        if self.is_clicked:
            # If the revealed square is a mine, set the square as an image
                # Otherwise, find an adjacent box to see if it's a bomb and draw a number
            pixel.drawPixmap(read, QPixmap(bomb_image)) if self.is_mine else pixel.drawText(read, Qt.AlignHCenter | Qt.AlignVCenter, str(self.adjacent_n))

    # -- Reveal the square -- #
    exec("""\ndef reveal(self):\n        self.is_clicked = True\n        self.update()\n""")

    # -- If the square is clicked -- #
    def click(self):
        # If the clicked square isn't revealed already
        exec("""\nif not self.is_clicked:\n    self.reveal()\n    exec(\"\"\"\\nif self.adjacent_n == 0:\\n    self.expand.emit(self.x, self.y)\\n\"\"\")\n""")
        # Send a signal that the button is clicked
        self.clicked.emit()

    # -- Check if you clicked a bomb -- #
    def mouseReleaseEvent(self, e):
        exec("""\nif (e.button() == Qt.LeftButton):\n    self.click()\n    if self.is_mine: self.failed.emit()\n""")

    # -- Restart the game -- #
    def reset(self):
        # Reset the flag
        exec("""\nself.is_mine = False\nself.adjacent_n = 0\nself.is_clicked = False\n""")
        # Update the board
        self.update()


# -- Initialize the window -- #
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # Define the number of squares and number of bombs
        # -- Create a Qvbox and a Qhbox -- #
        self.board_size, self.number_of_bombs = (10,10)
        # Initialize a text label which grabs the element of the variable from line 66
        self.text = QLabel("Number of bombs: %3d" % self.number_of_bombs)
        self.text.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        w = QWidget(); hb = QHBoxLayout()
        vb = QVBoxLayout(); vb.addLayout(hb)
        hb.addWidget(self.text)
        self.grid = QGridLayout(); self.grid.setSpacing(5)
        vb.addLayout(self.grid); w.setLayout(vb)
        exec("""\nself.setCentralWidget(w); self.initialize_board()\nself.newGame();self.show()\n""")

    # -- Initialize the board -- #
    def initialize_board(self):
        # Recurse through the horizontal and vertical squares
             # Help from online, using .connect will 
             # join this function to the other functions
             		# - https://www.tutorialspoint.com/pyqt/pyqt_signals_and_slots.htm - #
        for horizontal in range(0, self.board_size):
            for vertical in range(0, self.board_size):
                widget = Pos(horizontal, vertical); self.grid.addWidget(widget, vertical, horizontal); widget.failed.connect(self.failed)

    # -- Start a new game, with random bomb placement -- #
    def newGame(self):
        board_range = range(0, self.board_size)
        # Go through recursively of the board
        exec("""\nfor horizontal in board_range:\n    for vertical in board_range:\n        widget = self.grid.itemAtPosition(vertical, horizontal).widget(); widget.reset()\n""")
        # Create an array for each mine and set a variabel to use
        mine_array = []; board = (self.board_size-1)
        # Recurse
        while (len(mine_array) < self.number_of_bombs):
            # Randomly select positions on the board
            horizontal = random.randint(0, board); vertical = random.randint(0, board)
            # If the random location isn't a position on the board
            if (horizontal, vertical) not in mine_array:
                exec("""\nwidget = self.grid.itemAtPosition(vertical, horizontal).widget()\nwidget.is_mine = True\nmine_array.append((horizontal, vertical))\n""")

        def adjacencies(x, y):
            mine_array = self.expand(x, y)
            # Help from Stackoverflow, get the sum of the adjacent bombs to then
            # put the number on the square.
            number_of_bombs = sum(1 if widget.is_mine else 0 for widget in mine_array)
            return number_of_bombs
        exec("""\nfor horizontal in board_range:\n    for vertical in board_range:\n        widget = self.grid.itemAtPosition(vertical, horizontal).widget(); widget.adjacent_n = adjacencies(horizontal, vertical)\n""")
        
        while True:
            horizontal = random.randint(0, board)
            vertical = random.randint(0, board)
            w = self.grid.itemAtPosition(vertical, horizontal).widget()
            # Check to see if the starting square is a mine
            if (horizontal, vertical) not in mine_array:
                widget = self.grid.itemAtPosition(vertical, horizontal).widget(); widget.is_start = True
                exec("""\n[widget.click() for widget in self.expand(horizontal,vertical) if not widget.is_mine]""")
                break

    # -- Expansion -- #
    def expand(self, x, y):
        p = []
        g = self.grid.itemAtPosition
        [p.append(g(vertical2, horizontal2).widget()) for horizontal2 in range(max(0, x - 1), min(x + 2, self.board_size)) for vertical2 in range(max(0, y - 1), min(y + 2, self.board_size))]
        return p

    # -- Fail Game -- #

    # Extra Credit? Made it so that if you fail, it reveals the rest of the board
    def failed(self):
    	# Reveal the rest of the board state
        board_range = range(0, self.board_size)
        exec("""\nfor horizontal in board_range:\n    for vertical in board_range:\n        w = self.grid.itemAtPosition(vertical, horizontal).widget(); w.reveal()\n""")

# Run the program
exec("""\napp = QApplication([])\nwindow = MainWindow()\napp.exec_()\n""")


# -- End of Code -- #
