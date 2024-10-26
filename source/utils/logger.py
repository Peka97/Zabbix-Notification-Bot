import logging

from config import CURRENT_CONFIG

LEVEL = CURRENT_CONFIG.logger_level

class CustomFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        record.levelname = "{:^8s}".format(record.levelname)
        return super().format(record)

formatter = CustomFormatter(
    fmt="%(asctime)s [%(levelname)s] %(pathname)s::%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
loggers = []

def create_bot_logger(name='bot', level=LEVEL):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    handlers = [
        logging.FileHandler(
            f'/lib/zabbix/alertscripts/Zabbix-Notification-Bot/source/logs/{name}.log',
        ),
        logging.StreamHandler(),
    ]
    
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    
    loggers.append(logger)
    return logger

def get_bot_logger(name='bot', level=LEVEL):
    print(name)
    for logger in loggers:
        if logger.name == name and logger.level == level:
            return logger
    
    logger = create_bot_logger(name, level)
    return logger
    
if __name__ == '__main__':
    logger = get_bot_logger()
    logger.debug('msg')
    logger.info('msg')
    logger.warning('msg')
    logger.error('msg')
    logger.critical('msg')
    