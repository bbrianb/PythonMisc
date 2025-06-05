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

    def deal(self, rank: str = None, suit: str = None) -> Card:
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
        self.equity = 0

    def new_cards(self, new_cards):
        for card in new_cards:
            self.cards.append(card)

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

    to_be_dealt = 5 - len(community_cards)

    winning_runouts = {hand: 0 for hand in hands}

    # straight flush
    low_end = 10
    while low_end >= 1:
        in_range = {'s': {}, 'h': {}, 'c': {}, 'd': {}}
        blockers = {'s': {}, 'h': {}, 'c': {}, 'd': {}}

        for hand in hands:
            for rank in hand.cards:
                if rank in range(low_end, low_end + 5):
                    if hand in in_range[rank.suit]:
                        in_range[rank.suit][hand].append(rank.rank)
                    else:
                        in_range[rank.suit][hand] = [rank.rank]

                elif rank in range(low_end+5, low_end+9):
                    if hand in blockers[rank.suit]:
                        blockers[rank.suit][hand].append(rank.rank)
                    else:
                        blockers[rank.suit][hand] = [rank.rank]

        for suit in in_range:
            in_range[suit]['community'] = []
            blockers[suit]['community'] = []

        for rank in community_cards:
            if rank in range(low_end, low_end+5):
                in_range[rank.suit]['community'].append(rank.rank)
            elif rank in range(low_end+5, low_end+9):
                blockers[rank.suit]['community'].append(rank.rank)

        for suit in in_range:
            if in_range[suit] != {}:

                for current_hand in in_range[suit]:
                    if current_hand != 'community':

                        for other_hand in in_range[suit]:
                            if other_hand not in (current_hand, 'community') and len(in_range[suit][other_hand]) > 0:
                                break
                        else:
                            straight_so_far = in_range[suit][current_hand] + in_range[suit]['community']
                            needed_for_straight = [i for i in range(low_end, low_end+5)]
                            for rank in straight_so_far:
                                if rank in needed_for_straight:
                                    needed_for_straight.remove(rank)

                            nfs = len(needed_for_straight)
                            if nfs <= to_be_dealt:
                                consecutive = 1
                                for i, rank in enumerate(needed_for_straight[:-1]):
                                    if rank + 1 == needed_for_straight[i+1]:
                                        consecutive += 1
                                    else:
                                        consecutive = 1

                                needed_for_block = []

                                # ts may be wrong
                                for i in range(5 - consecutive):

                                    needed_for_block.append(needed_for_straight[-1]+i+1)

                                print(f'{low_end=}, {current_hand=}, {community_cards=}, {needed_for_straight=}, {consecutive=}, {needed_for_block=}')

                                blocking_runouts = 0

                                for other_hand in blockers[suit]:
                                    if other_hand == 'community':
                                        other_ranks = []
                                    else:
                                        other_ranks = blockers[suit][other_hand]
                                    other_ranks += blockers[suit]['community']

                                    blockers_found = 0
                                    for rank in other_ranks:
                                        if rank in needed_for_block:
                                            blockers_found += 1
                                            needed_for_block.remove(rank)

                                    blocking_cards = len(needed_for_block)

                                    print(f'{other_hand=}, {needed_for_block=} {blockers_found=}, {blockers_found == len(needed_for_block)}')

                                    if blockers_found == len(needed_for_block):
                                        break
                                    elif blocking_cards < to_be_dealt and nfs + blocking_cards < to_be_dealt:
                                            print(to_be_dealt, nfs, blocking_cards)
                                            blocking_runouts = math.comb(nfs, nfs) * math.comb(blocking_cards, blocking_cards) * math.comb(len(deck)-nfs-blocking_cards, to_be_dealt - nfs - blocking_cards)

                                print(nfs, len(deck)-nfs, to_be_dealt-nfs)
                                winning_runouts[current_hand] += math.comb(nfs, nfs) * math.comb(len(deck) - nfs, to_be_dealt - nfs) - blocking_runouts
        for hand in winning_runouts:
            hand.equity += winning_runouts[hand]/math.comb(len(deck), to_be_dealt)

        low_end -= 1

    print(winning_runouts)



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