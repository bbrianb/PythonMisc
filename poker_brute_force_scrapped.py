from random import shuffle
from itertools import combinations
from enum import Enum, auto
from time import perf_counter

class Rank:
    def __init__(self, rank):
        self.rankName: str
        self.rankNumber: int

        if isinstance(rank, str):
            self.rankName = rank
            number_dict = {'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
            if self.rankName in number_dict:
                self.rankNumber = number_dict[self.rankName]
            else:
                self.rankNumber = int(self.rankName)
        else:
            self.rankNumber = rank
            name_dict = {10: 'T', 11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
            if self.rankNumber in name_dict:
                self.rankName = name_dict[self.rankNumber]
            else:
                self.rankName = str(self.rankNumber)

    def __repr__(self) -> str:
        return self.rankName

    def __eq__(self, other):
        if isinstance(other, Rank):
            return self.rankName == other.rankName
        elif isinstance(other, int):
            return self.rankNumber == other
        else:
            return False

    def __add__(self, other):
        return self.rankNumber + other

    def __hash__(self):
        return hash(self.rankName)

class Card:
    def __init__(self, rank, suit: str):
        self.suit: str = suit
        self.rank: Rank

        if isinstance(rank, Rank):
            self.rank = rank
        else:
            self.rank = Rank(rank)

    def __repr__(self) -> str:
        return str(self.rank) + self.suit

    def __eq__(self, other):
        if isinstance(other, Rank) or isinstance(other, int):
            return self.rank == other
        elif isinstance(other, str):
            return self.suit == other
        elif isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        else:
            return False

    def __add__(self, other):
        return self.rank + other

    def __hash__(self):
        return hash((self.rank, self.suit))

class Player:
    def __init__(self):
        self.cards = []

        self.tempAvailableCards: list[Card]
        self.tempHandStrength: HandStrength
        self.tempHighCardInfo: list[Rank]

    def __repr__(self) -> str:
        output = ''
        for card in self.cards:
            output += str(card) + " "
        return output[:-1]

    def __add__(self, other):
        return self.cards + list(other)

class HandStrength(Enum):
    STRAIGHT_FLUSH = auto()
    ROYAL_FLUSH = auto()

class Deck:
    def __init__(self):
        self.cards = []
        self.suits = 's', 'h', 'c', 'd'
        self.ranks = []

        ranks = '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'
        for rank in ranks:
            self.ranks.append(Rank(rank))

        for suit in self.suits:
            for rank in self.ranks:
                self.cards.append(Card(rank, suit))

    def shuffle_deck(self) -> None:
        shuffle(self.cards)

    def deal(self, player: Player = None, rank: str = None, suit_wanted: str = None):
        if rank and suit_wanted:
            rank_wanted = Rank(rank)
            for i, card in enumerate(self.cards):
                if card == rank_wanted and card == suit_wanted:
                    # noinspection PyUnusedLocal
                    dealt_card = self.cards.pop(i)
                    break
        else:
            dealt_card = self.cards.pop()

        if player:
            player.cards.append(dealt_card)
            return None
        else:
            return dealt_card

    def __repr__(self) -> str:
        output = ''
        for card in self.cards:
            output += str(card) + " "
        return output[:-1]

    def __len__(self) -> int: return len(self.cards)

def prep_players(current_board, players: list[Player]):
    to_be_dealt = 5 - len(current_board)

    for current_player in players:
        current_player.availableCards = current_player + current_board
        current_player.cardsNeeded = {}

    for suit in Deck().suits:
        for low_end in range(10, 0, -1):
            original_straight = [Card(i, suit) for i in range(low_end, low_end + 5)]

            for current_player in players:
                potential_straight = original_straight.copy()

                for card in current_player.availableCards:
                    if card in potential_straight:
                        potential_straight.remove(card)


                if len(potential_straight) < 5 and len(potential_straight) <= to_be_dealt:
                    current_player.cardsNeeded[tuple(potential_straight)] = [None, original_straight[-1].rank]

                    if original_straight[0] == 10:
                        current_player.cardsNeeded[tuple(potential_straight)][0] = HandStrength.ROYAL_FLUSH
                    else:
                        current_player.cardsNeeded[tuple(potential_straight)][0] = HandStrength.STRAIGHT_FLUSH

    for current_player in players:
        print(current_player.cardsNeeded)



def get_hand_strengths(rest_of_board: list[Card], players: list[Player]) -> None:
    for current_player in players:
        current_player.tempHandStrength = None

    hands_made = 0
    player_count = len(players)

def main():
    deck = Deck()

    print(deck)

    deck.shuffle_deck()

    player1, player2 = Player(), Player()
    players = [player1, player2]

    cheating = True
    if cheating:
        deck.deal(player1, 'T', 's')
        deck.deal(player1, 'J', 's')
        deck.deal(player2, 'T', 'c')
        deck.deal(player2, 'J', 'c')
    else:
        for _ in range(2):
            for player in players:
                deck.deal(player)

    print(player1, player2)

    current_board = []

    rest_of_boards = []
    for rest_of_board in combinations(deck.cards, 5):
        rest_of_boards.append(rest_of_board)

    prep_players(current_board, players)

    for rest_of_board in rest_of_boards:
        start = perf_counter()
        get_hand_strengths(list(rest_of_board), players)
        stop = perf_counter()
        print(stop - start)

if __name__ == '__main__':
    main()