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
    FOUR_OF_A_KIND = auto()
    STRAIGHT_FLUSH = auto()
    ROYAL_FLUSH = auto()


class Claim:
    def __init__(self, cards, hand_strength, belongs_to_hand, high_card_info, original_claim):
        self.cards = cards
        self.handStrength = hand_strength
        self.belongsToHand = belongs_to_hand
        self.highCardInfo: list[Rank] = high_card_info
        self.originalClaim = original_claim
        self.blocked = 0

    def __repr__(self):
        return str([self.cards, self.handStrength, self.highCardInfo, self.belongsToHand, self.blocked])

    def __len__(self):
        return len(self.cards)

    def __eq__(self, other):
        if isinstance(other, Claim):
            return self.cards == other.cards and self.belongsToHand == other.belongsToHand and self.highCardInfo == other.highCardInfo
        else:
            return False


def equity(hands, deck, community_cards=None):
    if community_cards is None:
        community_cards = []
    to_be_dealt = 5 - len(community_cards)

    all_claims = get_claims(community_cards, deck, hands)
    process_claims(all_claims, hands, deck, to_be_dealt)


def get_claims(community_cards, deck, hands):
    for hand in hands:
        hand.winning_runouts = 0

    potential_claims = []

    # straight flush
    for suit in ('s', 'h', 'c', 'd'):
        for low_end in range(10, 0, -1):
            current_straight = [Card(i, suit) for i in range(low_end, low_end + 5)]

            for current_hand in hands:
                potential_claim = current_straight.copy()

                for card in current_hand.cards + community_cards:
                    if card in current_straight:
                        potential_claim.remove(card)

                if low_end == 10:
                    hand_strength = HandStrength.ROYAL_FLUSH
                else:
                    hand_strength = HandStrength.STRAIGHT_FLUSH

                potential_claims.append(Claim(potential_claim, hand_strength, current_hand, [Rank(low_end+4)], current_straight))

    # quads
    for current_rank in range(14, 1, -1):
        for kicker in range(14, 1, -1):
            if kicker != current_rank:
                for current_suit in ('s', 'h', 'c', 'd'):
                    current_quads = [Card(current_rank, suit) for suit in ('s', 'h', 'c', 'd')] + [Card(kicker, current_suit)]
                    for current_hand in hands:
                        potential_claim = current_quads.copy()

                        for card in current_hand.cards + community_cards:
                            if card in current_quads:
                                potential_claim.remove(card)

                        potential_claims.append(Claim(potential_claim, HandStrength.FOUR_OF_A_KIND, current_hand, [Rank(current_rank), Rank(kicker)], current_quads))

    all_claims = []
    for potential_claim in potential_claims:
        for card in potential_claim.cards:
            if card not in deck.cards:
                break
        else:
            if len(potential_claim) < len(potential_claim.originalClaim) and all_claims.count(potential_claim) == 0:
                all_claims.append(potential_claim)

    return all_claims


# noinspection PyUnusedLocal
def process_claims(all_claims, hands, deck, to_be_dealt):
    print(all_claims)
    current_index = 0
    while current_index in range(len(all_claims) - 1):
        j = 0
        while j in range(len(all_claims[current_index + 1:])):
            current_claim = all_claims[current_index]
            other_index = current_index + 1 + j
            other_claim = all_claims[other_index]
            overlapping = sum(1 for card in other_claim.cards if card in current_claim.cards)

            if overlapping == len(current_claim) or overlapping == len(other_claim):
                stronger_hand = determine_stronger_hand(current_claim, other_claim)
                print(current_claim, other_claim, stronger_hand)

                if stronger_hand in ('chop', 'current'):
                    all_claims.pop(other_index)
                if stronger_hand in ('chop', 'other'):
                    all_claims.pop(current_index)
                    current_index -= 1
                j -= 1

            elif overlapping != 0:
                stronger_hand = determine_stronger_hand(current_claim, other_claim)

                if stronger_hand == 'current':
                    stronger = current_index
                    weaker = other_index
                else:
                    stronger = other_index
                    weaker = current_index

                weaker_length = len(all_claims[weaker])
                needed_for_block = len(all_claims[stronger]) - overlapping
                new_deck_length = len(deck) - weaker_length - needed_for_block
                remaining = max(to_be_dealt - weaker_length - needed_for_block, 0)

                if needed_for_block <= to_be_dealt - weaker_length:
                    all_claims[weaker].blocked += math.comb(new_deck_length, remaining)

            j += 1
        current_index += 1

    print(all_claims)

    for claim in all_claims:
        claim_length = len(claim)
        remaining = to_be_dealt - claim_length
        new_deck_length = len(deck) - claim_length

        claim.belongsToHand.winning_runouts += math.comb(new_deck_length, remaining) - claim.blocked

    for hand in hands:
        hand.equity = hand.winning_runouts / math.comb(len(deck), to_be_dealt)
        print(hand, hand.winning_runouts, hand.equity)


def determine_stronger_hand(current_claim, other_claim):
    if current_claim.tempHandStrength == other_claim.tempHandStrength:
        return compare_high_cards(current_claim.tempHighCardInfo, other_claim.tempHighCardInfo)
    elif current_claim.tempHandStrength.value > other_claim.tempHandStrength.value:
        return 'current'
    else:
        return 'other'


def compare_high_cards(current_high_cards, other_high_cards):
    for current_info, other_info in zip(current_high_cards, other_high_cards):
        if current_info > other_info:
            return 'current'
        elif other_info > current_info:
            return 'other'
    else:
        return 'chop'


def main():
    deck = Deck()
    print(deck)

    deck.shuffle()
    player1, player2 = Hand(), Hand()
    players = player1, player2

    cheating = True
    if cheating:
        deck.deal(player1, '5', 's')
        deck.deal(player1, 'K', 'h')
        deck.deal(player2, '7', 'h')
        deck.deal(player2, 'Q', 'h')
    else:
        for _ in range(2):
            for player in players:
                deck.deal(player)

    equity((player1, player2), deck)

    print(f'\n'
          f'{'':^7} Player 1  Player 2\n'
          f'{'Hand:':>7} {player1:<8}  {player2}\n'
          f'Equity: {f'{player1.equity:.2f}%':<8}  {player2.equity:.2f}%')


if __name__ == '__main__':
    main()