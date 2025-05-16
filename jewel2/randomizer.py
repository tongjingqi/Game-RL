# randomizer.py
import random
from abc import ABC, abstractmethod

class Randomizer(ABC):
    @abstractmethod
    def next_chess(self) -> str:
        pass

class NormalRandom(Randomizer):
    alphabet = ['A', 'B', 'C', 'D', 'E']

    def next_chess(self) -> str:
        return random.choice(self.alphabet)

class SpecialRandom(Randomizer):
    NORMAL_ELEMENTS = ['A', 'B', 'C', 'D', 'E']
    SPECIAL_ELEMENTS = ['a', 'b', 'c', 'd', 'e', '+', '|']
    NORMAL_PROBABILITY = 0.95

    def next_chess(self) -> str:
        # 95% probability of generating a normal element; 5% probability of generating a special element
        if random.random() < self.NORMAL_PROBABILITY:
            return random.choice(self.NORMAL_ELEMENTS)
        else:
            return random.choice(self.SPECIAL_ELEMENTS)
