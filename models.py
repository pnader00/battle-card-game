import random
from pygame import image, transform

class Card:
    values = range(0,13)
    suits = ["Spades", "Hearts", "Diamonds", "Clubs"]
    names = list(range(2, 11)) + ["Jack", "Queen", "King", "Ace"]
    scale = 0.15

    def __init__(self, value, suit) -> None:
        self.value = value
        self.suit = suit

    def __str__(self) -> str:
        return f'{self.__name()}_of_{self.suit}'
    
    def __repr__(self) -> str:
        return f'({self.__name()}, {repr(self._suit)})'

    def __name(self):
        return Card.names[Card.values.index(self._value)]
    
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        if value in Card.values:
            self._value = value
        else:
            raise ValueError(f"Value not in {Card.values}")
    @property
    def suit(self):
        return self._suit
    @suit.setter
    def suit(self, suit):
        if suit in Card.suits:
            self._suit = suit
        else:
            raise ValueError(f"Suit not in {Card.suits}")

    def __hash__(self):
            return hash(self.__repr__())

    def __gt__(self,  __o: object):
        return self.value > __o.value
    
    def __eq__(self, __o: object) -> bool:
        return self.value == __o.value

    def __lt__(self,  __o: object):
        return self.value < __o.value

class Deck:
    def __init__(self) -> None:
        self._deck = []

        for suit in Card.suits:
            for value in Card.values:
                self._deck.append(Card(value, suit))

    def lenght(self):
        return len(self._deck)

    def shuffle_deck(self):
        random.shuffle(self._deck)
    
    def deal(self):
        #deal first card from deck
        return self._deck.pop(0)

    def is_empty(self):
        return len(self._deck) == 0

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < len(self._deck):
            card = self._deck[self.n]
            self.n += 1
            return card
        else:
            raise StopIteration

class Player:
    id = 0
    def __init__(self, name: str) -> None:
        self.name = name
        self.hand = []
        self.pile = []
        self.id = Player.id
        Player.id += 1

    def __str__(self) -> str:
        return f'{self.name}, {self.hand_len()} cards'

    # def __repr__(self) -> str:
    #     return f"{self.name}"

    def add_card(self, card):
        self.hand.append(card)
    
    def play_card(self):
        #option for later reference, add card variable to function definition
        #self.hand.remove(card)
        if self.hand_len() > 0:
            self.pile.append(self.hand.pop(0))
            
    
    def print_hand(self):
        return repr(self.hand)

    def get_hand(self):
        return self.hand

    def hand_len(self):
        return len(self.hand)

    def is_empty(self):
        return len(self.hand) == 0

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < len(self.hand):
            card = self.hand[self.n]
            self.n += 1
            return card
        else:
            raise StopIteration

