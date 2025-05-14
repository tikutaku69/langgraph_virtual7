import json
from typing import Any
from core import State
from logger import logger

#データ収集ノード
def collect_data(state: State) -> dict[str, Any]:
    with open("input/sample.json", "r", encoding='utf-8') as f:
        dict_json = json.load(f)
    logger.debug(f"dict_json: {dict_json}")
    logger.debug(f"dict_json['query']: {dict_json['query']}")
    logger.info("JSONファイルの読み込みが完了しました。")
    return {"query": dict_json['query']}
