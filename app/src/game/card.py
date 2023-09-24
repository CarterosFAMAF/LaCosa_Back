from abc import ABC, abstractmethod

class Card(ABC):
    type: str
    
    @abstractmethod
    def play_card(self):
        pass
    
class Lanzallamas(Card):

    def __init__(self) -> None:
        self.type = "Lanzallamas"
        
    def play_card(self):
        pass
