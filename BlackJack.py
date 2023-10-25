import random

def show_card(card):
    # img = cv2.imread(card.path(), cv2.IMREAD_ANYCOLOR)
    # RGB_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # fig = plt.figure()
    # axs = plt.axes()
    # axs.imshow(RGB_img)
    print(card.face(), card.suit())
    
def ask_player():
    return input("What will you like to do? ")

def begining_stake(num_players):
    print("Each player should input their bet. ")
    round_bet = []
    for i in range(num_players):
        not_move_on = True
        while not_move_on:
            try:
                bet = int(input(f"Player {i+1} "))
                not_move_on = False
            except:
                print("Invalid bet")
        round_bet.append(bet)
    return round_bet

class Hand:
    def __init__(self, stake):
        self._storage = []
        self._open = True
        self._stake = stake
        self._surrendered = False
        self._insured = False

    def add_card(self, card):
        if isinstance(card, Card):
            self._storage.append(card)
        return card

    def is_open(self):
        return self._open

    def close(self):
        self._open = False

    def __len__(self):
        return len(self._storage)

    def count(self):
        total = 0
        for card in self._storage:
            total += card._value
        return total

    def first(self):
        return self._storage[0]

    def can_split(self):
        if self._storage[0]._value == self._storage[1]._value:
            return True
        return False

    def pop(self):
        return self._storage.pop()

    def has_surrendered(self):
        return self._surrendered

    def surrrender(self):
        self._surrendered = True

    def is_insured(self):
        return self._insured

    def insure(self):
        self._insured = True

    def stake(self):
        return self._stake

    def add_stake(self, stake):
        self._stake += stake

    def __iter__(self):
        for card in self._storage:
            yield card

            
class Player:
    def __init__(self, bank):
        self._bank = bank
        self._hands = []

    def payout(self, amount):
        self._bank += amount

    def bet(self, stake):
        if self._bank > stake and stake >= 25:
            self._bank -= stake
            return stake
        print("Invalid Bet")
        raise ValueError

    def check_open(self):
        for hand in self._hands:
            if hand.is_open():
                return True
        return False

    def bank(self):
        return self._bank

    def __len__(self):
        return len(self._hands)

    def pop(self, j=None):
        if j == None:
            return self._hands.pop()
        return self._hands.pop(j)

    def add_hand(self, hand):
        self._hands.append(hand)

    def one_hand(self):
        return self._hands[0]

    def __iter__(self):
        for hand in self._hands:
            yield hand

    def initialise_hand(self):
        self._hands = []

    def hand_index(self, hand):
        return (self._hands.index(hand))

    def hand_insert(self, position, hand):
        self._hands.insert(position, hand)

class Table:
    _START_AMOUNT = 10000

    def __init__(self, num_players, num_deck=6):
        self._dealer = Dealer(Stack(num_deck))
        self._players = [Player(Table._START_AMOUNT) for num in range(num_players)]
        self._dict = {"s1" : self.stand,
                 "s2": self.split,
                 "s3": self.surrender,
                 "h": self.hit,
                 "d": self.double_down,
                 "i": self.insurance
                 }
        

    def begin_round(self):
        bets = begining_stake(len(self._players))
        self._dealer.hand = Hand(None)
        for i in range(len(self._players)):
            self._players[i].add_hand(Hand(self._players[i].bet(bets[i])))
            self._players[i].one_hand().add_card(self._dealer.deal_card())
            self._players[i].one_hand().add_card(self._dealer.deal_card())
        self._dealer.hand.add_card(self._dealer.deal_card())
        self._dealer.hand.add_card(self._dealer.deal_card())
        print("Dealer")
        show_card(self._dealer.hand.first())
        for i in range(len(self._players)):
            print(f"Player {i+1}")
            print(f"Bank: {self._players[i].bank()}")
            for card in iter(self._players[i].one_hand()):
                show_card(card)
                
            

    def go_round(self):
        while self.check_round_open():
            for player in self._players:
                if player.check_open():
                    print(f"Player {self._players.index(player) + 1}")
                    for hand in iter(player):
                        if hand.is_open():
                            for card in iter(hand):
                                show_card(card)
                            self.player_move(player, hand)
                            for card in iter(hand):
                                show_card(card)

        print("Dealer")
        for card in iter(self._dealer.hand):
            show_card(card)
        while self._dealer.hand.count() < 17:
            show_card(self._dealer.hand.add_card(self._dealer.deal_card()))
        for player in self._players:
            print(f"Player {self._players.index(player) + 1}")
            for hand in iter(player):
                print("Next Hand")
                for card in iter(hand):
                    show_card(card)
                if hand.count() > 21:
                    print("Burst")
                elif hand.has_surrendered():
                    player.payout(hand.stake())
                elif hand.is_insured():
                    if (self._dealer.hand.count() == 21) and (len(self._dealer.hand) == 2):
                        player.payout(hand.stake()*3)   
                elif (hand.count() == 21) and (len(hand) == 2) and ((self._dealer.hand.count() != 21) or len(self._dealer.hand) != 2) and (len(player) == 1):
                    print("BlackJack!!!")
                    player.payout(int(hand.stake()*2.5))
                else:
                    if self._dealer.hand.count() > 21:
                        player.payout(hand.stake()*2)
                    elif hand.count() > self._dealer.hand.count():
                        player.payout(hand.stake()*2)
                    elif hand.count() == self._dealer.hand.count():
                        player.payout(hand.stake())
        for player in self._players:
            print(f"Player {self._players.index(player) + 1}")
            print(player.bank())
            player.initialise_hand()
        self._dealer.hand = None                 

    def player_move(self, player, hand):
        answer = ask_player().lower()
        try:
            self._dict[answer](player, hand)
        except KeyError:
            print("That wasn't a valid option")
            self.player_move(player, hand)
        except ValueError:
            print("Try again")
            self.player_move(player, hand)
   
    def check_round_open(self):
        for player in self._players:
            if player.check_open():
                return True
        return False
    
    def stand(self, player, hand):
        hand.close()

    def hit(self, player, hand):
        hand.add_card(self._dealer.deal_card())
        if hand.count() > 20:
            hand.close()          

    def double_down(self, player, hand):
        hand.add_stake(player.bet(hand.stake()))
        hand.add_card(self._dealer.deal_card())
        hand.close()        

    def surrender(self, player, hand):
        hand.add_stake(-int(hand.stake * 0.5))
        hand.surrender()
        hand.close()

    def insurance(self, player, hand):
        if self._dealer.hand.first().face() != "Ace":
            print("Insurance is only offered when the dealer has an Ace")
            raise ValueError
        ransom = player.bet(int(hand.stake *0.5))    
        hand.insure()
        hand.close()

    def split(self, player, hand):
        if len(hand) == 0:
            print("Can only split hand if it contains 2 cards")
            raise ValueError
        if not hand.can_split():
            print("Both cards need to have equal value")
            raise ValueError
        hand_index = player.hand_index(hand)
        new_hand = Hand(player.bet(hand.stake()))
        first_card = hand.pop()
        new_hand.add_card(first_card)    
        newer_hand = Hand(hand.stake())
        newer_hand.add_card(hand.pop())
        player.hand_insert(hand_index, new_hand)
        player.hand_insert(hand_index, newer_hand)
        player.pop(hand_index + 2)
        if first_card.face() == "Ace":      
            self.hit(player, new_hand)
            self.hit(player, newer_hand)
            print("New hand")
            for card in iter(new_hand):
                show_card(card)
            print("New hand")
            for card in iter(newer_hand):
                show_card(card)
            new_hand.close()
            newer_hand.close()
        else:
            self.player_move(player, new_hand)
            for card in iter(new_hand):
                show_card(card)
            self.player_move(player, newer_hand)
            for card in iter(newer_hand):
                show_card(card)

