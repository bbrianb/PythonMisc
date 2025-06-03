import random
import math


class Card:
    def __init__(self, rank: str, suit: str):
        self.rank: Rank = Rank(rank)
        self.suit: str = suit

    def __repr__(self):
        return str(self.rank) + self.suit

    def __eq__(self, other):
        if isinstance(other, Rank) or isinstance(other, int):
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
        self.rankNumber: int

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
        elif isinstance(other, int):
            if self.rankNumber == 14:
                return other in (1, 14)
            else:
                return self.rankNumber == other
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


def equity(hands, deck, community_cards=None):
    if community_cards is None:
        community_cards = []
    to_be_dealt = 7 - len(hands[0])
    runouts = {hand: 0 for hand in hands}

    # straight flush
    low_end = 10
    while low_end >= 1:
        in_range = {'s': {}, 'h': {}, 'c': {}, 'd': {}}
        blockers = {'s': {}, 'h': {}, 'c': {}, 'd': {}}
        for hand in hands:
            for card in hand.cards:
                if card in range(low_end, low_end + 5):
                    if hand in in_range[card.suit]:
                        in_range[card.suit][hand].append(card.rank)
                    else:
                        in_range[card.suit][hand] = [card.rank]

                elif card in range(low_end+5, low_end+10):
                    if hand in blockers[card.suit]:
                        blockers[card.suit][hand].append(card.rank)
                    else:
                        blockers[card.suit][hand] = [card.rank]

        for card in community_cards:
            if card in range(low_end+5, low_end+10):
                if 'community' in in_range[card.suit]:
                    in_range[card.suit]['community'].append(card.rank)
                else:
                    in_range[card.suit]['community'] = [card.rank]

        for suit in in_range:
            if in_range[suit] != {}:
                for current_hand in in_range[suit]:
                    if current_hand != 'community':
                        connectors = 0
                        for rank in range(low_end, low_end + 5):
                            if rank in in_range[suit][current_hand] + in_range[suit]['community']:
                                connectors += 1
                            else:
                                break

                        blocked = False

                        for other_hand in in_range[suit]:
                            if other_hand != current_hand and len(in_range[suit][other_hand]) > 0:
                                blocked = True
                                break

                        # add other blocks
                        if not blocked:
                            drawing = 5 - len(in_range[suit][current_hand])
                            runouts[current_hand] += math.comb(drawing, drawing) * math.comb(len(deck)-drawing, to_be_dealt-drawing)
                            print(low_end, current_hand, drawing, len(deck))
        for hand in runouts:
            hand.equity += runouts[hand]/math.comb(len(deck), to_be_dealt)

        low_end -= 1

    print(runouts)



def main():
    deck = Deck()
    print(deck)

    deck.shuffle()
    player1, player2 = Hand(), Hand()
    player1.new_cards([deck.deal('2', 's'), deck.deal('3', 's')])
    player2.new_cards([deck.deal('7', 's'), deck.deal('8', 's')])

    equity((player1, player2), deck)

    print(f'\n'
          f'{'':^7} Player 1  Player 2\n'
          f'{'Hand:':>7} {player1:<8}  {player2}\n'
          f'Equity: {f'{player1.equity:.2f}%':<8}  {player2.equity:.2f}%')


if __name__ == '__main__':
    main()