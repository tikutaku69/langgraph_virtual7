from src import raghon_batch_catch
from src.raghon_batch_catch import answering_node, State
from src.raghon_batch_catch import main
import os
import json
import pytest

# 単一のクエリに対する応答をテスト
def test_answering_node_1():
    state = State(query=["AIの未来について教えてください。"])
    result = answering_node(state)
    assert "messages" in result
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], str)

# 複数のクエリに対する応答をテスト
def test_answering_node_multiple_queries():
    state = State(query=["AIの未来について教えてください。", "生成AIの最新技術は何ですか？"])
    result = answering_node(state)
    assert "messages" in result
    assert len(result["messages"]) == 2
    for message in result["messages"]:
        assert isinstance(message, str)

# 空のクエリに対するエラーメッセージをテスト
def test_answering_node_empty_query():
    state = State(query=[""])
    result = answering_node(state)
    assert "messages" in result
    assert len(result["messages"]) == 1
    assert result["messages"][0] == "エラーが発生しました。もう一度お試しください。"

# 無効なロールに対するエラーメッセージをテスト
def test_answering_node_invalid_role():
    state = State(query=["AIの未来について教えてください。"], current_role="未知のロール")
    result = answering_node(state)
    assert "messages" in result
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], str)

# 非常に長いクエリに対する応答をテスト
def test_answering_node_long_query():
    long_query = "AIの未来について教えてください。" * 1000
    state = State(query=[long_query])
    result = answering_node(state)
    assert "messages" in result
    assert len(result["messages"]) == 1
    
# main関数でjson出力がされているかのテスト
def test_main_json_output(monkeypatch):
    # テスト用の入力JSONファイルを作成
    input_data = {"query": ["AIの未来について教えてください。"]}
    input_file = os.path.join("tests", "sample.json")
    with open(input_file, "w", encoding='utf-8') as f:
        json.dump(input_data, f, ensure_ascii=False)

    # 環境変数を一時的に設定
    monkeypatch.setenv("INPUT_JSON_PATH", str(input_file))
    output_file = os.path.join("tests", "output.json")
    monkeypatch.setenv("OUTPUT_JSON_PATH", str(output_file))

    # モック関数を定義
    def mock_invoke(state):
        return {
            'query': ['AIの未来について教えてください。'],
            'current_role': '一般知識エキスパート',
            'messages': ['AIの未来について考えると、私たちが直面するさまざまな可能性や課題が浮かび上がります。AI技術は急速に進化しており、その影響は私たちの生活、仕事、社会全体に及ぶと予想されます。ここでは、AIの未来に関するいくつかの重要な側面を詳しく探っていきたいと思います。\n\nまず、AIの進化における技術的な側面について考えてみましょう。現在、機械学習や深層学習といった技術が急速に発展しており、これによりAIはますます高度なタスクをこなすことができるようになっています。例えば、自然言語処理の分野では、AIは人間の言語を理解し、生成する能力が飛躍的に向上しています。これにより、カスタマーサポートやコンテンツ生成、翻訳などの分野での利用が進んでいます。今後、AIはさらに多くのデータを学習し、より複雑な問題を解決する能力を持つようになるでしょう。\n\n次に、AIの社会的な影響について考えると、雇用の変化が大きなテーマとなります。AIの導入により、特定の職業が自動化される一方で、新たな職業が生まれることも予想されます。例えば、データサイエンティストやAIエンジニアといった職業は今後ますます需要が高まるでしょう。しかし、これに伴い、従来の職業に従事していた人々が新たなスキルを習得する必要が生じるため、教育や再教育の重要性が増すことが考えられます。社会全体として、AIによる変化に適応するための戦略を考えることが求められるでしょう。\n\nまた、AIの倫理的な側面も無視できません。AIが人間の生活に深く関与するようになるにつれて、プライバシーやセキュリティ、バイアスといった問題が浮上します。AIが収集するデータの扱いや、そのデータを基にした意思決定がどのように行われるかは、社会的な信頼を築く上で非常に重要です。今後、AIの開発者や企業は、倫理的なガイドラインを遵守し、透明性を持った運用を行うことが求められるでしょう。これにより、AIがもたらす利益を最大化しつつ、リスクを最小限に抑えることが可能になります。\n\nさらに、AIの未来には、医療や環境問題、交通など、さまざまな分野での応用が期待されています。例えば、医療分野では、AIを活用した診断支援システムや個別化医療が進展することで、より早期かつ正確な治療が可能になるでしょう。また、環境問題においては、AIを用いたデータ分析により、気候変動の予測や資源の効率的な利用が進むことが期待されます。交通分野では、自動運転技術の進化により、交通事故の減少や渋滞の緩和が実現する可能性があります。\n\n最後に、AIの未来は私たちの価値観や文化にも影響を与えるでしょう。AIが人間の生活にどのように組み込まれるかは、私たち自身の選択や社会の合意によって決まります。AIをどのように活用し、どのような社会を築いていくのかは、私たち一人ひとりの責任でもあります。したがって、AIの未来を考える際には、技術的な側面だけでなく、倫理的、社会的な側面も含めた包括的な視点が必要です。\n\nこのように、AIの未来は多岐にわたる可能性を秘めており、私たちの生活や社会に大きな影響を与えることが予想されます。技術の進化に伴い、私たちがどのようにAIと共存し、活用していくかが、今後の重要な課題となるでしょう。'],
            'current_judge': False,
            'judgement_reason': ''
        }

    # モック関数を適用
    monkeypatch.setattr(raghon_batch_catch, 'answering_node', mock_invoke)

    # main関数を実行
    main(str(input_file), str(output_file))

    # 出力されたJSONファイルを読み込んで検証
    with open(output_file, "r", encoding='utf-8') as f:
        output_data = json.load(f)
    
    assert "answer" in output_data
    assert len(output_data["answer"]) == 1
    assert "messages" in output_data["answer"][0]
    assert isinstance(output_data["answer"][0]["messages"], str)

    # テストが終わった後にファイルを削除
    os.remove(input_file)
    os.remove(output_file)

