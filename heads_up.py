import random
from enum import Enum, auto
import math


class Card:
    def __init__(self, rank, suit: str):
        self.rank: Rank = Rank(rank)
        self.suit: str = suit

    def __repr__(self):
        return str(self.rank) + self.suit

    def __eq__(self, other):
        if isinstance(other, Rank) or isinstance(other, int):
            return self.rank == other
        elif isinstance(other, str):
            if other.islower():
                return self.suit == other
            else:
                return self.rank == other
        elif isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        else:
            return False

    def __ge__(self, other):
        return self.rank >= other

    def __add__(self, other):
        return Card(self.rank+other, self.suit)

class Rank:
    def __init__(self, rank):
        if isinstance(rank, int):
            name_dict = {10: 'T', 11: 'J', 12: 'Q', 13: 'K', 14: 'A', 1: 'A'}
            if rank in name_dict:
                self.rankName = name_dict[rank]
            else:
                self.rankName = str(rank)
        else:
            self.rankName = rank

        self.rankNumber: int

        number_dict = {'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        if self.rankName in number_dict:
            self.rankNumber = number_dict[self.rankName]
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
        elif isinstance(other, str):
            return self.rankName == other
        else:
            return False

    def __ge__(self, other):
        return self.rankNumber >= other

    def __hash__(self):
        return hash(self.rankName)

    def __add__(self, other):
        return self.rankNumber + other

    def __gt__(self, other):
        if isinstance(other, Rank):
            return self.rankNumber > other.rankNumber
        return False

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

    def deal(self, hand, rank: str = None, suit: str = None) -> None:
        if rank and suit:
            rank_wanted = Rank(rank)
            for i, card in enumerate(self.cards):
                if card == rank_wanted and card == suit:
                    hand.cards.append(self.cards.pop(i))
                    break
        else:
            hand.cards.append(self.cards.pop())

    def count(self, thing):
        return self.cards.count(thing)

class Hand:
    def __init__(self):
        self.cards = []
        self.equity = 0

        self.winning_runouts = 0

    def __len__(self):
        return len(self.cards)

    def __repr__(self) -> str:
        output = ''
        for card in self.cards:
            output += str(card) + ' '
        return output[:-1]

    def __format__(self, format_spec):
        return f'{f'{str(self)}':{format_spec}}'

class HandStrength(Enum):
    STRAIGHT_FLUSH = auto()
    ROYAL_FLUSH = auto()

class Claim:
    def __init__(self, cards, hand_strength, belongs_to_hand, high_card_info):
        self.cards = cards
        self.handStrength = hand_strength
        self.belongsToHand = belongs_to_hand
        self.highCardInfo: list[Rank] = high_card_info
        self.blocked = 0

    def __repr__(self):
        return str([self.cards, self.handStrength, self.belongsToHand, self.highCardInfo, self.blocked])

    def __len__(self):
        return len(self.cards)


def equity(hands, deck, community_cards=None):
    if community_cards is None:
        community_cards = []
    to_be_dealt = 5 - len(community_cards)

    all_claims = get_claims(community_cards, deck, hands, to_be_dealt)
    process_claims(all_claims, deck, to_be_dealt)


def process_claims(all_claims, deck, to_be_dealt):
    print(all_claims)
    i = 0
    while i in range(len(all_claims) - 1):
        current_claim = all_claims[i]
        j = 0
        while j in range(len(all_claims[i + 1:])):
            k = i + 1 + j
            other_claim = all_claims[k]
            overlapping = sum(1 for card in other_claim.cards if card in current_claim.cards)

            # the same exact claim --> one claim has to lose, so it will get deleted
            if overlapping == len(current_claim):

                if current_claim.handStrength == other_claim.handStrength:
                    if current_claim.handStrength in (HandStrength.STRAIGHT_FLUSH, HandStrength.ROYAL_FLUSH):
                        if current_claim.highCardInfo[0] > other_claim.highCardInfo[0]:
                            all_claims.pop(k)
                            j -= 1
                        else:
                            all_claims.pop(i)
                            i -= 1
                else:
                    pass
                    # the higher hand automatically beats out the other one every time

            elif overlapping != 0:
                if current_claim.handStrength == other_claim.handStrength:
                    if current_claim.handStrength in (HandStrength.STRAIGHT_FLUSH, HandStrength.ROYAL_FLUSH):
                        if current_claim.highCardInfo[0] > other_claim.highCardInfo[0]:
                            stronger = i
                            weaker = k
                        else:
                            stronger = k
                            weaker = i

                        weaker_length = len(all_claims[weaker])
                        needed_for_block = len(all_claims[stronger]) - overlapping
                        new_deck = len(deck) - weaker_length - needed_for_block
                        remaining = max(to_be_dealt - weaker_length - needed_for_block, 0)

                        if needed_for_block <= to_be_dealt - weaker_length:
                            all_claims[weaker].blocked += math.comb(weaker_length, weaker_length) * math.comb(needed_for_block, needed_for_block) * math.comb(new_deck, remaining)
                            print(all_claims[weaker], all_claims[stronger], overlapping)
                else:
                    pass

            j += 1
        i += 1
    print(all_claims)


def get_claims(community_cards, deck, hands, to_be_dealt):
    for hand in hands:
        hand.winning_runouts = 0
    all_claims = []
    # straight flush
    for suit in ('s', 'h', 'c', 'd'):
        for low_end in range(10, 0, -1):
            current_straight = [Card(i, suit) for i in range(low_end, low_end + 5)]

            for current_hand in hands:
                potential_claim = current_straight.copy()

                for card in current_hand.cards + community_cards:
                    if card in current_straight:
                        potential_claim.remove(card)

                for card in potential_claim:
                    if card not in deck.cards:
                        break
                else:
                    if low_end == 10:
                        hand_strength = HandStrength.ROYAL_FLUSH
                    else:
                        hand_strength = HandStrength.STRAIGHT_FLUSH
                    if len(potential_claim) <= to_be_dealt and len(potential_claim) < 5:
                        all_claims.append(Claim(potential_claim, hand_strength, current_hand, [Rank(low_end+4)]))
    return all_claims


def main():
    deck = Deck()
    print(deck)

    deck.shuffle()
    player1, player2 = Hand(), Hand()
    deck.deal(player1, '2', 's')
    deck.deal(player1, '3', 's')
    deck.deal(player2, '7', 's')
    deck.deal(player2)

    equity((player1, player2), deck)

    print(f'\n'
          f'{'':^7} Player 1  Player 2\n'
          f'{'Hand:':>7} {player1:<8}  {player2}\n'
          f'Equity: {f'{player1.equity:.2f}%':<8}  {player2.equity:.2f}%')


if __name__ == '__main__':
    main()