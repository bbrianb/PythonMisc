import random
from enum import Enum, auto
from dataclasses import dataclass, field


class Card:
    def __init__(self, suit: str, card_value: str):
        self.suit: str = suit
        self.cardValue: str = card_value
        self.suitMatters: bool = False

        face_cards = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10}
        if self.cardValue in face_cards:
            self.numberValue = face_cards[self.cardValue]
        else:
            self.numberValue = int(self.cardValue)

    def __repr__(self):
        return f'{self.cardValue}{self.suit}'

    def __eq__(self, other):
        if isinstance(other, Card):
            if self.suitMatters or other.suitMatters:
                return self.cardValue == other.cardValue and self.suit == other.suit
            else:
                return self.cardValue == other.cardValue

        elif isinstance(other, str):
            if other.islower():
                return self.suit == other
            else:
                return self.cardValue == other

        elif isinstance(other, int):
            return self.numberValue == other

        else:
            return False

    def __add__(self, other):
        return self.numberValue + other

    def __gt__(self, other):
        if isinstance(other, Card):
            return self.numberValue > other.numberValue
        else:
            return self.numberValue > other

    def __ge__(self, other):
        return self > other or self.numberValue == other


class Deck:
    def __init__(self, suits, values):
        self.cards: list[Card] = []
        for suit in suits:
            for value in values:
                self.cards.append(Card(suit, value))

    def __len__(self):
        return len(self.cards)

    def __repr__(self):
        return str(self.cards)

    def deal(self, suit: str = None, value: str = None) -> Card:
        dealt_card = None

        if value and suit:
            for i, c in enumerate(self.cards):
                if c == value and c == suit:
                    dealt_card = c
                    self.cards.pop(i)
                    break
        else:
            dealt_card = self.cards.pop()
        return dealt_card

    def shuffle(self):
        random.shuffle(self.cards)

    def count_and_remove(self, thing):
        card_count = 0
        i = 0
        while i < len(self.cards):
            if self.cards[i] == thing:
                card_count += 1
                self.cards.pop(i)
                i -= 1
            i += 1
        return card_count


class HandStrength(Enum):
    HIGH_CARD = auto()
    PAIR = auto()
    TWO_PAIR = auto()
    THREE_OF_A_KIND = auto()
    STRAIGHT = auto()
    FLUSH = auto()
    FULL_HOUSE = auto()
    FOUR_OF_A_KIND = auto()
    STRAIGHT_FLUSH = auto()
    ROYAL_FLUSH = auto()


@dataclass
class HandAnalysis:
    handName: HandStrength | None = None
    numberOfPairs: int = 0
    numberOfThreeOfKinds: int = 0
    flushSuit: str = ''
    highCardInfo: list[str] = field(default_factory=list)
    fiveCardHand: list[Card] = field(default_factory=list)
    cards: list[Card] = field(default_factory=list)
    draws_dict: dict = field(default_factory=dict)


def get_hand_and_draws(cards):
    analysis = HandAnalysis()

    for card in cards:
        analysis.cards.append(card)

    analysis = check_pair_etc(analysis)
    analysis = check_straight_and_flush(analysis)
    analysis = find_5_card_hand(analysis)
    analysis = finalize_analysis(analysis)

    return (analysis.handName, analysis.highCardInfo, analysis.fiveCardHand), analysis.draws_dict


def check_pair_etc(analysis):
    for card in analysis.cards:
        number_of_matching_cards = analysis.cards.count(card)

        if card.cardValue not in analysis.highCardInfo:
            if number_of_matching_cards >= 2:
                hand_dict = {2: HandStrength.PAIR, 3: HandStrength.THREE_OF_A_KIND, 4: HandStrength.FOUR_OF_A_KIND}
                new_hand_name = hand_dict[number_of_matching_cards]
                if analysis.handName is None or new_hand_name.value > analysis.handName.value:
                    analysis.handName = new_hand_name
                    analysis.highCardInfo.append(card.cardValue)
                    if number_of_matching_cards == 2:
                        analysis.numberOfPairs += 1
                    elif number_of_matching_cards == 3:
                        analysis.numberOfThreeOfKinds += 1


    return analysis


