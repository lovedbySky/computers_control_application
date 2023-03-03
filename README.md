# computers_control_application
This is a web-app written in Flask and sockets that allows you to control many computers from defferent networks using the command-line.

# Builder

This is a documentation for builder

Что бы сбилдить шелл нужно скопировать папку на ту систему, под которую планируется билд (windows/linux)
Далее установить python и pip
А так же установить нуитку (nuitka) и модуль standalone

 pip3 install nuitka

 pip3 install zstandard

Далее переходим в папку и прописываем:

 python3 builder.py --obfuscation true --new_name bot

Билдер может собирать файл с использованием обфускации и без неё,
Чтобы без обфускации нужно убрать из предыдущей команды флаг --obfuscation 


# Console

Документация к терминалу

Commands:

~$ status - вернёт статус листенера

~$ reload - перезапустит листенер, нужно для обновления статуса ботов

~$ show - покажет ботов, достпуных для подключения, так же можно посмотреть в Board

~$ clear - очистит консоль

~$ help - покажет первостепенную справку

~$ connect {your_ip} - подключиться к боту. Например: connect 12.56.326.1

~$ disconnect - отключиться от бота

~$ files - покажет файлы, загруженные в панель, которые можно загрузить в бота

~$ upload {filename} - загрузить файл в бота из доступных. Например: upload file.txt

~$ download - скачать файл с бота. Например: download secret.txt


# Upload file

Загрузить файлы в панель

Что бы загрузить файлы в панель нужно перейти во вкладку Upload file и загрузить файл.
Так же там отображаются все загруженные файлы и по нажатию на крестик их можно удалить


# Board

This is a documentation for board and bots

В Board можно посмотреть всех когда-либо подключанных ботов,
добавить в избранное, удалить бота,посмотреть скаченные файлы и подключиться к нему

![image](https://user-images.githubusercontent.com/101527966/222714201-dce408f1-b5a6-47f1-8f97-b358fed379b9.png)

Нажав на сердечко бот добавится в избранное и будет отображаться сверху
Так же можно посмотреть IP и нынешний статус бота, перед этим следует перезапустить листенер

![image](https://user-images.githubusercontent.com/101527966/222714235-8361caf0-bf3d-46ed-ad1f-1dab2b752bde.png)

Чтобы подключиться к боту и перейти в терминал нужно нажать на круглую консоль слева от папки
Справа от папки при нажатии на крестик бот удалиться из базы данных (навсегда)

![image](https://user-images.githubusercontent.com/101527966/222714279-4b5054b0-36a5-45c9-85c2-cae2876ea70e.png)

Нажав на папку откроется страница бота:

![image](https://user-images.githubusercontent.com/101527966/222714326-e9c0475b-fa4a-4f87-b6c8-45065c9dc3fe.png)

Здесь будут отображаться скаченные файлы


# User

В панеле один юзер - administrator

Пароль по умолчанию: "123456789"

Чтобы сменить пароль, нужно перейти в соответствующую вкладку change password
в меню чуть выше logout


# Deploy

Как развернуть панель на сервере?

Что-бы развернуть панель на сервере
(linux ubuntu/debian)
- нужно копировать на удалённый сервер панель,
перейти в ее папку и прописать команды:

 make install
 make run

После этого панель будет запущенна в docker container на вашем сервере.
Панель работает на порту 80, а листенер на 5002.

Так же у make есть другие команды:

 uninstall - удалит панель docker container с панелью и образ

 restart - перезапускает панель в docker container'е
