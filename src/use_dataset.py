import os
from dotenv import load_dotenv
import json
from numpy import average
from openai import OpenAI
import time
from tqdm import tqdm  # Progress bar

# 評価対象の関数
def target(inputs: dict) -> dict:
    with open("temporary/stock_data.json", "r", encoding="utf-8") as f:
        stock_data = json.load(f)
    
    question = inputs["question"]
    for item in stock_data:
        if item.get("query") == question:
            return {"response": item.get("message", "")}
    
    # 一致するクエリが見つからない場合は、ログ出力しておいてquestionをreturnする
    print(f"以下のquestionに一致するクエリが見つかりませんでした: {question[:50]}...")
    return {"response": question[:50]}

# 評価プロンプト
instructions = """生徒の答えをGround Truthと比較して、概念の類似性を評価し、0～100点で採点する： 
- 0： 概念の一致と類似はない
- 100: 概念的な一致と類似性がほとんど、または完全に一致する
- 重要な基準 正確な表現ではなく、概念が一致していること。
"""

def accuracy(student_answer, ground_truth) -> int:
    api_key = os.getenv("OPENAI_API_KEY")
    openai_client = OpenAI(api_key=api_key)
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            { "role": "system", "content": instructions },
            {
                "role": "user",
                "content": f"""Ground Truth answer: {ground_truth}; 
                Student's Answer: {student_answer}
                
                点数を0～100の数字のみで出力してください。"""
            },
        ]
    )
    
    # レスポンスからスコアを抽出
    response_text = response.choices[0].message.content.strip()
    try:
        # 数字部分のみを抽出して整数に変換
        score = int(''.join(filter(str.isdigit, response_text)))
        # 範囲を0-100に制限
        score = max(0, min(score, 100))
    except:
        # 変換できない場合のデフォルト値
        score = 0
    
    return score

def evaluate_dataset():
    start_time = time.time()
    # print(f"評価実験を開始します。")

    # 環境設定
    load_dotenv()
    
    # データセットを読み込む
    with open("temporary/stock_data.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)
    
    scores = []
    
    # 1つずつ評価する
    for item in tqdm(dataset):
        question = item.get("query", "")
        ground_truth = item.get("expected_output", "")
        
        # targetを呼び出してレスポンスを得る
        output = target({"question": question})
        
        # 評価する
        score = accuracy(output["response"], ground_truth)
        scores.append(score)
        
        # レート制限を避けるための小さな待機
        time.sleep(0.5)

    end_time = time.time()
    execution_time = end_time - start_time
    # print(f"評価実験が完了しました。所要時間: {execution_time:.2f}秒")
    average_score = int(sum(scores) / len(scores)) if scores else 0
    print(average_score)
    # print(f"個々のスコア: {scores}")

    return scores

if __name__ == "__main__":
    evaluate_dataset()
