import sys
import models
import os
import pygame as pg
from pygame.locals import *
from collections import OrderedDict

class App:
    scenes = []
    scene = None
    window = None
    focus = None

    def __init__(self, size=(640, 480)) -> None:
        pg.init()
        flags = 0 #RESIZABLE
        
        App.window = pg.display.set_mode(size, flags)
        self.running = True   

    def run(self):

        while self.running:

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == MOUSEBUTTONDOWN:
                    App.scene.do_event(event)
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        self.next_scene()
            
            App.scene.update()
            App.scene.draw()                      

        pg.quit()

    def next_scene(self, d=1):
        i = App.scenes.index(App.scene)
        n = len(App.scenes)
        i = (i+d) % n
        App.scene = App.scenes[i]
        App.scene.enter()

class Scene:
    """Createa new scene and initialize the node options"""
    options = {'id': 0,
                'bg': Color('darkgreen'), #backgroud color
                'caption': 'Pygame', #window caption
                'focus': None, #currently active node
                'keep': True
                }

    def __init__(self, remember=True, **options):
        App.scenes.append(self)
        App.scene=self
        self.nodes = []

        #Reset node options to default
        Node.reset_options()
        # update existing Scene options, without adding new ones
        if remember:
            for k in options:
                if k in Scene.options:
                    Scene.options[k] = options[k]
                else:
                    raise TypeError(f"'{k}' is an invalid keyword argument for Scene()")

        # Add/update instance options from class options
        self.__dict__.update(Scene.options)
        if not remember:
            self.__dict__.update(options)
        Scene.options['id'] += 1

        self.enter()

    def __str__(self) -> str:
        return 'Scene() {}'.format(self.id)

    def do_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            for node in self.nodes:
                if node.rect.collidepoint(event.pos):
                    self.focus = node
                    print(f'app scene focus: {self.focus.id}')
            if self.focus != None and self.focus.rect.collidepoint(event.pos):
                self.focus.do_event(event)
            
    def draw(self):
        App.window.fill(self.bg)
        for node in self.nodes:
            node.draw()
        
        pg.display.flip()
    
    def enter(self):
        pg.display.set_caption(self.caption)

    def update(self):
        pass

    def debug(self):
        """Print all scene/node options."""
        obj = self.focus if self.focus else self
        print('===', obj, '===')
        for k, v in obj.__dict__.items():
            print(k, '=', v)

class Node:
    """Create a nose object with automatic osition and inherited size"""
    #initial options for nodes
    options0 = {'pos': (20, 20),
                'size': (75, 100),
                'dir': (0, 1),
                'gap': (10, 10),
                
                'id' : 0,
                'keep': True,
                'file': '',
                'bg': None,
                'img': None,
                'visible': True}

    #current options dictionary for each node
    options = options0.copy()

    focus = Color('red'), 1
    outline = Color('black'), 1

    @classmethod
    def reset_options(cls):
        Node.options = cls.options0.copy()
    
    @staticmethod
    def increment_id():
        Node.options['id'] +=1
    
    def __init__(self, **options):
        self.set_options(Node, options)
        self.increment_id()

        self.calculate_pos(options)
        self.rect = Rect(*self.pos, *self.size)
        # self.rect.center = self.pos
        
        App.scene.nodes.append(self)

        self.create_img()
        self.color_img()
        if self.file != '':
            self.load_img()
  
    def set_options(self, cls, options):

        if 'keep' in options:
            Node.options['keep'] = options['keep']

        if Node.options['keep']:
            # update class options from instance option
            for key in options:
                if key in cls.options:
                    cls.options[key] = options[key]
                # else:
                #     raise TypeError(f'{key} is invalid argument for Node()')
        # update instance options from class options
        self.__dict__.update(cls.options)
        self.__dict__.update(options)

    def create_img(self):
        """Create surface and origina img0"""
        self.img = pg.Surface(self.rect.size, SRCALPHA)
        self.img0 = self.img.copy()
    
    def color_img(self):
        """Add background color to the image"""
        if self.bg == None:
            self.img.fill((0, 0, 0, 0))
        else:
            self.img.fill(self.bg)
        self.img0 = self.img.copy()

    def set_background(self, img):
        """Set background color or transparency."""
        if self.bg == None:
            img.fill((0, 0, 0, 0))
        else:
            img.fill(self.bg)

    def load_img(self):
        """Load image file"""
        module = sys.modules['__main__']
        path, name = os.path.split(module.__file__)
        path = os.path.join(path, self.file)

        img = pg.image.load(path)
        self.img0 = pg.Surface(img.get_size(), flags=SRCALPHA)
        self.set_background(self.img0)
        self.img0.blit(img, (0, 0))

        self.img = pg.transform.smoothscale(img, self.rect.size)

    def draw(self):
        App.window.blit(self.img, self.rect)

        if self == App.scene.focus:
            pg.draw.rect(App.window, Node.focus[0], self.rect, Node.focus[1])
        
        if self.rect.collidepoint(pg.mouse.get_pos()):
            pg.draw.rect(App.window, Node.outline[0], self.rect, Node.outline[1])

    def calculate_pos(self, options):
        """Calculate the next node position"""
        if self.id > 0 and 'pos' not in options:
            last = App.scene.nodes[-1].rect
            x = self.pos[0] + self.dir[0] * (last.size[0] + self.gap[0])
            y = self.pos[1] + self.dir[1] * (last.size[1] + self.gap[1])
            self.pos = x, y
            Node.options['pos'] = x, y

    def do_event(self, event):
        if event.type == KEYDOWN:
            pass 

