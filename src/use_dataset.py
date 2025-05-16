import os
from urllib import response
from dotenv import load_dotenv
from langsmith import Client
import json
from langsmith import wrappers, Client
from pydantic import BaseModel, Field
from openai import OpenAI
from logger import logger
import time


# 評価対象の関数
def target(inputs: dict) -> dict:
    with open("temporary/stock_data.json", "r", encoding="utf-8") as f:
        stock_data = json.load(f)
    
    question = inputs["question"]
    for item in stock_data:
        if item.get("query") == question:
            logger.debug(f"一致するクエリが見つかりました: {question[:50]}...{item.get('message')[:50]}...")
            return {"response": item.get("message", "")}
    
    # 一致するクエリが見つからない場合は、ログ出力しておいてquestionをreturnする
    logger.error(f"以下のquestionに一致するクエリが見つかりませんでした: {question[:50]}...")
    return {"response": question[:50]}


# 評価プロンプト
instructions = """生徒の答えをGround Truthと比較して、概念の類似性を評価し、0～100点で採点する： 
- 0： 概念の一致と類似はない
- 100: 概念的な一致と類似性がほとんど、または完全に一致する
- 重要な基準 正確な表現ではなく、概念が一致していること。
"""

class Grade(BaseModel):
    score: int = Field(
        description="回答が参照回答に対して正確かどうかを示す整数。0～100。"
    )

# 評価軸：正確さ
def accuracy(outputs: dict, reference_outputs: dict) -> bool:
    openai_client = wrappers.wrap_openai(OpenAI())
    response = openai_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            { "role": "system", "content": instructions },
            {
                "role": "user",
                "content": f"""Ground Truth answer: {reference_outputs["ground_truth"]}; 
                Student's Answer: {outputs["response"]}"""
            },
        ],
        response_format=Grade,
    )
    score = response.choices[0].message.parsed.score
    logger.debug(f"正確性評価が完了しました。スコア: {score}")
    return score


def evaluate_dataset():
    logger.info("評価実験を開始します...")
    start_time = time.time()

    #環境設定########################################################################################
    load_dotenv()

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_PROJECT"] = "langsmith-add"

    client = Client()

    # evaluator
    experiment_results = client.evaluate(
        target,
        data="langsmith-add",
        evaluators=[accuracy,],
        experiment_prefix="ワークフローの結果に対して評価",
        max_concurrency=2,
    )

    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"評価実験が完了しました。所要時間: {execution_time:.2f}秒")

    return experiment_results


if __name__ == "__main__":
    evaluate_dataset()