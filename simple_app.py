import sys
from uremi import *

class Dialog:

    def __init__(self):
        self.w = Widget(width=300, height=200, margin=10, padding="20px 0px")
        b = Button('Press me!', width=200, height=30, margin="auto 50px")

        self.lbl = Label('Hello %s!' % 'world', width='80%', height='70%')
        self.lbl.style['margin'] = 'auto'

        self.w.append(self.lbl)
        self.w.append(b)

        b.on("click", self.on_bt_click)

    def on_bt_click(self):
        print("here")
        self.lbl.set("Hi there!")

#render(w, sys.stdout)

top = Dialog()
app = WebApp(top.w)
app.serve()
