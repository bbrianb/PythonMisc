import random
import math


class Card:
    def __init__(self, rank: str, suit: str):
        self.rank: Rank = Rank(rank)
        self.suit: str = suit

    def __repr__(self):
        return str(self.rank) + self.suit

    def __eq__(self, other):
        if isinstance(other, Rank):
            return self.rank == other
        elif isinstance(other, str):
            return self.suit == other
        else:
            return False

    def __ge__(self, other):
        return self.rank >= other

class Rank:
    def __init__(self, rank: str):
        self.rankName = rank

        rank_dict = {'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        if self.rankName in rank_dict:
            self.rankNumber = rank_dict[self.rankName]
        else:
            self.rankNumber = int(self.rankName)

    def __repr__(self):
        return self.rankName

    def __eq__(self, other):
        if isinstance(other, Rank):
            return self.rankNumber == other.rankNumber
        else:
            return False

    def __ge__(self, other):
        return self.rankNumber >= other

    def __hash__(self):
        return hash(self.rankName)

class Deck:
    def __init__(self):
        self.cards = []

        suits = 's', 'h', 'c', 'd'
        ranks = '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(rank, suit))

    def __repr__(self):
        output = ''
        for card in self.cards:
            output += str(card) + " "
        return output

    def __len__(self):
        return len(self.cards)

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, rank: str = None, suit: str = None):
        if rank and suit:
            rank_wanted = Rank(rank)
            for i, card in enumerate(self.cards):
                if card == rank_wanted and card == suit:
                    self.cards.pop(i)
                    return card
        else:
            return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []
        self.cardsBySuit = {'s': [], 'h': [], 'c': [], 'd': []}
        self.cardsByRank = {}
        self.equity = 0

    def new_cards(self, new_cards):
        for card in new_cards:
            self.cards.append(card)
            if card.suit not in self.cardsBySuit:
                self.cardsBySuit[card.suit] = [card.rank]
            else:
                self.cardsBySuit[card.suit].append(card.rank)

            if str(card.rank) not in self.cardsByRank:
                self.cardsByRank[str(card.rank)] = [card.suit]
            else:
                self.cardsByRank[str(card.rank)].append(card.suit)

    def __len__(self):
        return len(self.cards)

    def __repr__(self) -> str:
        output = ''
        for card in self.cards:
            output += str(card) + ' '
        return output[:-1]

    def __format__(self, format_spec):
        return f'{f'{str(self)}':{format_spec}}'


def equity(hands, deck):
    to_be_dealt = 7 - len(hands[0])
    combinations = {hand: 0 for hand in hands}

    # royal flush
    count = {'s': {}, 'h': {}, 'c': {}, 'd': {}}
    for hand in hands:
        for card in hand.cards:
            if card >= 10:
                if hand in count[card.suit]:
                    count[card.suit][hand] += 1
                else:
                    count[card.suit][hand] = 1

    for suit in count:
        if count[suit] == {}:
            for hand in hands:
                combinations[hand] += math.comb(to_be_dealt, 5)
        else:
            for current_hand in count[suit]:
                unblocked = True
                for other_hand in count[suit]:
                    if other_hand != current_hand and count[suit][other_hand] > 0:
                        unblocked = False
                if unblocked:
                    combinations[current_hand] += math.comb(to_be_dealt, 5-count[suit][current_hand])

    print(count, combinations)


def main():
    deck = Deck()
    print(deck)

    deck.shuffle()
    player1, player2 = Hand(), Hand()
    player1.new_cards([deck.deal(), deck.deal()])
    player2.new_cards([deck.deal(), deck.deal()])

    equity((player1, player2), deck)

    print(f'\n'
          f'{'':^7} Player 1  Player 2\n'
          f'{'Hand:':>7} {player1:<8}  {player2}\n'
          f'Equity: {f'{player1.equity:.2f}%':<8}  {player2.equity:.2f}%')

if __name__ == '__main__':
    main()