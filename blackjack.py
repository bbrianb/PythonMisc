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
    def __init__(self, rank, suit) -> None:
        self.rankName: str
        self.rankNumber: int
        self.suit: str = suit
        self.fullCompare = False

        numbers = {'A': 11, 'T': 10, 'J': 10, 'Q': 10, 'K': 10}
        names = {11: 'A', 10: 'T'}

        if rank in numbers:
            self.rankName = rank
            self.rankNumber = numbers[self.rankName]
        elif isinstance(rank, str):
            self.rankName = rank
            self.rankNumber = int(self.rankName)
        elif rank in names:
            self.rankName = names[rank]
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
                return False
        elif isinstance(other, Card):
            if self.fullCompare or other.fullCompare:
                return self.rankNumber == other.rankNumber and self.suit == other.suit
            else:
                return self.rankNumber == other.rankNumber
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

    player.append(deck.deal())
    dealer.append(deck.deal())
    player.append(deck.deal())
    dealer.append(deck.deal())

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
            print(odds_dict)


def get_odds_dict(current_cards: list[Card], deck: Deck) -> dict:
    odds_dict = dict.fromkeys(range(2, 22), 0.)
    return odds_dict


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