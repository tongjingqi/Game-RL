from random import *

def form_options(options: list) -> str:
    return 'Options:\n' + '\n'.join(f'{i+1}: {options[i]}' for i in range(len(options)))

def gen_consecutive_int_options(x, total=8) -> str:
    l_off = randint(0, min(x, total-1))
    return list(range(x-l_off, x-l_off+total))

def gen_consecutive_five_multiple_options(x, total=8) -> str:
    assert x % 5 == 0, 'x should be a multiple of 5'
    x //= 5
    base_options = gen_consecutive_int_options(x, total=total)
    return [i*5 for i in base_options]

def gen_consecutive_ten_multiple_options(x, total=8) -> str:
    assert x % 10 == 0, 'x should be a multiple of 10'
    x //= 10
    base_options = gen_consecutive_int_options(x, total=total)
    return [i*10 for i in base_options]

if __name__ == '__main__':
    print(gen_consecutive_ten_multiple_options(100, total=8))