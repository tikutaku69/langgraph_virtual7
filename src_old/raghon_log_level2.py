from csv import Error
import os
from dotenv import load_dotenv

import operator
from typing import Annotated
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.runnables import ConfigurableField

from typing import Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langgraph.graph import StateGraph

from langgraph.graph import END

from logging import getLogger, StreamHandler, FileHandler, Formatter, INFO, ERROR
from datetime import datetime

# ログの設定########################################################################################
logger = getLogger(__name__)
logger.setLevel(INFO)

formatter = Formatter(
    "%(asctime)s - %(levelname)s : %(name)s : "
    "%(message)s (%(filename)s:%(lineno)d)"
)

s_handler = StreamHandler()
s_handler.setLevel(ERROR)
s_handler.setFormatter(formatter)
logger.addHandler(s_handler)

now = datetime.now().strftime("%Y%m%d_%H%M%S")
file_handler = FileHandler(f"log/raghon_{now}.log", encoding='utf-8')
file_handler.setLevel(INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logger.info("ログの出力を開始します。")

#環境設定########################################################################################
load_dotenv()

# os.environ["OPENAI_API_KEY"] = userdata.get("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
# os.environ["LANGCHAIN_API_KEY"] = userdata.get("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "9.3 LangGraph"

#ロールの定義########################################################################################
ROLES = {
    "1": {
        "name": "一般知識エキスパート",
        "description": "幅広い分野の一般的な質問に答える",
        "details": "幅広い分野の一般的な質問に対して、正確で分かりやすい回答を提供してください。"
    },
    "2": {
        "name": "生成AI製品エキスパート",
        "description": "生成AIや関連製品、技術に関する専門的な質問に答える",
        "details": "生成AIや関連製品、技術に関する専門的な質問に対して、最新の情報と深い洞察を提供してください。"
    },
    "3": {
        "name": "カウンセラー",
        "description": "個人的な悩みや心理的な問題に対してサポートを提供する",
        "details": "個人的な悩みや心理的な問題に対して、共感的で支援的な回答を提供し、可能であれば適切なアドバイスも行ってください。"
    }
}

#ステートの定義########################################################################################
class State(BaseModel):
    query: str = Field(..., description="ユーザーからの質問")
    current_role: str = Field(
        default="", description="選定された回答ロール"
    )
    messages: Annotated[list[str], operator.add] = Field(
        default=[], description="回答履歴"
    )
    current_judge: bool = Field(
        default=False, description="品質チェックの結果"
    )
    judgement_reason: str = Field(
        default="", description="品質チェックの判定理由"
    )

#chat modelの初期化########################################################################################
# llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
# 後からmax_tokensの値を変更できるように、変更可能なフィールドを宣言
llm = llm.configurable_fields(max_tokens=ConfigurableField(id='max_tokens'))

#ノードの定義########################################################################################
#sectionノード
def selection_node(state: State) -> dict[str, Any]:
    query = state.query
    role_options = "\n".join([f"{k}. {v['name']}: {v['description']}" for k, v in ROLES.items()])
    prompt = ChatPromptTemplate.from_template(
"""質問を分析し、最も適切な回答担当ロールを選択してください。

選択肢:
{role_options}

回答は選択肢の番号（1、2、または3）のみを返してください。

質問: {query}
""".strip()
    )
    # 選択肢の番号のみを返すことを期待したいため、max_tokensの値を1に変更
    chain = prompt | llm.with_config(configurable=dict(max_tokens=1)) | StrOutputParser()
    role_number = chain.invoke({"role_options": role_options, "query": query})

    selected_role = ROLES[role_number.strip()]["name"]
    return {"current_role": selected_role}

#answeringノード
def answering_node(state: State) -> dict[str, Any]:
    query = state.query
    role = state.current_role
    role_details = "\n".join([f"- {v['name']}: {v['details']}" for v in ROLES.values()])
    prompt = ChatPromptTemplate.from_template(
"""あなたは{role}として回答してください。以下の質問に対して、あなたの役割に基づいた適切な回答を提供してください。

役割の詳細:
{role_details}

質問: {query}

回答:""".strip()
    )
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"role": role, "role_details": role_details, "query": query})
    return {"messages": [answer]}

#checkノード
class Judgement(BaseModel):
    judge: bool = Field(default=False, description="判定結果")
    reason: str = Field(default="", description="判定理由")

def check_node(state: State) -> dict[str, Any]:
    query = state.query
    answer = state.messages[-1]
    prompt = ChatPromptTemplate.from_template(
"""以下の回答の品質をチェックし、問題がある場合は'False'、問題がない場合は'True'を回答してください。
また、その判断理由も説明してください。

ユーザーからの質問: {query}
回答: {answer}
""".strip()
    )
    chain = prompt | llm.with_structured_output(Judgement)
    result: Judgement = chain.invoke({"query": query, "answer": answer})

    return {
        "current_judge": result.judge,
        "judgement_reason": result.reason
    }

def main():
    #ログの設定########################################################################################
    logger.error("ログの確認")

    # #グラフの作成########################################################################################
    # workflow = StateGraph(State)
    # workflow.add_node("selection", selection_node)
    # workflow.add_node("answering", answering_node)
    # workflow.add_node("check", check_node)
    # workflow.set_entry_point("selection")
    # workflow.add_edge("selection", "answering")
    # workflow.add_edge("answering", "check")

    # # checkノードから次のノードへの遷移に条件付きエッジを定義
    # # state.current_judgeの値がTrueならENDノードへ、Falseならselectionノードへ
    # workflow.add_conditional_edges(
    #     "check",
    #     lambda state: state.current_judge,
    #     {True: END, False: "selection"}
    # )

    # compiled = workflow.compile()

    # initial_state = State(query="生成AIについて教えてください")
    # result = compiled.invoke(initial_state)
    # # print(result)
    # print(result["messages"][-1])

if __name__ == "__main__":
    main()