def check_straight_and_flush(analysis):

    # noinspection SpellCheckingInspection
    suit_counts = {s: 0 for s in 'hdcs'}
    for card in analysis.cards:
        suit_counts[card.suit] += 1
    analysis.flushSuit, suit_count = max(suit_counts.items(), key=lambda x: x[1])

    analysis = check_straight_etc(analysis)

    check_flush(analysis, suit_count)

    return analysis


def check_straight_etc(analysis):
    add_draw(analysis, HandStrength.STRAIGHT, None)
    add_draw(analysis, HandStrength.STRAIGHT_FLUSH, None)
    add_draw(analysis, HandStrength.ROYAL_FLUSH, None)

    for card in analysis.cards:
        if card >= 10:
            possible_straight = [10, 11, 12, 13, 14]
        else:
            possible_straight = [i for i in range(card.numberValue, card + 5)]

        while card in possible_straight:
            analysis, straight_matches, straight_flush_matches, straight_absences, straight_flush_absences = check_straight_instance(analysis,
                                                                                                   possible_straight)
            if straight_flush_matches == 5:
                analysis.highCardInfo = [possible_straight[-1]]
                add_draw(analysis, HandStrength.STRAIGHT, None)
                if analysis.highCardInfo[0] == 14:
                    analysis.handName = HandStrength.ROYAL_FLUSH
                    add_draw(analysis, HandStrength.STRAIGHT_FLUSH, None)
                else:
                    analysis.handName = HandStrength.STRAIGHT_FLUSH
            elif straight_matches == 5:
                analysis.highCardInfo = [possible_straight[-1]]
                analysis.handName = HandStrength.STRAIGHT

            add_straight_draws(analysis, possible_straight, straight_absences, straight_flush_absences,
                               straight_flush_matches, straight_matches)

            possible_straight = decrease_possible_straight(possible_straight)
    return analysis


def add_straight_draws(analysis, possible_straight, straight_absences, straight_flush_absences, straight_flush_matches,
                       straight_matches):
    if straight_flush_matches == 4:
        addition = Card(analysis.flushSuit, straight_flush_absences[0])
        if not analysis.highCardInfo:
            analysis.highCardInfo = [0]
        if (analysis.handName not in [HandStrength.STRAIGHT_FLUSH, HandStrength.ROYAL_FLUSH]
                or addition.numberValue > analysis.highCardInfo[0]
        ):
            if possible_straight[-1] == 14:
                add_draw(analysis, HandStrength.ROYAL_FLUSH, addition)
            else:
                add_draw(analysis, HandStrength.STRAIGHT_FLUSH, addition)
    if straight_matches == 4:
        addition = straight_absences[0]
        if not analysis.highCardInfo:
            analysis.highCardInfo = [0]
        if (analysis.handName not in [HandStrength.STRAIGHT, HandStrength.STRAIGHT_FLUSH, HandStrength.ROYAL_FLUSH]
                or Card('', addition).numberValue > analysis.highCardInfo[0]
        ):
            add_draw(analysis, HandStrength.STRAIGHT, addition)


def check_flush(analysis, suit_count):
    if suit_count > 4 and analysis.handName not in [HandStrength.ROYAL_FLUSH, HandStrength.STRAIGHT_FLUSH]:
        analysis.handName = HandStrength.FLUSH
    elif suit_count == 4 and analysis.handName not in [HandStrength.ROYAL_FLUSH, HandStrength.STRAIGHT_FLUSH,
                                                       HandStrength.FLUSH]:
        add_draw(analysis, HandStrength.FLUSH, None)
        add_draw(analysis, HandStrength.FLUSH, analysis.flushSuit)


def find_5_card_hand(analysis):
    the_fok = None

    if analysis.handName == HandStrength.STRAIGHT_FLUSH or analysis.handName == HandStrength.ROYAL_FLUSH:
        find_straight(analysis, True)

    elif analysis.handName == HandStrength.FOUR_OF_A_KIND:
        find_four_of_kind(analysis, the_fok)

    elif full_house_logic(analysis):
        find_full_house(analysis)

    elif analysis.handName == HandStrength.FLUSH:
        find_flush(analysis)

    elif analysis.handName == HandStrength.STRAIGHT:
        find_straight(analysis)

    elif analysis.handName == HandStrength.THREE_OF_A_KIND:
        find_three_of_kind(analysis)


    elif analysis.numberOfPairs == 2 or analysis.numberOfPairs == 3:  # have to account for 3 pairs
        find_two_pairs(analysis)

    elif analysis.handName == HandStrength.PAIR:
        find_pair(analysis)

    else:
        find_high_card(analysis)


    return analysis


