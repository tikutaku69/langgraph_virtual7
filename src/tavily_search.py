import os
from typing import Dict, Any
from logger import logger
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

def search_with_tavily(query: str) -> Dict[str, Any]:
    """
    Tavily APIを使用して検索を実行する
    
    Args:
        query (str): 検索クエリ
        
    Returns:
        Dict[str, Any]: 検索結果
    """
    try:
        client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
        
        # 検索を実行
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=1
        )
        
        results = []
        for result in response.get("results", []):
            results.append({
                "title": result.get("title", ""),
                "content": result.get("content", "")
            })
        # １質問あたりの検索結果をログに出力
        logger.debug(f"Query: {query}")
        logger.debug(f"Results: {results}")
            
        return {
            "query": query,
            "results": results
        }
    except Exception as e:
        logger.error(f"Tavily Search中にエラーが発生しました: {e}")
        return {
            "query": query,
            "results": [
                {
                    "title": "エラー",
                    "content": f"検索中にエラーが発生しました: {e}"
                }
            ]
        }
