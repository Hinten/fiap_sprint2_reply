import logging
from src.logger.color_text import makeCyan, makeBlue, makeYellow, makeRed, makePink
from src.settings import DEBUG

LOGGER_COLORS = {
    logging.DEBUG: makeCyan,
    logging.INFO: makeBlue,
    logging.WARNING: makeYellow,
    logging.ERROR: makeRed,
    logging.CRITICAL: makePink,
}


class LoggerColorFormatter(logging.Formatter):
    """Formata mensagens de log com cores diferentes para cada nível de log."""


    def format(self, record):
        color = LOGGER_COLORS.get(record.levelno)

        if color is not None:
            formatted_message = super().format(record)
            return color(formatted_message)

        return super().format(record)


def configurar_logger(file_name: str = 'app.log', level: int = None):
    """
    Configura o logger para o aplicativo.
    :param file_name: nome do arquivo de log. Se não for fornecido, o nome padrão é 'app.log'.
    :param level: nível de log. Se não for fornecido, o nível padrão é DEBUG se DEBUG for True, caso contrário, INFO.
    :return:
    """

    logger = logging.getLogger()

    level = level or logging.DEBUG if DEBUG else logging.INFO

    logger.setLevel(level)

    format_string = '[%(levelname)s] %(asctime)s %(filename)s: %(message)s'

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    formatter = LoggerColorFormatter(format_string)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(file_name)
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(file_handler)

if __name__ == '__main__':
    configurar_logger()
    logging.info('This is an info message')
    logging.debug('This is a debug message')
    logging.warning('This is a warning message')
    logging.error('This is an error message')
    logging.critical('This is a critical message')