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
        # nie potrzeba wgrywac obrazków bo robi to klasa node
        # self.image = image.load('cards_png/' + self.__str__() + ".png")
        # self.image = transform.scale(self.image, (self.image.get_width() * Card.scale, self.image.get_height() * Card.scale))

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
        self._cards = []
        self.id = Player.id
        Player.id += 1

    def __str__(self) -> str:
        return f'Name: {self.name}, {self.how_many_cards()} cards'

    def __repr__(self) -> str:
        return f"{self.name}"

    def add_card(self, card):
        self._cards.append(card)
    
    def play_card(self):
        #option for later reference, add card variable to function definition
        #self._cards.remove(card)
        return self._cards.pop(0)
    
    def print_hand(self):
        return repr(self._cards)

    def get_hand(self):
        return self._cards

    def how_many_cards(self):
        return len(self._cards)

    def is_empty(self):
        return len(self._cards) == 0

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < len(self._cards):
            card = self._cards[self.n]
            self.n += 1
            return card
        else:
            raise StopIteration

class Battle:
    def __init__(self, hand_size = 26) -> None:
        self.end_game=False
        self.deck = Deck()
        self.pool = []
        self.last_pool = []
        self.hand_size = hand_size
        self.main_loop()
    
    def help(self):
        print("commands:")
        print("0 - exit")
        print("1 - new game")
        print("2 - next turn")

    def new_game(self, players = 2):
        
        self.players = {p: Player(f"Player {p}") for p in range(players)}
        self.deck.shuffle_deck()

        self.deal_cards()

        return self

    def deal_cards(self):
        keys = list(self.players.keys())
        id_pos = 0
        max_id_pos = len(self.players) - 1
        hand_size = self.hand_size * len(self.players)

        while not self.deck.is_empty() and hand_size > 0:
            if id_pos > max_id_pos:
                id_pos = 0
            self.players[keys[id_pos]].add_card(self.deck.deal())
            id_pos += 1
            hand_size -= 1

    def get_winners_and_cards (self, players):
        #returns list id of players with highest cards and list of cards played in round
        
        # in case of battle last card played by the player (drawn from last_pool) is used
        table = [(player.play_card(), id) if not player.is_empty() else (self.last_pool[0], id)\
                for id, player in players.items()]
        table.sort(reverse=True)

        print(f"table: {table}")
        table_cards = [t[0] for t in table]
        #id of round winners
        winners_id = [table[i][1] for i, x in enumerate(table_cards) if x == table_cards[0]]
        return winners_id, table_cards        

    def play_turn(self, players):
        #play one card for each player and check who is the winner
        winners_id, sub_pool = self.get_winners_and_cards(players)
        self.pool += sub_pool
        
        #in case of battle last_pool is used to draw card for player which has no cards on hand
        self.last_pool.clear()
        self.last_pool += sub_pool
        
        # print(f"pool: {self.pool}")
        # print(f"last pool: {self.last_pool}")
        
        #when there is only one winner finish turn and add cards to winner's hand
        if len(winners_id) == 1:
            #remove duplicate cards from pool
            self.pool = list(set(self.pool))
            print(f"pool to add: {self.pool}")
            
            for card in self.pool:
                self.players[winners_id[0]].add_card(card)
            
            self.pool.clear()
            self.last_pool.clear()
            return print(f"Winner: {self.players[winners_id[0]]}")

        #in case of battle make list with players involved
        new_players = dict((k, self.players[k]) for k in winners_id)
        
        #add one card from each player to the pool
        for player in new_players.values():
            if not player.is_empty():
                self.pool.append(player.play_card())

        print(f"new players: {new_players}")
        #play next round to see who is the battle winner
        self.play_turn(new_players)

    def remove_loosers(self):
        loosers = [id for id, player in self.players.items() if player.is_empty()]
        for looser in loosers:
            print(f"{self.players[looser].name} lost!")
            del self.players[looser]
           
    def is_winner(self):
        return len(self.players) == 1
          
    def show_players(self):
        for p in self.players.values():
            print(p)
        
    def main_loop(self):

        while True:
            self.help()
            command = int(input("command: "))

            if command == 0:
                print("exit")
                break
            if command == 1:
                self.new_game()
                self.show_players()

            if command == 2:
                print(f"Players:")
                self.show_players()
                self.play_turn(self.players)
                self.remove_loosers()
                self.end_game = self.is_winner()
                
                if self.end_game:
                    print(f"Winner is:")
                    self.show_players()
                
