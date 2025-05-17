from typing import Literal

def form_addition_formula(nums: list) -> str:
    if len(nums) == 1:
        return str(nums[0])
    return ' + '.join(str(n) for n in nums) + ' = ' + str(sum(nums))

def enumerate_items(items: list, conj: Literal['and', 'or']) -> str:
    items = [str(item) for item in items]
    if len(items) == 1:
        return items[0]
    return ', '.join(items[:-1]) + f' {conj} ' + items[-1]
