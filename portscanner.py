import socket
import sys
import subprocess
from datetime import datetime
from colorama import Fore, Style

verbose = False  # flag to show that verbose mode is enabled
write = False
target = None
targets_range = None
multiple_targets = False
quiet = False
read_ips = False
scanned_ips = []
check_alive = False

def print_help():
    print(Fore.YELLOW + '-' * 50 + Style.RESET_ALL)
    print(Fore.RED + "Syntax: python portscanner.py [options] <ip>" + Style.RESET_ALL)
    print(Fore.MAGENTA + "Options: " + Style.RESET_ALL)
    print(Fore.WHITE + "-v    Enable Verbose Mode")
    print(Fore.WHITE + "-n    Check if Target is Online")
    print(Fore.WHITE + "-o    Print Output to File")
    print(Fore.WHITE + "-q    Quiet Mode")
    print(Fore.WHITE + "-f    Read IP(s) From File")
    print(Fore.WHITE + "-h    View Help Menu")
    print(Fore.MAGENTA + "Examples: " + Style.RESET_ALL)
    print(Fore.LIGHTBLACK_EX + "python portscanner.py 192.168.88.10")
    print(Fore.LIGHTBLACK_EX + "python portscanner.py -v 192.168.88.10")
    print(Fore.LIGHTBLACK_EX + "python portscanner.py -q 192.168.88.10")
    print(Fore.LIGHTBLACK_EX + "python portscanner.py 192.168.88.0-255")
    print(Fore.LIGHTBLACK_EX + "python portscanner.py -o file.txt 192.168.88.0")
    print(Fore.LIGHTBLACK_EX + "python portscanner.py -f file.txt 192.168.88.0")
    print(Fore.YELLOW + '-' * 50 + Style.RESET_ALL)

def print_banner(word):
    print(Fore.YELLOW + '-' * 50 + Style.RESET_ALL)
    print(Fore.LIGHTMAGENTA_EX + '\t\tPORT SCANNER' + Style.RESET_ALL)
    if multiple_targets:
        print(Fore.BLUE + '\tScanning ' + word + str(target) + "-" + str(targets_range) + Style.RESET_ALL)
    else:
        print(Fore.BLUE + '\tScanning ' + word + str(target) + Style.RESET_ALL)

    if read_ips:
        print(Fore.BLUE + '\tScanning ' + word + Style.RESET_ALL)
    print(Fore.GREEN + "\tTime Started " + str(datetime.now()) + Style.RESET_ALL)
    if verbose:
        print(Fore.WHITE + '\tVerbose mode enabled' + Style.RESET_ALL)
    print(Fore.YELLOW + '-' * 50 + Style.RESET_ALL)

def check_target_response(ip):
    # Use the ping command to check the host
    try:
        # `-c 1` means send 1 packet, `-W 1` means timeout after 1 second (Linux/Mac)
        # For Windows use `-n 1` for one packet and `-w 1000` for 1-second timeout
        if sys.platform != "win32":
            command = ["ping", "-c", "1", "-W", "1", ip] 
        else:
            command = ["ping", "-n", "1", "-w", "1000", ip]
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
        return True
    except subprocess.CalledProcessError:
        return False
    
def write_file(port, message):
    if write:
        with open(file_name, mode='a') as file:
            if read_ips and ip not in scanned_ips:
                file.write(f'Started Scanning {ip}\n')
                scanned_ips.append(ip)
            file.write(f'Port {port} is {message}\n')

def write_file_targets(target, message):
    if write:
        with open(file_name, mode='a') as file:
            file.write(f'Target {target} {message}\n')


def scan_one_target(target):
    target = socket.gethostbyname(target)  # translate host name to IPv4
    if not check_target_response(target):
        print(Fore.RED + f'Target {target} is not responding.' + Style.RESET_ALL)
        if not read_ips:
            sys.exit()
        else:
            return

    if read_ips:
        print(Fore.GREEN + f'Scanning {target} has Started...' + Style.RESET_ALL)
    
    try:
        for port in range(1, 65535):
            #AF_INET => IPV4
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket.setdefaulttimeout(0.2)
            #RETURN ERROR
            #IF ERROR = 0 => NO ERROR OCCURED
            #ELSE ERROR = 1 => THEIR IS ERROR
            result = s.connect_ex((target, port))
            if verbose and not quiet:
                if result == 0:
                    print(Fore.GREEN + f'Port {port} is open' + Style.RESET_ALL)
                    if write:
                        write_file(port, "is open")
                else:
                    print(Fore.RED + f'Port {port} is closed' + Style.RESET_ALL)
                    write_file(port, "is closed")
            elif verbose and quiet:
                if result == 0:
                    if write:
                        write_file(port, "is open")
                else:
                    write_file(port, "is closed")
            elif not verbose and quiet:
                if result == 0:
                    if write:
                        write_file(port, "is open")
            else:
                if result == 0:
                    print(Fore.GREEN + f'Port {port} is open' + Style.RESET_ALL)
                    if write:
                        write_file(port, "is open")
            s.close()  # close the connection on this port to try and connect to the next port
    except KeyboardInterrupt:  # if we hit ctrl+c
        print('\nExiting Program')
        sys.exit()  # exit the program peacefully
    except socket.gaierror:
        print('Hostname could not be resolved')
        sys.exit()
    except socket.error:
        print('Could not connect to the server')
        sys.exit()