class TextObj:
    """Create a text surface image"""
    options = {'fontname': None,
                'fontsize': 24,
                'fontcolor': Color('black'),

                'italic': False,
                'bold': False,
                'underline': False,
                
                'width': 150,
                'align': 0, # 0=left, 1=center, 2=right
                'bg': None,
                'x': 0
                }

    def __init__(self, text='Text', **options):
        """Create and render text object"""
        #update existing Text options, without adding new ones
        for k in options:
            if k in TextObj.options:
                TextObj.options[k] = options[k]
        
        self.__dict__.update(TextObj.options)

        self.text = text
        self.set_font()
        self.render_text()
    
    def set_font(self):
        """Set font and its properties"""
        self.font = pg.font.Font(self.fontname, self.fontsize)
        self.font.set_bold(self.bold)
        self.font.set_italic(self.italic)
        self.font.set_underline(self.underline)

    def render_text(self):
        """Render the text into an image."""
        img = self.font.render(self.text, True, self.fontcolor, self.bg)
        self.rect = img.get_rect()
        self.align_image(img)

    def align_image(self, img):
        w, h = self.font.size(self.text)
        w0 = self.width
        self.x = 0
        if w0 > 0:
            self.x = (0, (w0-w)//2, (w0-w))[self.align]
            self.img = pg.Surface((w0, h), flags=SRCALPHA)
            if self.bg != None:
                self.img.fill(self.bg)
            self.img.blit(img, (self.x, 0))
            self.rect.size = self.img.get_size()
        else:
            self.img = img

class Text(Node):
    """Create a text object horizontal and vertical alignement."""
    def __init__(self, text='Text', **options):
        super().__init__(**options)

        self.txt = TextObj(text, **options)
        self.rect.size = self.txt.rect.size
        self.img = self.txt.img

class Button(Node):
    """Create button object with command"""
    options={ 'border': 2,
              'bg': Color('darkgreen'),
              'size': (160, 40),
              'align': 1,
              'state': False
    }

    def __init__(self,text='Button', cmd='', **options):
        super().__init__(**options)
        self.set_options(Button, options)
        self.cmd = cmd
        self.label = TextObj(text, **options)
        self.render()
    
    def render(self):
        #  self.img.fill(SRCALPHA)
        self.label.render_text()
        w, h = self.rect.size
        self.label.rect.center = w//2, h//2
        self.img.blit(self.label.img, self.label.rect)

    def do_event(self, event):
        super().do_event(event)
        if event.type == MOUSEBUTTONDOWN:
            self.state = not self.state
            try:
                exec(self.cmd)
            except:
                print('cmd error')
            
            # if self.state:
            #     self.label.text = 'ON'
            # else:
            #     self.label.text = 'OFF'
            self.render()

class Battle(App):

    def __init__(self, size=(640, 480)) -> None:
        super().__init__(size)
        self.players = {}
        self.loosers = []
        self.active_player = None
        self.first_player = None
        self.turn_players = None

        self.deck = models.Deck()

        self.card_size = Node.options['size']
        self.deck_gaps = [(0, 0), (320,0), (320, 50)]
        self.deck_dirs = [(0, 0), (1, 0), (-1, 1)]
        self.pile_pos = [(100, 25), (-100, 25), (200, -25)]
        self.bg_color = Color('darkgreen')

        self.game_on = False
        self.is_battle = False
        self.end_turn = False
        self.show_winner = False
        
        self.turn = 1
        self.battle_turn = 0
        self.battle_size = 3

    def run(self):
        while self.running:

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == MOUSEBUTTONDOWN:
                    if self.end_turn:
                        self.play_turn()
                        self.end_turn = False
                    else:
                        App.scene.do_event(event)
                        if self.show_winner:
                            self.show_winner = False
                            self.loosers.clear()
                        
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        self.next_scene()

            self.update()
            self.draw()

            if self.game_on:        
                if not self.end_turn and self.full_table():
                    self.end_turn = True
                if self.is_winner():
                    self.game_over()
                    self.game_on = False
        pg.quit()        

    def update(self):
        App.scene.update()
        if self.game_on:
            self.update_piles()
            self.update_text()

    def draw(self):
        App.scene.draw()
    
    def new_game(self, players = 2):
        """initialize new game""" 
        self.players.clear()
        models.Player.id = 0
        
        for i in range(players):
            player = models.Player(f"Player {i}")
            self.players[player.id] = player
        
        print(self.players)

        self.active_player = self.players[0]
        self.turn_players = self.players
        self.game_on = True
        self.turn = 1

        self.deck.shuffle_deck()
        self.deal_cards()

        self.first_player = self.players[self.active_player.id]

        self.next_scene()
        self.scene.nodes.clear()
        Node.reset_options()

        self.add_buttons()

    def deal_cards(self, to_deal=52):
        while not self.deck.is_empty() and to_deal > 0:
            self.active_player.add_card(self.deck.deal())
            self.next_player()
            to_deal -= 1
    
    def add_buttons(self):
        """add deck buttons to scene"""
        players = len(self.players)

        for i in range(players):
            if i == 0:
                Button(file='cards_png/back.png',cmd='battle.play_card()', text='', pos=(80, 190))
            else:
                Button(file='cards_png/back.png',cmd='battle.play_card()', text='', gap=self.deck_gaps[i], dir=self.deck_dirs[i])

    def update_text(self):
        """add text nodes to scene"""
        for player in self.players.values():
            if player.id == 0:
                Text(text=f'{player}', pos=(20, 170), fontsize=24, width=200, align=1)
            elif player.id % 2 == 0:
                Text(text=f'{player}', gap=(200,130), dir=(-1,1))
            else:
                Text(text=f'{player}', gap=(200,0), dir=(1,0))
        

        Text(text=f'Round {self.turn}', pos=(270, 50), fontsize=36, width=110, align=1)

        gap = (-205, 25)
        dir = (1, 1)

        if self.show_winner:
            Text(text=f'{self.first_player.name} wins the Round!', gap=gap, dir=dir, fontsize=36, width=300, align=1)
        
        if self.is_battle and not self.full_table():
            Text(text=f'Battle!', gap=gap, dir=dir, fontsize=36, width=300, align=1)

        if self.full_table() and not self.show_winner:
            text='Click to check winner'
        elif self.show_winner or self.is_battle:
            text=f'{self.active_player.name} click on pile to play card'
            gap=(0,25)
            dir=(0,1)     
        else:
            text = f'{self.active_player.name} click on pile to play card'    
        
        Text(text=text, gap=gap, dir=dir, fontsize=24, width=300, align=1)

        if len(self.loosers) != 0:
            for looser in self.loosers:
                Text(text=f'{looser.name} lost', gap=gap, dir=dir, fontsize=36, width=300, align=1)

    def update_piles(self):
        '''update scene with each player's cards'''
        #remove all nodes except pile buttons
        self.scene.nodes = self.scene.nodes[:len(self.players)]
        
        for player in self.players.values():
            index = list(self.players.keys()).index(player.id)
            parent_pos = self.scene.nodes[index].pos
            
            #show every second card
            for n, card in enumerate(player.pile):
                if n % 2 == 0:
                    path = f'cards_png/{card.__str__()}.png'
                else:
                    path = 'cards_png/back.png'
            
                if n == 0:
                    pos = (parent_pos[0] + self.pile_pos[index][0], parent_pos[1] + self.pile_pos[index][1])
                    self.scene.nodes.append(Node(file=path, pos=pos, size=self.card_size))
                else:
                    self.scene.nodes.append(Node(file=path, gap=(0,-75), dir=(0,1), size=self.card_size))

    def play_card(self):
        if self.scene.focus.id == self.active_player.id:
            self.active_player.play_card()
            self.next_player()

    def play_turn(self):
        """check who wins the round/is there a battle"""
        turn_winners = self.get_winners()
        if len(turn_winners) == 1:
            self.clear_table(turn_winners)
            self.active_player = self.players[turn_winners[0]]
            self.first_player = self.players[turn_winners[0]]
            self.remove_loosers()
            self.turn_players = self.players
            self.show_winner = True
            self.is_battle = False
            self.battle_turn = 0
            self.turn += 1
        else:
            self.is_battle = True
            self.battle_turn += 1
            self.turn_players = OrderedDict((k, self.players[k]) for k in sorted(turn_winners))

    def get_winners(self):
        """returns list id of players with highest cards and list of cards played in round"""
        
        # in case of battle last card played by the player (drawn from last_pool) is used
        table = [(player.pile[-1], id) if len(player.pile) % 2 != 0 \
                else (player.pile[len(player.pile) - 1], id) \
                for id, player in self.turn_players.items()]
        table.sort(reverse=True)

        table_cards = [t[0] for t in table]
        #id of round winners
        winners_id = [table[i][1] for i, x in enumerate(table_cards) if x == table_cards[0]]
        return winners_id

    def clear_table(self, winners_id):
        """add card's to winner's deck"""
        for player in self.players.values():
            for card in player.pile:
                self.players[winners_id[0]].add_card(card)
            player.pile.clear()

    def remove_loosers(self):
        self.loosers = [player for player in self.players.values() if player.is_empty()]
        for looser in self.loosers:
            del self.players[looser.id]

    def next_player(self, d=1):
        key_list = list(self.turn_players.keys())
        i = key_list.index(self.active_player.id)
        n = len(self.turn_players)
        i = (i+d) % n
        self.active_player = self.turn_players[key_list[i]]

    def is_winner(self):
        return len(self.players) == 1

    def full_table(self):
        return self.active_player.id == self.first_player.id and self.is_full_pile() 

    def is_full_pile(self):
        """check if all players played their cards"""
        if self.is_battle:
            for player in self.turn_players.values():
                if len(player.pile) % (1 + self.battle_turn * 2) == 0:
                    return True
        else:
            return len(self.active_player.pile) != 0
        return False

    def get_game_winner(self):
        return list(self.players.values())[0].name    

    def game_over(self):
        """generate game over scene with winners name"""
        Scene(caption='Game over')
        Text(text=f'{battle.get_game_winner()} wins the Game!', pos=(120, 120), fontsize=48, width=400, align=1)
        Button(text='Main Menu', cmd='battle.next_scene(d=2)', gap=(0, 40), size=(400,40))
        Button(text='Quit', cmd='pg.quit()', gap=(0, 20))

    def debug(self):
        """helper function show state of the game"""
        print(f"active: {self.active_player.id}")
        # print(f'focus: {self.scene.focus.id}')
        print(f"turn: {self.turn}")
        print(f"is battle: {self.is_battle}")
        print(f"end turn: {self.end_turn}")

    def test_cards(self):
        """helper function genarate predefined decks"""
        cards1 = [models.Card(4, 'Spades')
                #   , models.Card(6, 'Hearts'),
                #     models.Card(8, 'Spades'), models.Card(3, 'Spades'),models.Card(9, 'Spades')            
             ]
        cards2 = [models.Card(6, 'Diamonds')
                #   , models.Card(6, 'Clubs'),
                #     models.Card(8, 'Clubs'), models.Card(4, 'Clubs'),models.Card(12, 'Spades')            
             ]
        
        cards3 = [models.Card(8, 'Diamonds')
                #   , models.Card(6, 'Clubs'),
                #     models.Card(8, 'Clubs'), models.Card(4, 'Clubs'),models.Card(12, 'Spades'), models.Card(0, 'Spades')
                     ]
        print('cards')
        for c in cards1:
            self.players[0].add_card(c)
        
        for c in cards2:
            self.players[1].add_card(c)
        
        for c in cards3:
            self.players[2].add_card(c)
        
        for p in self.players.values():
            print(p.print_hand())

def test():
    size = 640, 480
    pg.init()
    window = pg.display.set_mode(size)

    my_font = pg.font.SysFont(None, 50)
    text_surface = my_font.render("Hello world!", True, (255, 0, 0))
    window.blit(text_surface, (10, 10))

    text = TextObj(bg=Color('black'))

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
    
        window.fill(Color('darkgreen'))
        window.blit(text_surface, (10, 10))
        window.blit(text.img, (100, 100))

        pg.display.flip()

if __name__ == '__main__':

    battle = Battle()

    # w, h = Battle.window.get_size()
    Scene(caption='Main Table')

    Scene(caption='Main Menu')
    Text(text='Card Battle Main Menu:', pos=(120, 120), fontsize=48, width=400, align=1)
    Button(text='New Game 2 players', cmd='battle.new_game()', gap=(0, 40), size=(400,40))
    Button(text='New Game 3 players', cmd='battle.new_game(players=3)', gap=(0, 20))
    Button(text='Quit', cmd='pg.quit()')
    
    battle.run()