def find_high_card(analysis):
    for c in analysis.cards:
        add_draw(analysis, HandStrength.PAIR, c.cardValue)


def find_pair(analysis):
    find_matching_cards(analysis, 2, analysis.highCardInfo[0])
    add_draw(analysis, HandStrength.THREE_OF_A_KIND, analysis.highCardInfo[0])
    for c in analysis.cards:
        if c != analysis.highCardInfo[0]:
            add_draw(analysis, HandStrength.TWO_PAIR, c.cardValue)


def find_two_pairs(analysis):
    analysis.handName = HandStrength.TWO_PAIR
    if analysis.numberOfPairs == 3:
        analysis.highCardInfo.remove(min(analysis.highCardInfo))
    high_pair = max(analysis.highCardInfo)
    low_pair = min(analysis.highCardInfo)
    analysis.highCardInfo = [high_pair, low_pair]
    for pairValue in analysis.highCardInfo:
        find_matching_cards(analysis, 2, pairValue)
        add_draw(analysis, HandStrength.FULL_HOUSE, pairValue)


def find_three_of_kind(analysis):
    find_matching_cards(analysis, 3, analysis.highCardInfo[0])
    add_draw(analysis, HandStrength.FOUR_OF_A_KIND, analysis.highCardInfo[0])


def find_flush(analysis):
    for _ in range(2):
        for card in analysis.cards:
            if card != analysis.flushSuit:
                move_card(analysis, analysis.cards.index(card), False)


def find_full_house(analysis):
    analysis.handName = HandStrength.FULL_HOUSE
    pairs = []
    three_of_kinds = []
    for value in analysis.highCardInfo:
        if analysis.cards.count(value) == 3:
            three_of_kinds.append(value)
        else:
            pairs.append(value)
    the_three_of_kind = max(three_of_kinds)
    if pairs:
        the_pair = max(pairs)
    else:
        the_pair = min(three_of_kinds)
    find_matching_cards(analysis, 3, the_three_of_kind)
    find_matching_cards(analysis, 2, the_pair)
    add_draw(analysis, HandStrength.FOUR_OF_A_KIND, the_three_of_kind)
    if the_pair > the_three_of_kind:
        add_draw(analysis, HandStrength.FULL_HOUSE, the_pair)
    analysis.highCardInfo = three_of_kinds + pairs


def find_four_of_kind(analysis, the_fok):
    for value in analysis.highCardInfo:
        if analysis.cards.count(value) == 4:
            the_fok = value
    find_matching_cards(analysis, 4, the_fok)


def find_straight(analysis, flush=False):
    straight_high_card = int(analysis.highCardInfo[0])
    current_value = straight_high_card

    while current_value > straight_high_card - 5 and current_value > 1:
        i = analysis.cards.index(current_value)
        if analysis.cards[i] == analysis.flushSuit or not flush:
            move_card(analysis, i)
            current_value -= 1

    if current_value == 1:
        for i, value in enumerate(analysis.cards):
            if value.cardValue == 'A' and (analysis.cards[i] == analysis.flushSuit or not flush):
                move_card(analysis, i)
                break

    return analysis


def move_card(analysis, current_index, add_to_hand=True):
    current_card = analysis.cards.pop(current_index)

    if add_to_hand:
        analysis.fiveCardHand.append(current_card)

    return analysis


def find_matching_cards(analysis, count, card):
    for _ in range(count):
        move_card(analysis, analysis.cards.index(card))
    return analysis


def full_house_logic(analysis):
    return ((analysis.numberOfPairs == 0 and analysis.numberOfThreeOfKinds == 2)
            or (analysis.numberOfPairs == 1 and analysis.numberOfThreeOfKinds == 1)
            or (analysis.numberOfPairs == 2 and analysis.numberOfThreeOfKinds == 1))


