from random import shuffle

class Deck:
    def __init__(self) -> None:
        self.cards = []
        self.suits = 's', 'h', 'c', 'd'
        self.ranks = 'A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K'

        for suit in self.suits:
            for rank in self.ranks:
                self.cards.append(Card(rank, suit))

    def shuffle_deck(self) -> None:
        shuffle(self.cards)

    def deal(self, rank: str = None, suit: str = None):
        if rank and suit:
            for i, card in enumerate(self.cards):
                if card == rank and card == suit:
                    return self.cards.pop(i)
        elif rank:
            for i, card in enumerate(self.cards):
                if card == rank:
                    return self.cards.pop(i)
        else:
            return self.cards.pop()

    def count(self, item):
        return self.cards.count(item)

    def __repr__(self) -> str:
        output = ''
        for card in self.cards:
            output += str(card) + " "
        return output[:-1]

    def __len__(self) -> int:
        return len(self.cards)

class Card:
    def __init__(self, rank=None, suit=None) -> None:
        self.rankName: str
        self.rankNumber: int
        self.suit: str = suit
        self.fullCompare: bool = False
        if suit is None:
            self.suit = ''

        self.numbers_dict: dict = {'A': 11, 'T': 10, 'J': 10, 'Q': 10, 'K': 10}
        self.names_dict: dict = {11: 'A', 10: 'T'}

        if rank in self.numbers_dict:
            self.rankName = rank
            self.rankNumber = self.numbers_dict[self.rankName]
        elif isinstance(rank, str):
            self.rankName = rank
            self.rankNumber = int(self.rankName)
        elif rank in self.names_dict:
            self.rankName = self.names_dict[rank]
            self.rankNumber = rank
        else:
            self.rankName = str(rank)
            self.rankNumber = rank

    def __repr__(self) -> str:
        if self.suit is None:
            return self.rankName
        else:
            return self.rankName + self.suit

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            if other.isupper() or other.isnumeric():
                if other == 'T':
                    return self.rankName in ('T', 'J', 'Q', 'K')
                else:
                    return self.rankName == other
            else:
                return self.suit == other
        else:
            return False

    def __int__(self):
        return self.rankNumber

def main() -> None:
    deck: Deck = Deck()

    print(deck)

    deck.shuffle_deck()

    player: list[Card] = []
    dealer: list[Card] = []

    player.append(deck.deal('T', 'h'))
    dealer.append(deck.deal('T', 's'))
    player.append(deck.deal('6', 'd'))

    player_total, soft = blackjack_sum(player)

    print(f'Dealer  {dealer[0]}\n'
          f'Player  {print_cards(player)}  {player_total}{' (soft)' if soft else ''}')
    dealer_total, _ = blackjack_sum(dealer)
    if dealer_total == 21:
        print('Dealer has blackjack')
        if player_total == 21:
            print('Player has blackjack')
            print('Push')
    else:
        print('Dealer does not have blackjack')
        if player_total == 21:
            print('Player has blackjack')
        else:
            deck.cards.append(dealer.pop())

            odds_dict = get_odds_dict(dealer, deck)
            print(odds_dict, sum(odds_dict.values()))

def get_odds_dict(input_cards: list[Card], deck: Deck, space='') -> dict:
    output_odds: dict = {}
    next_card_rank: int = 11
    while next_card_rank > 1:
        next_card_rank_name: str = Card(next_card_rank).rankName
        next_card: Card = deck.deal(next_card_rank_name)
        current_odds: float = (deck.count(next_card_rank_name) + 1)/(len(deck) + 1)

        if next_card:
            current_cards = input_cards + [next_card]

            total, _ = blackjack_sum(current_cards)

            if total < 17:
                next_odds = get_odds_dict(current_cards, deck, space+'   ')

                # odds of getting both the current card and the one before
                adjusted_odds: dict = {}
                for key in next_odds:
                    adjusted_odds[key] = current_odds * next_odds[key]

                for key in adjusted_odds:
                    if key in output_odds:
                        output_odds[key] += adjusted_odds[key]
                    else:
                        output_odds[key] = adjusted_odds[key]

                # print(current_cards, total, current_odds, next_odds, adjusted_odds, output_odds)
            elif total <= 21:
                    output_odds[total] = current_odds
            else:
                if 'bust' in output_odds:
                    output_odds['bust'] += current_odds
                else:
                    output_odds['bust'] = current_odds

            deck.cards.append(next_card)
        next_card_rank -= 1
    return output_odds

def blackjack_sum(cards: list[Card]) -> tuple[int, bool]:
    output = 0
    soft = False
    ace_count = 0

    for card in cards:
        output += int(card)

        if card == 'A':
            ace_count += 1

    while output > 21 and ace_count > 0:
        output -= 10
        ace_count -= 1
    if output <= 21 and ace_count > 0:
        soft = True
    return output, soft

def print_cards(cards: list[Card]) -> str:
    output = ''
    for card in cards:
        output += str(card) + ' '
    return output[:-1]

if __name__ == '__main__':
    main()