class Card:
    def __init__(self, suit, face, value):
        self._suit = suit
        self._face = face
        self._value = value
        self._path = "C:/Users/USER/Desktop/Cards/" + suit + "/" + face + ".png"

    def face(self):
        return self._face

    def path(self):
        return self._path

    def suit(self):
        return self._suit
        

class Dealer:
    def __init__(self, stack):
        self._stack = stack
        self.hand = None

    def deal_card(self):
        if len(self._stack) == 0:
            self._stack.add_deck(2)
        return self._stack.remove_card()

class Stack:
    def __init__(self, num_deck):
        self._storage = []
        self.add_deck(num_deck)

    def __len__(self):
        return len(self._storage)

    def add_deck(self, num_deck):
        for i in range(num_deck):
            for suit in ["spade", "club", "heart", "diamond"]:
                self._storage.append(Card(suit, "Ace", MutableInt(11)))
                for j in range(2, 11):
                    self._storage.append(Card(suit, str(j), j))
                for rank in ["J", "Q", "K"]:
                    self._storage.append(Card(suit, rank, 10))
        random.shuffle(self._storage)

    def remove_card(self):
        return self._storage.pop()

    def path(self):
        return self._path

class MutableInt:
    GAP = 10
    BOUND = 21
    
    def __init__(self, value, redo=1):
        self._value = value
        self._redo = redo

    def __add__(self, other):
        if isinstance(other, int):
            new_mutable_int = MutableInt(self._value + other, self._redo)
        elif isinstance(other, MutableInt):
            new_mutable_int = MutableInt(self._value + other._value, self._redo + other._redo)
        else:
            raise ValueError
        while new_mutable_int._value > MutableInt.BOUND and new_mutable_int._redo > 0:
            new_mutable_int._value -= MutableInt.GAP
            new_mutable_int._redo -= 1
        if new_mutable_int._redo == 0:
            return new_mutable_int._value
        return new_mutable_int

    def __radd__(self, other):
        if isinstance(other, int):
            new_mutable_int = MutableInt(self._value + other, self._redo)
        elif isinstance(other, MutableInt):
            new_mutable_int = MutableInt(self._value + other._value, self._redo + other._redo)
        else:
            raise ValueError
        while new_mutable_int._value > MutableInt.BOUND and new_mutable_int._redo > 0:
            new_mutable_int._value -= MutableInt.GAP
            new_mutable_int._redo -= 1
        if new_mutable_int._redo == 0:
            return new_mutable_int._value
        return new_mutable_int

    def value(self):
        return self._value
 
    def __eq__(self, other):
        if isinstance(other, int):
            if other > MutableInt.BOUND:
                raise ValueError
            return (self._value == other)
        elif isinstance(other, MutableInt):
            return (self._value == other._value)
        else:
            raise ValueError

    def __ne__(self, other):
        return not (self == other)

    def __gt__(self, other):
        if isinstance(other, int):
            if other > MutableInt.BOUND:
                raise ValueError
            return (self._value > other)
        elif isinstance(other, MutableInt):
            return (self._value > other._value)
        else:
            raise ValueError

    def __lt__(self, other):
        if isinstance(other, int):
            if other > MutableInt.BOUND:
                raise ValueError
            return (self._value < other)
        elif isinstance(other, MutableInt):
            return (self._value < other._value)
        else:
            raise ValueError


num_players = int(input("How many players are in? "))
table = Table(num_players)
while True:
    table.begin_round()
    table.go_round()
    stop = input("Do you want to end now? Enter Y to quit and N to continue ").lower()
    if stop == "y":
        break
    