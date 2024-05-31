# Port Scanner
Simple Port Scanner Using Python3

Syntax: python portscanner.py [options] [ip] 

Options:

-v Enable Verbose Mode

-n Check if Target is Online

-o Print Output to File

-q Quiet Mode

-f Read IP(s) From File

-h View Help Menu

Examples:

python portscanner.py 192.168.88.10

python portscanner.py -v 192.168.88.10

python portscanner.py -q 192.168.88.10

python portscanner.py 192.168.88.0-255

python portscanner.py -o file.txt 192.168.88.0
python portscanner.py -f file.txt 192.168.88.0
