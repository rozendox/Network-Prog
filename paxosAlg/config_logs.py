import logging
import sys


class ColoredFormatter(logging.Formatter):
    """
    Formatador customizado que pinta a linha inteira dependendo
    das palavras-chave encontradas na mensagem.
    """
    # Códigos ANSI para cores
    RESET = "\033[0m"
    RED = "\033[91m"  # Vermelho Claro
    GREEN = "\033[92m"  # Verde Claro
    YELLOW = "\033[93m"  # Amarelo
    BLUE = "\033[94m"  # Azul Claro
    CYAN = "\033[96m"  # Ciano

    # Formato base
    base_format = '%(asctime)s | %(levelname)-8s | %(message)s'

    def format(self, record):
        # Primeiro, formatamos a mensagem normalmente
        # Isso garante que a data e o nível fiquem no lugar certo
        formatter = logging.Formatter(self.base_format, datefmt='%H:%M:%S')
        formatted_msg = formatter.format(record)

        # Agora aplicamos a cor baseada no CONTEÚDO da mensagem
        msg_upper = str(record.msg).upper()

        # Lógica de Cores
        if "REJEIT" in msg_upper or "ERRO" in msg_upper or "FALHA" in msg_upper:
            return f"{self.RED}{formatted_msg}{self.RESET}"

        elif "ACEITOU" in msg_upper or "CONSENSO" in msg_upper or "QUORUM" in msg_upper or "PROMETENDO" in msg_upper:
            return f"{self.GREEN}{formatted_msg}{self.RESET}"

        elif "ENVIANDO" in msg_upper or "INICIANDO" in msg_upper:
            return f"{self.BLUE}{formatted_msg}{self.RESET}"

        elif "PROCESSO" in msg_upper or "NETWORK" in msg_upper:
            return f"{self.CYAN}{formatted_msg}{self.RESET}"

        # Se for warning do sistema
        elif record.levelno == logging.WARNING:
            return f"{self.YELLOW}{formatted_msg}{self.RESET}"

        # Padrão (Sem cor)
        return formatted_msg


def setup_logging():
    """
    Configura os logs:
    - Colorido no Terminal
    - Texto puro no Arquivo
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove handlers antigos se houver (evita duplicidade ao rodar threads)
    if root_logger.handlers:
        root_logger.handlers = []

    # 1. Handler do Arquivo (SEM CORES)
    file_handler = logging.FileHandler("paxos_simulation.log", mode='w', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s', datefmt='%H:%M:%S'))
    root_logger.addHandler(file_handler)

    # 2. Handler do Terminal (COM CORES)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter())
    root_logger.addHandler(console_handler)

    logging.info("Sistema de logs colorido ativado.")