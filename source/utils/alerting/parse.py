import xmltodict
from xml.parsers.expat import ExpatError

from utils.logger import get_bot_logger

logger = get_bot_logger()

def parse_argv(argv: list) -> list[dict, dict, dict] | None:
    try:
        send_to, subject, message = argv[1:]
        message = xmltodict.parse(message)
        text, settings, errors = parse_data(message)

        if errors:
            raise KeyError(f"Key(s) {errors} not found.")

    except (TypeError, KeyError, ValueError, ExpatError) as err:
        msg = f'{err}\nMessage: {message}'
        logger.error(msg, exc_info=True)
        return
    
    else:
        return send_to, subject, text, settings
    
def parse_data(data: dict) -> tuple[dict | None, dict | None, list[str] | list]:
    errors = []

    try:
        text = data["root"]["body"]["messages"]
    except KeyError:
        text = None
        errors.append("messages")

    try:
        settings = data["root"]["settings"]
    except Exception:
        settings = None
        errors.append("settings")

    return text, settings, errors