install:
	docker build --tag panel .
	echo "[+] Installed"

run:
	docker run -v files:/var/www/panel/bots -v db:/var/www/panel/database -v builds:/var/www/panel/files -p 80:5000 -p 5002:5002 --rm -d --name panel_container panel
	echo "[+] Success"

stop:
	docker stop panel_container
	echo "[+] Success"

uninstall:
	docker stop panel_container
	docker rmi panel
	echo "[+] Uninstalled"

restart:
	docker stop panel_container
	docker run -v files:/var/www/panel/bots -v db:/var/www/panel/database -v builds:/var/www/panel/files -p 80:5000 -p 5002:5002 --rm -d --name panel_container panel
	echo "[+] Success"
