import curses
import random

def main(stdscr):
    # Setup terminal settings
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)
    
    sh, sw = stdscr.getmaxyx()
    w = curses.newwin(sh, sw, 0, 0)
    w.keypad(1)
    
    # Initial snake position
    snk_x = sw // 4
    snk_y = sh // 2
    snake = [
        [snk_y, snk_x],
        [snk_y, snk_x - 1],
        [snk_y, snk_x - 2]
    ]
    
    # Initial food position
    food = [sh // 2, sw // 2]
    w.addch(food[0], food[1], curses.ACS_PI)
    
    key = curses.KEY_RIGHT
    score = 0

    while True:
        next_key = w.getch()
        key = key if next_key == -1 else next_key

        # Check if snake hit itself or walls
        if (snake[0][0] in [0, sh] or 
            snake[0][1] in [0, sw] or 
            snake[0] in snake[1:]):
            break

        new_head = [snake[0][0], snake[0][1]]

        if key == curses.KEY_DOWN:
            new_head[0] += 1
        if key == curses.KEY_UP:
            new_head[0] -= 1
        if key == curses.KEY_LEFT:
            new_head[1] -= 1
        if key == curses.KEY_RIGHT:
            new_head[1] += 1

        snake.insert(0, new_head)

        # Check if snake ate food
        if snake[0] == food:
            score += 1
            food = None
            while food is None:
                nf = [
                    random.randint(1, sh - 2),
                    random.randint(1, sw - 2)
                ]
                food = nf if nf not in snake else None
            w.addch(food[0], food[1], curses.ACS_PI)
        else:
            tail = snake.pop()
            w.addch(tail[0], tail[1], ' ')

        w.addch(snake[0][0], snake[0][1], curses.ACS_CKBOARD)

    # Game Over Screen
    stdscr.nodelay(0)
    msg = f" GAME OVER! Score: {score} "
    w.addstr(sh // 2, (sw - len(msg)) // 2, msg, curses.A_REVERSE)
    w.refresh()
    w.getch()

if __name__ == "__main__":
    curses.wrapper(main)
