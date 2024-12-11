import logging

class Logger:
    def __init__(self, log_file="app.log"):
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def log(self, message):
        logging.info(message)
