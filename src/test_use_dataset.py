from use_dataset import evaluate_dataset

def test_add_numbers_1():
    scores = evaluate_dataset()

    assert len(scores) > 0, "スコアが空のリストです"
    border_score = 95
    average_score = round(sum(scores) / len(scores), 1)
    assert average_score >= border_score, f"平均点が{border_score}点未満です。現在の平均点: {average_score:.2f}"

if __name__ == "__main__":
    test_add_numbers_1()
    print("全てのテストが成功しました。")