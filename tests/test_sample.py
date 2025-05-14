from src.sample import add_number

def test_add_numbers_1():
    # 正の整数同士の足し算
    assert add_number(1, 2) == 3

def test_add_numbers_2():
    # 正の整数と負の整数の足し算
    assert add_number(-1, 1) == 0

def test_add_numbers_3():
    # ゼロ同士の足し算
    assert add_number(0, 0) == 0

def test_add_numbers_4():
    # 負の整数同士の足し算
    assert add_number(-1, -1) == -2

def test_add_numbers_5():
    # 大きな正の整数同士の足し算
    assert add_number(100, 200) == 300
