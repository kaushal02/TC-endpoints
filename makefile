ALL:
	sudo chmod 777 Data
	sudo apachectl restart
new:
	sudo rm -rf Data/*
	sudo chmod 777 Data
	sudo apachectl restart
