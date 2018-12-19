## Anleitung - software

### Betriebssystem installieren

Zuerst brauchen wir die neueste Version von Raspbian für unseren Raspberry Pi, die hier kostenlos heruntergeladen werden kann: [https://www.raspberrypi.org/downloads/raspbian/](https://www.raspberrypi.org/downloads/raspbian/)

Um es einfacher zu gestalten entschieden wir uns dazu, die Image Version mit Desktop zu nutzen.

Eine detaillierte Installationsanleitung auf englisch findet man ebenso auf RaspberryPi.org: [https://www.raspberrypi.org/documentation/installation/installing-images/](https://www.raspberrypi.org/documentation/installation/installing-images/)

### Datenbankinstallation

Im nächsten Schritt installieren wir die Datenbank auf unserem Raspberry Pi.
Auch hierzu gibt es viele Anleitungen im Netz.

Folgende Anleitung empfanden wir als sehr übersichtlich und verständnissvoll.

In unserem Fall ist es jedoch ausreichend, Teil 1 bis Teil 4 zu folgen (Apache2, PHP5 - Webserver, MySQL, PhpMyAdmin). Teil 5 beschäftigt sich mit der Installation eines FTP-Servers, den wir hier nicht benötigen.

[https://tutorials-raspberrypi.de/webserver-installation-apache2/](https://tutorials-raspberrypi.de/webserver-installation-apache2/)

### Einrichtung des Webservers und der Datenbank
Alle erforderlichen Dateien für das AdminInterface sind im Ordner html zu finden. Dieser wird einfach komplett auf dem Raspberry unter /var/http gespeichert.
Wichtig hierbei ist jedoch, dass man die Usernames und Passwörter in den php Files anpasst!

Anschließend muss noch die Datei doorMaster.sql in PhpMyAdmin importiert werden.

Hierzu öffnet man PhpMyAdmin im Webbrowser, klickt auf "Datenbanken" im oberen Menü, dann auf die Datenbank in die importiert werden soll, anschließend auf "Importieren".
Dann muss nur noch die Datei "doorMaster.sql" aus diesem Repository ausgewählt werden und mit dem Button "Go" importiert werden.

### Python Skripte einfügen
Die Python Skripte befinden sich im Ordner doorControl in diesem Repository. Dieser muss einfach komplett im home-Ordner des angemeldeten Nutzers in Raspbian gespeichert werden.

### dependencies - Abhängigkeiten
Um das System zum Laufen zu kriegen müssen noch einige Module mit dem Terminal installiert werden.

1. Python
Falls das Python-Paketinstallationsprogramm pip noch nicht installiert ist, kann dies mit dem command
  >$ sudo apt-get install python-pip

nachgeholt werden.

Desweiteren benötigen wir einige Pakete für die python-SQL-Verbindung:

  >$ sudo pip install pip --upgrade
  >$ sudo apt-get build-dep python-mysqldb

2. NFC
Unser Python Skript nutzt den Befehl "nfc-poll" aus der Bibliothek "libnfc". Diese kann durch den Befehl
  >$ git clone https://github.com/nfc-tools/libnfc.git

heruntergeladen werden.
Bevor diese installiert werden kann, muss allerdings das Skript dazu angepasst werden!

Das zu anpassende Skript befindet sich nach dem clone im home-Verzeichnis unter libnfc-master/examples/nfc-poll.c und muss durch das gleichnamige skript im Ordner "skripte" in diesem Repository ersetzt werden. Dies ist wesentlich einfacher, wenn man es über den Dateimanager macht.

anschließend wechselt man im Terminal in den Ordner libnfc-master.

Um die Bibliothek zu installieren sind folgende Befehle notwendig:

  >$ autoreconf -vis
  >$ ./configure --enable-doc
  >$ make
  >$ sudo make install

3. i²c

Der RaspberryPi kommuniziert über die Schnittstelle i²c mit dem NFC Shield.

Auch hierzu müssen dependencies installert werden.
Eine detaillierte Anleitung auf deutsch ist unter folgendem Link zu finden:

[http://www.netzmafia.de/skripten/hardware/RasPi/RasPi_I2C.html](http://www.netzmafia.de/skripten/hardware/RasPi/RasPi_I2C.html)

### Puzzlestücke zusammenfügen

to be continued ...
