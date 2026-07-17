import curses
import random
import time

# Shape definitions (7 classic Tetrominoes)
SHAPES = [
    [[1, 1, 1, 1]], # I
    [[1, 1], [1, 1]], # O
    [[0, 1, 0], [1, 1, 1]], # T
    [[0, 1, 1], [1, 1, 0]], # S
    [[1, 1, 0], [0, 1, 1]], # Z
    [[1, 0, 0], [1, 1, 1]], # J
    [[0, 0, 1], [1, 1, 1]]  # L
]

def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

def check_collision(board, shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                try:
                    if y + off_y >= 20 or x + off_x < 0 or x + off_x >= 10 or board[y + off_y][x + off_x]:
                        return True
                except IndexError:
                    return True
    return False

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(400) # Speed of the game
    
    board = [[0] * 10 for _ in range(20)]
    curr_shape = random.choice(SHAPES)
    curr_off = [3, 0]
    score = 0

    while True:
        stdscr.clear()
        # Draw board and piece
        for y, row in enumerate(board):
            for x, cell in enumerate(row):
                if cell: stdscr.addch(y, x*2, curses.ACS_CKBOARD)
        
        for y, row in enumerate(curr_shape):
            for x, cell in enumerate(row):
                if cell: stdscr.addch(y + curr_off[1], (x + curr_off[0])*2, curses.ACS_DIAMOND)

        stdscr.addstr(0, 22, f"SCORE: {score}")
        stdscr.refresh()

        key = stdscr.getch()
        new_off = list(curr_off)

        if key == curses.KEY_LEFT: new_off[0] -= 1
        elif key == curses.KEY_RIGHT: new_off[0] += 1
        elif key == curses.KEY_DOWN: new_off[1] += 1
        elif key == ord('w'): # Rotate
            rotated = rotate(curr_shape)
            if not check_collision(board, rotated, curr_off):
                curr_shape = rotated

        if not check_collision(board, curr_shape, new_off):
            curr_off = new_off

        # Automatic drop logic
        new_off_down = [curr_off[0], curr_off[1] + 1]
        if not check_collision(board, curr_shape, new_off_down):
            curr_off = new_off_down
        else:
            # Place piece
            for y, row in enumerate(curr_shape):
                for x, cell in enumerate(row):
                    if cell: board[y + curr_off[1]][x + curr_off[0]] = 1
            
            # Clear lines
            board = [row for row in board if any(c == 0 for c in row)]
            while len(board) < 20:
                board.insert(0, [0] * 10)
                score += 10
            
            # New piece
            curr_shape = random.choice(SHAPES)
            curr_off = [3, 0]
            if check_collision(board, curr_shape, curr_off):
                break # Game Over

    stdscr.nodelay(0)
    stdscr.addstr(10, 5, " GAME OVER! ", curses.A_REVERSE)
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)
