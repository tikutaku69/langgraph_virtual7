from use_dataset import evaluate_dataset

def test_add_numbers_1():
    experiment_results = evaluate_dataset()
    print(experiment_results)

if __name__ == "__main__":
    test_add_numbers_1()
    print("全てのテストが成功しました。")