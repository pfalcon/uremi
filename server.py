import usocket as socket
import uselect

def serve(handler, micropython_optimize=True):
    s = socket.socket()

    ai = socket.getaddrinfo("127.0.0.1", 8080)
    print("Bind address info:", ai)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    print("Listening, connect your browser to http://<this_host>:8080/")

    poll = uselect.poll()

    while True:
        res = s.accept()
        client_sock = res[0]
        client_addr = res[1]
        print("Client address:", client_addr)
        print("Client socket:", client_sock)

        client_stream = client_sock
        poll.register(client_stream, uselect.POLLIN)
        if not poll.poll(100):
            print("Timeout in request")
        else:
            print("Request:")
            req = client_stream.readline()
            print(req)

            if req:
                handler(client_stream, req)

        poll.unregister(client_stream)
        client_stream.close()
        print()


def skip_headers(client_stream):
    while True:
        h = client_stream.readline()
        if h == b"" or h == b"\r\n":
            break
        print(h)
