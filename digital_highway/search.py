from abc import ABC, abstractmethod
from typing import Any

class Search(ABC):
    @abstractmethod
    def search(self, target, term):
        pass

class EqualitySearch(Search):
    def search(self, target, term):
        return [obj for obj in target if any(getattr(obj, attr, None) == term for attr in vars(obj))]

class ContainsSearch(Search):
    def search(self, target, term):
        return [obj for obj in target if any(term in str(getattr(obj, attr, '')) for attr in vars(obj))]

class SearchManager:
    def __init__(self):
        self.strategies = {
            str: ContainsSearch(),
            Bot: EqualitySearch(),
        }

    def search(self, target, term):
        strategy = self.strategies.get(type(term))
        if strategy:
            return strategy.search(target, term)
        else:
            raise ValueError(f"No search strategy found for type: {type(term)}")
