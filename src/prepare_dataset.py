import os
from dotenv import load_dotenv
from langsmith import Client
import json

#環境設定########################################################################################
load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "langsmith-add"

def main():
    dataset_name = "langsmith-add"
    client = Client()
    if client.has_dataset(dataset_name=dataset_name):
        client.delete_dataset(dataset_name=dataset_name)
    dataset = client.create_dataset(dataset_name=dataset_name)

    with open('input/sample.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    inputs = []
    outputs = []
    metadatas = []
    for i in range(len(data['query'])):
        inputs.append({"question": data['query'][i],})
        outputs.append({"ground_truth": data['answer'][i],})
        metadatas.append({"evolution_type": f"メッセージ：{i}個目のデータ",})

    client.create_examples(
        inputs=inputs,
        outputs=outputs,
        metadata=metadatas,
        dataset_id=dataset.id,
    )


if __name__ == "__main__":
    main()