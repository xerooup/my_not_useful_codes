import turtle
from config import settings

screen = turtle.Screen()
screen.title("Управляемая черепашка")
screen.bgcolor("white")

t = turtle.Turtle()
t.shape("turtle")
t.color("green")
t.speed(5)
t.pensize(3)

def clear_screen():
    t.clear()
    t.penup()
    t.home()
    t.pendown()

def up():
    t.forward(settings["move_distance"])

def pup():
    t.penup()

def pdown():
    t.pendown()

def tright():
    t.right(settings["rotate_angle"])

def tleft():
    t.left(settings["rotate_angle"])

def back():
    t.backward(settings["move_distance"])

screen.listen()
screen.onkey(up, "Up")
screen.onkey(back, "Down")
screen.onkey(tleft, "Left")
screen.onkey(tright, "Right")
screen.onkey(pup, "u")
screen.onkey(pdown, "d")
screen.onkey(clear_screen, "c")

instruction = turtle.Turtle()
instruction.goto(0, -350)
instruction.write("Стрелки: движение\nU/D: поднять/опустить перо\nC: очистить экран", 
                 align="center", font=("Monocraft", 12, "normal"))

screen.mainloop()