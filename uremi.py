import sys

EVENT_MAP = {}
CONN = None

def conn():
    return CONN

class Tag:

    events = ""

    def __init__(self, **styles):
        self.children = []
        self.style = styles
        self.inner = ""

    def html(self, s):
        st = ""
        for k, v in self.style.items():
            st += "{}:{};".format(k, v)
        s.write('<{} id="{}" class="{}" style="{}" {}>\n'.format(self.tag, id(self), self.class_, st, self.events.format(id(self))))
        s.write(self.inner)
        for c in self.children:
            c.html(s)
        s.write('</{}>'.format(self.tag))

    def append(self, c):
        self.children.append(c)

    def on(self, event, handler):
        global EVENT_MAP
        EVENT_MAP[(id(self), event)] = handler


class Widget(Tag):

    tag = "div"
    class_ = "Widget"

    def __init__(self, **styles):
        super().__init__(**styles)


class Label(Tag):

    tag = "p"
    class_ = "Label"

    def __init__(self, text, **styles):
        super().__init__(**styles)
        self.inner = text

    def set(self, text):
        CONN.write("innerHTML\t{}\t{}".format(id(self), text))


class Button(Tag):

    class_ = "Button"
    tag = "button"
    events = 'onclick="ev(\'{0}\', \'click\')"'

    def __init__(self, text, **styles):
        super().__init__(**styles)
        self.inner = text


def render(w, s):
    s.write("""\
<html>
<head>
<link href="res/style.css" rel="stylesheet">
<script>
var ws;

function ev(id, e) {
//    alert(id + " " + e);
    ws.send(id + " " + e + "\\n");
}
window.onload = function() {
    var wsaddr = window.location.toString().replace("http:", "ws:")
//    alert("loaded: " + wsaddr);
    ws = new WebSocket(wsaddr + "ws");
    ws.onmessage = function(ev) {
//        alert(ev.data);
        var comp = ev.data.split("\t");
        if (comp[0] == "innerHTML") {
            var el = document.getElementById(comp[1]);
            el.innerHTML = comp[2];
        }
    }
}
</script>
</head>
<body>
""")
    w.html(s)
    s.write("\n</body></html>\n")


#
# HTTP serving part
#

import server
import websocket_helper
import websocket

class WebApp:

    def __init__(self, toplevel_widget):
        self.w = toplevel_widget


    def http_handler(self, s, req):
        meth, path, proto = req.split()
        if path == b"/":
            server.skip_headers(s)
            s.write("HTTP/1.0 200 OK\r\n\r\n")
            render(self.w, s)
        elif path == b"/res/style.css":
            server.skip_headers(s)
            s.write("HTTP/1.0 200 OK\r\n\r\n")
            with open(path[1:], "rb") as f:
                data = f.read()
                s.write(data)
        elif path == b"/ws":
            websocket_helper.server_handshake(s)
            s = websocket.websocket(s)
            print("websock connected")
            while 1:
                data = s.readline()
                data = data.decode("ascii").rstrip().split()
                print(data)
                global CONN
                CONN = s
                EVENT_MAP[(int(data[0]), data[1])]()
        else:
            s.write("HTTP/1.0 404 NAK\r\n\r\n")


    def serve(self):
        print(EVENT_MAP)
        server.serve(self.http_handler)
