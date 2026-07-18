import turtle

# Create the turtle screen and turtle object
screen = turtle.Screen()
t = turtle.Turtle()

# Set initial pen size
t.pensize(1)

# Define movement functions
def move_up():
    t.setheading(90)
    t.forward(5)

def move_down():
    t.setheading(270)
    t.forward(5)

def move_left():
    t.setheading(180)
    t.forward(5)

def move_right():
    t.setheading(0)
    t.forward(5)

# Define a function to toggle drawing state
def toggle_pen():
    if t.isdown():
        t.penup()  # Lift the pen
    else:
        t.pendown()  # Put the pen down

# Define functions to change the color to blue, green, and red
def set_color_blue():
    t.color("blue")

def set_color_green():
    t.color("green")

def set_color_red():
    t.color("red")

def set_color_yellow():
    t.color("yellow")

def set_color_black():
    t.color("black")

def set_color_orange():
    t.color("orange")

def set_color_gray():
    t.color("gray")

def set_color_white():
    t.color("white")

def set_color_pink():
    t.color("pink")



# Define functions to increase and decrease pen size
def increase_pen_size():
    current_size = t.pensize()
    t.pensize(current_size + 1)  # Increase pen size by 1

def decrease_pen_size():
    current_size = t.pensize()
    if current_size > 1:  # Ensure pen size doesn't go below 1
        t.pensize(current_size - 1)

# Bind arrow keys, WASD keys, space bar, and color keys to functions
screen.listen()  # Enable the screen to listen for key presses
screen.onkeypress(move_up, "Up")
screen.onkeypress(move_down, "Down")
screen.onkeypress(move_left, "Left")
screen.onkeypress(move_right, "Right")
screen.onkeypress(move_up, "w")
screen.onkeypress(move_down, "s")
screen.onkeypress(move_left, "a")
screen.onkeypress(move_right, "d")
screen.onkeypress(toggle_pen, "space")  
screen.onkeypress(set_color_blue, "b")  
screen.onkeypress(set_color_green, "g")  
screen.onkeypress(set_color_red, "r") 
screen.onkeypress(increase_pen_size, "+")  
screen.onkeypress(decrease_pen_size, "-")  
screen.onkeypress(set_color_yellow, "y")
screen.onkeypress(set_color_black, "e")
screen.onkeypress(set_color_orange, "o")
screen.onkeypress(set_color_gray, "0")
screen.onkeypress(set_color_white, "q")
screen.onkeypress(set_color_pink, "p")

# Keep the window open
screen.mainloop()
