import socket
import time
import sys

address = ("localhost", 8080)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(address)
sock.listen(2)
print("server up and running\n Listening for connections\n")

clients = 0

while True:
    con, addr = sock.accept()

    if con:
        print(f"got hook from {addr}")
        response = con.recv(4096)
        if response == b"CID_req":
            con.send(f"CID {str(clients)}".encode())
            clients += 1
        else:
            print(response.decode("utf-8"))

        # if not con:

    command = input()
    con.send(f"CID {command}".encode())
    response = con.recv(4096).decode("utf-8")
    if response is None:
        continue
    print(response)
    command_follow_up = input()
    con.send(command_follow_up.encode())
    print(con.recv(4096).decode("utf-8"))
    con.close()


sock.close()
sys.exit(1)
