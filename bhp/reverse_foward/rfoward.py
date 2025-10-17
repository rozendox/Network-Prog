"""
 fixme -> parse_options and getpass not working
    verbose
    and setDaemon depreciated


"""


import paramiko
import threading
import socket
import sys

def reverse_forward_tunnel(server_port, remot_host, remot_port, transport):
    transport.request_port_foward('', server_port)
    while True:
        chan = transport.accept(1000)
        if chan is None:
            continue
        thr = threading.Thread(target=handler, args=(chan, remot_host, remot_port))

        thr.setDaemon(True) # deprec
        thr.start()


def handler(chan, host, port):
    sock = socket.socket():
    try:
        sock.connect((host, port))
    except Exception as e:
        verbose('FOWARD REQUEST TO %s:%d FAILED: %r' % (host, port, e)) # verbose not working
        return

    while True

def main():
    option, server, remote = parse_options() # here
    password = None
    if option.readpass:
        password = getpass.getpass('ENTER SSH PASSWORD') # here
    client = paramiko.SSHClient()
    client.load_system_hostkeys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    verbose('Conneting to SSH host %s %d ...' % (server[0], ssh_port[1]))
    try:
        client.connect(server[0], server[1], username=option.user, key_filename=option.key_filename,
                       look_for_keys=options.look_for_keys, password=password)
    except Exception as e:
        print('*** Failed to connect to %s:%d...' % (server[0], server[1]))

    try:
        reverse_forward_tunnel(options.port, remote[0], remote[1], client.get_transport()) # here
    except KeyboardInterrupt:
        print("C-c: PORT FOWARDING STOPPED")
        sys.exit(0)
