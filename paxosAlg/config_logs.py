
import logging
import sys

def setup_logging():
    """
    Configura o logger raiz.
    Qualquer arquivo que importar 'logging' herdará essas configurações.
    """
    # Formato: [HORA] [NIVEL] MENSAGEM
    log_format = '%(asctime)s | %(levelname)-8s | %(message)s'
    date_format = '%H:%M:%S'

    logging.basicConfig(
        level=logging.INFO,  # Mude para DEBUG se quiser ver detalhes minuciosos
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Salva num arquivo para histórico
            logging.FileHandler("paxos_simulation.log", mode='w', encoding='utf-8'),
            # Mostra no console para você acompanhar
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("Logger configurado com sucesso via config_logs.py")