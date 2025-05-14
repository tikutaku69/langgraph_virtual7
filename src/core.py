from csv import Error
import os
from pyexpat.errors import messages
from dotenv import load_dotenv
import operator
from typing import Annotated, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
import json
import time
from IPython.display import Image, display
from structure import AnswerType
from logger import logger
from tavily_search import search_with_tavily
import subprocess
from use_dataset import evaluate_dataset
#環境設定########################################################################################
load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "langsmith-add"

#ステートの定義########################################################################################
class State(BaseModel):
    query: list[str] = Field(..., description="ユーザーからの質問")
    messages: Annotated[list[str], operator.add] = Field(
        default=[], description="回答履歴"
    )
    search_results: list[str] = Field(
        default=[], description="検索結果"
    )
    trash: str = Field(
        default="", description="戻り値に困ったときに使うゴミ箱"
    )

#chat modelの初期化########################################################################################
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

#グラウンディングノード
def grounding(state: State) -> dict[str, Any]:
    logger.debug(f"grounding input state: {state}")
    queries = state.query
    search_results = []
    
    for query in queries:
        try:
            # Tavily APIを使用して検索を実行
            response = search_with_tavily(query)
            
            # 検索結果を文字列に整形
            formatted_results = []
            for result in response.get("results", []):
                formatted_results.append(f"タイトル: {result.get('title', '')}\n内容: {result.get('content', '')}")
            
            search_results.append("\n\n".join(formatted_results))
        except Exception as e:
            logger.error(f"検索中にエラーが発生しました: {e}")
            search_results.append(f"検索中にエラーが発生しました: {e}")
    
    result = {"search_results": search_results}
    logger.debug(f"grounding output: {result}")
    return result

#answeringノード
def answering(state: State) -> dict[str, Any]:
    logger.debug(f"answering input state: {state}")
    queries = state.query
    search_results = state.search_results
    prompt = ChatPromptTemplate.from_template(
"""以下の質問に対して、提供された検索結果を参考にしながら、生成AI製品エキスパートとして回答してください。
その際、最初に結論を１行で述べ、その後に詳細な説明を行ってください。

質問: {query}
検索結果: {search_results}

回答:""".strip()
    )
    chain = prompt | llm.with_structured_output(AnswerType)
    answers = []
    inputs = [{"query": query, "search_results": result} for query, result in zip(queries, search_results)]
    answers = chain.batch(inputs, config={"max_concurrency": 200})
    answers_dict = [answer.insert_dict() for answer in answers]
    messages = [f"結論: {answer['conclusion']}\n詳細: {answer['detail']}" for answer in answers_dict]
    
    # queriesとmessagesのペアをJSONデータとして書き出す
    stock_data = []
    for query, message in zip(queries, messages):
        stock_data.append({"query": query, "message": message})
    with open("temporary/stock_data.json", "w", encoding='utf-8') as f:
        json.dump(stock_data, f, ensure_ascii=False, indent=2)
    
    result = {"messages": messages}
    logger.debug(f"answering output: {result}")
    return result

#output_jsonノード
def output_json(state: State) -> dict[str, Any]:
    answer_dict = {"answer": [{"messages": message} for message in state.messages]}
    with open("output/sample.json", "w", encoding='utf-8') as f:
        json.dump(answer_dict, f, ensure_ascii=False)
    return {"trash": "JSONファイルの出力が完了しました。"}

def order_workflow():
    start_time = time.time()
    
    #グラフの作成########################################################################################
    from input import collect_data  # ここで遅延インポート
    workflow = StateGraph(State)
    workflow.add_node("collect_data", collect_data)
    workflow.add_node("grounding", grounding)
    workflow.add_node("answering", answering)
    workflow.add_node("output_json", output_json)
    workflow.set_entry_point("collect_data")
    workflow.add_edge("collect_data", "grounding")
    workflow.add_edge("grounding", "answering")
    workflow.add_edge("answering", "output_json")
    workflow.add_edge("output_json", END)

    compiled = workflow.compile()
    with open("temporary/workflow.md", "w", encoding='utf-8') as f:
        f.write("```mermaid\n")
        f.write(compiled.get_graph().draw_mermaid())
        f.write("\n```")

    # ワークフローを実行
    initial_state = State(query=[])
    result = compiled.invoke(initial_state)
    logger.debug(f"result: {result}")
    logger.info("ワークフローの実行が完了しました。")
    
    # ワークフロー完了後にデータセットを評価
    try:
        evaluate_dataset()
        logger.info(f"データセット評価結果成功")
    except ImportError:
        logger.error("use_dataset モジュールをインポートできませんでした。evaluate_dataset が実行されませんでした。")
    except Exception as e:
        logger.error(f"データセット評価中にエラーが発生しました: {e}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"実行時間: {elapsed_time:.2f} seconds")

def main():
    order_workflow()

if __name__ == "__main__":
    main()
