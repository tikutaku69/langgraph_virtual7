from logging import getLogger, StreamHandler, FileHandler, Formatter, INFO, DEBUG
from datetime import datetime

def setup_logger():
    logger = getLogger(__name__)
    logger.setLevel(DEBUG)

    formatter = Formatter(
        "%(asctime)s - %(levelname)s : %(name)s : "
        "%(message)s (%(filename)s:%(lineno)d)"
    )

    s_handler = StreamHandler()
    s_handler.setLevel(INFO)
    s_handler.setFormatter(formatter)
    logger.addHandler(s_handler)

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_handler = FileHandler(f"log/raghon_{now}.log", encoding='utf-8')
    file_handler.setLevel(DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info("ログの出力を開始します。")
    return logger

# グローバルなロガーインスタンスを作成
logger = setup_logger()