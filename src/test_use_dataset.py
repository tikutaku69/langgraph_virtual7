from use_dataset import evaluate_dataset

def test_add_numbers_1():
    scores = evaluate_dataset()
    print(scores)

if __name__ == "__main__":
    test_add_numbers_1()
    print("全てのテストが成功しました。")