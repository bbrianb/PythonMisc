from random import shuffle
from itertools import combinations
from enum import Enum, auto

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
        else:
            return False

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
        if isinstance(other, Rank):
            return self.rank == other
        elif isinstance(other, str):
            return self.suit == other
        elif isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        else:
            return False

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

def get_hand_strength(board: list[Card], players: list[Player]) -> None:
    print(board)

    for current_player in players:
        current_player.tempAvailableCards = current_player + board
        current_player.tempHandStrength = None

    hands_made = 0
    player_count = len(players)

    for suit in Deck().suits:
        for low_end in range(10, 0, -1):
            current_straight = [Card(i, suit) for i in range(low_end, low_end + 5)]

            for current_player in players:
                potential_straight = current_straight.copy()

                cards_found = 0
                for card in current_player.tempAvailableCards:
                    if card in potential_straight:
                        cards_found += 1

                    if cards_found == 5:
                        if low_end == 10:
                            current_player.tempHandStrength = HandStrength.ROYAL_FLUSH
                        else:
                            current_player.tempHandStrength = HandStrength.STRAIGHT_FLUSH

                        current_player.tempHighCardInfo = [Rank(low_end+4)]

                        hands_made += 1

    if hands_made < player_count:
        # quads
        pass

def main():
    deck = Deck()

    print(deck)

    deck.shuffle_deck()

    player1, player2 = Player(), Player()
    players = [player1, player2]

    cheating = True
    if cheating:
        deck.deal(player1, 'T', 's')
        deck.deal(player1, 'T', 'h')
        deck.deal(player2, 'T', 'c')
        deck.deal(player2, 'T', 'd')
    else:
        for _ in range(2):
            for player in players:
                deck.deal(player)

    print(player1, player2)

    current_board = []

    rest_of_boards = []
    for rest_of_board in combinations(deck.cards, 5):
        rest_of_boards.append(rest_of_board)

    for rest_of_board in rest_of_boards[:1]:
        get_hand_strength(current_board + list(rest_of_board), players)

if __name__ == '__main__':
    main()