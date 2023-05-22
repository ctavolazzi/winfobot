from abc import ABC, abstractmethod

class Search(ABC):
    @abstractmethod
    def search(self, target, term):
        pass

class AttributeSearch(Search):
    def search(self, target, term):
        attribute, value = term

        if not attribute or not value:
            return None

        for item in target:
            if hasattr(item, attribute) and getattr(item, attribute) == value:
                return item

        return None