def scan_multiple_targets(ip, rang):
    print(Fore.RED + ip + Style.RESET_ALL)
    split_ip = ip.split('.')
    for i in range(int(split_ip[3]), int(rang) + 1):
        ip_scan = split_ip[0] + "." + split_ip[1] + "." + split_ip[2] + "." + str(i)
        target = socket.gethostbyname(ip_scan)  # translate host name to IPv4
        if not check_target_response(target):
            print(Fore.RED + f'Target {target} is not responding.' + Style.RESET_ALL)
            write_file(target, 'did not respond...')
            continue
        else:
            print(Fore.GREEN + f'Scanning {target} has Started...' + Style.RESET_ALL)
            write_file(target, 'Scanning...')
        try:
            for port in range(1, 65535):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket.setdefaulttimeout(0.2)
                result = s.connect_ex((target, port))
                if verbose and not quiet:
                    if result == 0:
                        print(Fore.GREEN + f'Port {port} is open' + Style.RESET_ALL)
                        write_file(port, 'is open')
                    else:
                        print(Fore.RED + f'Port {port} is closed' + Style.RESET_ALL)
                        write_file(port, 'is closed')
                elif verbose and quiet:
                    if result == 0:
                        if write:
                            write_file(port, "is open")
                    else:
                        write_file(port, "is closed")
                elif not verbose and quiet:
                    if result == 0:
                        if write:
                            write_file(port, "is open")
                else:
                    if result == 0:
                        print(Fore.GREEN + f'Port {port} is open' + Style.RESET_ALL)
                        write_file(port, 'is open')
                s.close()  # close the connection on this port to try and connect to the next port
        except KeyboardInterrupt:  # if we hit ctrl+c
            print('\nExiting Program')
            sys.exit()  # exit the program peacefully
        except socket.gaierror:
            print('Hostname could not be resolved')
            sys.exit()
        except socket.error:
            print('Could not connect to the server')
            sys.exit()

def read_ips_file():
    ips = []
    with open(read_file_name, mode='r') as file:
        try:
            for line in file:
                ip = line.strip()  # Remove any surrounding whitespace (including newlines)
                ips.append(ip)
        except Exception as e:
            print(Fore.RED + f'Error While Reading {read_file_name}: {e}' + Style.RESET_ALL)
    return ips


i = 0
if len(sys.argv) < 2:
    print_help()
    sys.exit()
else:
    i = 0
    while i < len(sys.argv):
        option = sys.argv[i]
        if option == '-v':
            verbose = True
        elif option == '-o':
            write = True
            file_name = sys.argv[i + 1]
            i += 1  # skip the next argument as it's the file name
        elif option == '-h':
            print_help()
            sys.exit()
        elif option == '-q':
            quiet = True
        elif option == '-f':
            read_file_name = sys.argv[i + 1]
            read_ips = True
            i+= 1
        elif option == '-n':
            check_alive = True
        elif option.find('.') != -1:
            parts = option.split('.')
            if len(parts) == 4 and parts[len(parts) - 1].find('-') == -1 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
                target = option
            elif len(parts) == 2:
                target = parts[0] + "." + parts[1]
                target = socket.gethostbyname(target)
            elif len(parts) == 3 and i > 1:
                target = parts[0] + "." + parts[1] + "." + parts[2]
                target = socket.gethostbyname(target)
            
            targets_parts = option.split('-')
            if len(targets_parts) == 2:
                target = targets_parts[0]
                targets_range = int(targets_parts[1])
        i += 1

if targets_range == None:
    if not read_ips:
        # add a banner
        print_banner('Target: ')
        if check_alive:
            if check_target_response(target):
                if write:
                    write_file_targets(target, 'is Alive')
                if not quiet:
                    print(Fore.GREEN + f'Target {target} is Alive' + Style.RESET_ALL)
            else:
                if write:
                    write_file_targets(target, 'is Not Alive')
                if not quiet:
                    print(Fore.RED + f'Target {target} is Not Alive' + Style.RESET_ALL)
            sys.exit()
        else:
            scan_one_target(target) 
    else:
        print_banner('Targets... ')
        ips = read_ips_file()
        for ip in ips:
            scan_one_target(ip)
else:
    #add a banner
    multiple_targets = True
    print_banner('Targets: ')
    if not check_alive:
        scan_multiple_targets(target, targets_range)
    else:
        base_ip = target.rsplit('.', 1)[0]
        for i in range(int(target[len(target) - 1]), int(targets_range) + 1):
            target = f"{base_ip}.{i}"
            if check_target_response(target):
                if write:
                    write_file_targets(target, 'is Alive')
                if not quiet:
                    print(Fore.GREEN + f'Target {target} is Alive' + Style.RESET_ALL)
            else:
                if write:
                    write_file_targets(target, 'is Not Alive')
                if not quiet:
                    print(Fore.RED + f'Target {target} is Not Alive' + Style.RESET_ALL)
        sys.exit()