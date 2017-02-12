import tkinter as tk
from enum import Enum

WINDOW_SIZE = 500
BOARD_SIZE = 20
STEP = WINDOW_SIZE // BOARD_SIZE
HINT_RADIUS = int(STEP // 3)
SIDE_WIDTH = WINDOW_SIZE / 5

class BoardStatus(Enum):
    EMPTY = 0
    WHITE = 1
    BLACK = 2
    HINT = 3


board = [[BoardStatus.EMPTY] * BOARD_SIZE for i in range(BOARD_SIZE)]
currentPlayer = BoardStatus.BLACK

root = tk.Tk()
myCanvas = tk.Canvas(root, width=WINDOW_SIZE + SIDE_WIDTH, height=WINDOW_SIZE, background='linen')
myCanvas.pack()

def create_circle(centerX, centerY, radius, **kw):
    return myCanvas.create_oval(centerX - radius, centerY - radius, centerX + radius, centerY + radius, kw)

def draw_board():
    for i in range(1, BOARD_SIZE):
        myCanvas.create_line(i * STEP, STEP, i * STEP, WINDOW_SIZE - STEP, fill='black')
        myCanvas.create_line(STEP, i * STEP, WINDOW_SIZE - STEP, i * STEP, fill='black')
    create_circle(WINDOW_SIZE/2, WINDOW_SIZE/2, 0.1 * STEP, fill='black')



def get_center_coords():
    centerX, centerY = myCanvas.coords(myCanvas.find_withtag(tk.CURRENT))[0:2]
    centerX += 0.2 * STEP
    centerY += 0.2 * STEP
    print(centerX, centerY)
    return int(centerX), int(centerY)

def add_piece(event):
    global board
    global currentPlayer
    centerIndices = center_indices(event.x, event.y)
    if centerIndices == None:
        return
    index_x = centerIndices[0]
    index_y = centerIndices[1]
    if board[index_x][index_y] != BoardStatus.BLACK and board[index_x][index_y] != BoardStatus.WHITE:
        board[index_x][index_y] = currentPlayer
        color = {BoardStatus.BLACK: 'black', BoardStatus.WHITE: 'white'}[currentPlayer]
        create_circle(index_x * STEP, index_y * STEP, 0.5 * STEP, fill=color)
        if currentPlayer == BoardStatus.BLACK:
            currentPlayer = BoardStatus.WHITE
        else:
            currentPlayer = BoardStatus.BLACK
        color = {BoardStatus.BLACK: 'black', BoardStatus.WHITE: 'white'}[currentPlayer]
        myCanvas.delete('current player')
        create_circle(WINDOW_SIZE + SIDE_WIDTH/2, WINDOW_SIZE/2, 0.5 * STEP, fill=color, tags='current player')

def center_indices(x, y):
    index_x = int((x + 0.5 * STEP) // STEP)
    index_y = int((y + 0.5 * STEP) // STEP)
    if index_x < 1 or index_x >= BOARD_SIZE or index_y < 1 or index_y >= BOARD_SIZE:
        return None
    if (x - index_x * STEP) ** 2 + (y - index_y * STEP) ** 2 > HINT_RADIUS ** 2:
        return None
    return (index_x, index_y)

def draw_next_piece(centerIndices):
    index_x = centerIndices[0]
    index_y = centerIndices[1]
    if board[index_x][index_y] == BoardStatus.EMPTY:
        create_circle(index_x * STEP, index_y * STEP, 0.5 * STEP, outline='blue', fill='', tags='hint')


def show_next_piece(event):
    centerIndices = center_indices(event.x, event.y)
    if centerIndices == None:
        myCanvas.delete('hint')
        for i in range(1, BOARD_SIZE):
            for j in range(1, BOARD_SIZE):
                if board[i][j] == BoardStatus.HINT:
                    board[i][j] == BoardStatus.EMPTY
    else:
        draw_next_piece(centerIndices)

myCanvas.bind('<Motion>', show_next_piece)
myCanvas.bind('<Button-1>', add_piece)


draw_board()
create_circle(WINDOW_SIZE + SIDE_WIDTH/2, WINDOW_SIZE/2, 0.5 * STEP, fill='black', tags='current player')
root.mainloop()