def finalize_analysis(analysis):
    while len(analysis.fiveCardHand) < 5:
        move_card(analysis, analysis.cards.index(max(analysis.cards)))

    if not analysis.highCardInfo or analysis.highCardInfo == [0]:
        analysis.highCardInfo = [max(card.numberValue for card in analysis.fiveCardHand)]

    if analysis.handName == HandStrength.ROYAL_FLUSH:
        analysis.highCardInfo = []
    if analysis.handName is None:
        analysis.handName = HandStrength.HIGH_CARD

    # turn int into str
    if len(analysis.highCardInfo) == 1 and isinstance(analysis.highCardInfo[0], int):
        analysis.highCardInfo = [get_card_value(analysis.highCardInfo[0])]

    if analysis.handName not in analysis.draws_dict:
        add_draw(analysis, analysis.handName, None)
    return analysis


def check_straight_instance(analysis, possible_straight):
    straight_matches = 0
    straight_flush_matches = 0
    straight_absences = []
    straight_flush_absences = []
    for possible_value in possible_straight:
        found_for_straight = False
        found_for_straight_flush = False
        for i, c in enumerate(analysis.cards):
            if c == possible_value or (c == 'A' and possible_value == 1):
                if not found_for_straight:
                    found_for_straight = True
                    straight_matches += 1
                if analysis.cards[i] == analysis.flushSuit:
                    found_for_straight_flush = True
                    straight_flush_matches += 1
        if not found_for_straight:
            straight_absences.append(get_card_value(possible_value))
        if not found_for_straight_flush:
            straight_flush_absences.append(get_card_value(possible_value))
    return analysis, straight_matches, straight_flush_matches, straight_absences, straight_flush_absences


def decrease_possible_straight(possible_straight):
    if possible_straight[0] == 1:
        return [None for _ in range(5)]
    else:
        out_straight = []
        for v in possible_straight:
                out_straight.append(v-1)
        return out_straight


def get_card_value(number_value: int) -> str:
    face_cards = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
    if number_value <= 10:
        return str(number_value)
    else:
        return face_cards[number_value]


def display_probabilities(draws_dict, deck, hand_name):
    number_of_cards = len(deck)
    output_dict = {}
    all_outs = 0

    strength = 10
    while strength >= hand_name.value:
        for drawName in draws_dict:
            if drawName.value == strength:
                outs_list = draws_dict[drawName]
                outs = 0
                if outs_list:
                    for datum in outs_list:
                        if isinstance(datum, Card):
                            datum.suitMatters = True
                        outs += deck.count_and_remove(datum)
                    all_outs += outs
                output_dict[drawName] = outs
        strength -= 1

    output_dict[hand_name] += number_of_cards - all_outs

    strength = 10
    while strength > 0:
        for key in output_dict:
            if key.value == strength and output_dict[key] != 0:
                percent = output_dict[key]/number_of_cards*100
                print(f'{key:<28}  {f'{percent:.2f}%':>6}  {'█' * output_dict[key]}')
        strength -= 1


def add_draw(analysis, key, addition):
    if key not in analysis.draws_dict or addition is None:
        analysis.draws_dict[key] = []
    if addition is not None and addition not in analysis.draws_dict[key]:
        analysis.draws_dict[key].append(addition)
    return analysis


def main(cheating=False):
    suits = ['h', 's', 'c', 'd']
    values = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

    deck = Deck(suits, values)

    deck.shuffle()

    if cheating:
        two_card_hand = [deck.deal('c', 'A'), deck.deal('c', '2')]
        turn = [deck.deal('c', '3'), deck.deal('c', '4'), deck.deal('c', '5'),
                deck.deal('h', '4')]
    else:
        two_card_hand = [deck.deal(), deck.deal()]
        turn = [deck.deal() for _ in range(4)]

    result, draws_dict = get_hand_and_draws(two_card_hand + turn)
    hand_name = result[0]

    print('Turn\n'
          f'{turn}\n'
          'Hand\n'
          f'{two_card_hand}\n'
          'Result\n'
          f'{result}\n')

    display_probabilities(draws_dict, deck, hand_name)


if __name__ == '__main__':
    main()