# 無効な入力JSONファイルに対するエラーハンドリングをテスト
def test_main_invalid_json(monkeypatch, tmpdir):
    # 無効な入力JSONファイルを作成
    input_file = tmpdir.join("invalid_sample.json")
    with open(input_file, "w", encoding='utf-8') as f:
        f.write("invalid json")

    # 環境変数を一時的に設定
    monkeypatch.setenv("INPUT_JSON_PATH", str(input_file))
    output_file = tmpdir.join("output.json")
    monkeypatch.setenv("OUTPUT_JSON_PATH", str(output_file))

    # main関数を実行してエラーが発生することを確認
    with pytest.raises(json.JSONDecodeError):
        main(str(input_file), str(output_file))

# 出力ディレクトリが存在しない場合のテスト
def test_main_output_directory_not_exist(monkeypatch, tmpdir):
    # テスト用の入力JSONファイルを作成
    input_data = {"query": ["AIの未来について教えてください。"]}
    input_file = tmpdir.join("sample.json")
    with open(input_file, "w", encoding='utf-8') as f:
        json.dump(input_data, f, ensure_ascii=False)

    # 環境変数を一時的に設定
    monkeypatch.setenv("INPUT_JSON_PATH", str(input_file))
    output_file = tmpdir.join("non_existent_dir/output.json")
    monkeypatch.setenv("OUTPUT_JSON_PATH", str(output_file))

    # main関数を実行してエラーが発生しないことを確認
    main(str(input_file), str(output_file))

    # 出力されたJSONファイルを読み込んで検証
    with open(output_file, "r", encoding='utf-8') as f:
        output_data = json.load(f)
    
    assert "answer" in output_data
    assert len(output_data["answer"]) == 1
    assert "messages" in output_data["answer"][0]
    assert isinstance(output_data["answer"][0]["messages"], str)
