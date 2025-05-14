from sample import add_number

def test_add_numbers_1():
    print("正の整数同士の足し算")
    assert add_number(1, 2) == 3

def test_add_numbers_2():
    print("正の整数と負の整数の足し算")
    assert add_number(-1, 1) == 0

def test_add_numbers_3():
    print("ゼロ同士の足し算")
    assert add_number(0, 0) == 0

def test_add_numbers_4():
    print("負の整数同士の足し算")
    assert add_number(-1, -1) == -2

def test_add_numbers_5():
    print("大きな正の整数同士の足し算")
    assert add_number(100, 200) == 300

if __name__ == "__main__":
    test_add_numbers_1()
    test_add_numbers_2()
    test_add_numbers_3()
    test_add_numbers_4()
    test_add_numbers_5()
    print("全てのテストが成功しました。")