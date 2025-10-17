import nmap

scanner = nmap.PortScanner()
scanner.scan("192.168.1.0/24", "22-443")

for host in scanner.all_hosts():
    print(f"Host: {host} ({scanner[host].hostname()})")
    for proto in scanner[host].all_protocols():
        print(f"Protocolo: {proto}")
        portas = scanner[host][proto].keys()
        for porta in portas:
            print(f"Porta {porta}: {scanner[host][proto][porta]['state']}")
