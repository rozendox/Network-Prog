from scapy.all import conf, sendp, Ether, ARP


def change_mac(interface, new_mac):
    conf.iface = interface
    conf.verb = 0

    # Obter o endereço MAC atual
    current_mac = get_if_addr(interface)
    print(f"Current MAC: {current_mac}")

    # Alterar o endereço MAC
    sendp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst="192.168.1.1", hwdst=new_mac), count=3, iface=interface)

    # Verificar o novo endereço MAC
    new_mac_addr = get_if_addr(interface)
    print(f"New MAC: {new_mac_addr}")


def get_if_addr(interface):
    import socket
    import fcntl
    import struct

    def get_mac(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', ifname[:15].encode('utf-8')))
        return ':'.join(['%02x' % (b[i] & 0xff) for i in range(0, 6) for b in struct.unpack('6s6s6s6s', info[18:])])

    return get_mac(interface)


if __name__ == "__main__":
    interface = "eth0"  # 
    new_mac = "00:11:22:33:44:55"  #
    change_mac(interface, new_mac)
