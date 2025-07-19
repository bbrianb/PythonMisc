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

    player.append(deck.deal())
    dealer.append(deck.deal())
    player.append(deck.deal())

    player_total, soft = blackjack_sum(player)

    print(f'Dealer  {dealer[0]}\n'
          f'Player  {print_cards(player)}  {player_total}{' (soft)' if soft else ''}')

    dealer.append(deck.deal())
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
            # don't forget to put cards back
            deck.cards.append(dealer.pop())

            odds_dict: dict = get_odds_dict(dealer, deck)

            queue: list = []

            dealer_total, _ = blackjack_sum(dealer)
            print(f'\nCurrent cards: {dealer}\nCurrent odds: {float(1)}\nTotal: {dealer_total}\n1 Card')

            represent_odds_dict(deck, odds_dict, queue)

            while queue:
                print(queue[0])
                total, soft, count, cards, odds = queue[0]
                print(f'\nCurrent odds: {odds}\nCurrent cards: {cards}\nTotal: {total}\n{len(cards)} Cards')
                for card in cards[1:]: # make sure these cards aren't in the deck
                    deck.deal(card.rankName, card.suit)

                odds_dict = get_odds_dict(cards, deck)

                represent_odds_dict(deck, odds_dict, queue)

                print(queue)

                for card in cards[1:]:
                    deck.cards.append(card)

                queue.pop(0)


def represent_odds_dict(deck, odds_dict, queue):
    for total in list(range(1, 22)) + ['bust']:
        if total in odds_dict:
            soft = odds_dict[total][0]
            count = odds_dict[total][1]
            odds = count / len(deck)
            print(f'{f'{total}{' (soft)' if soft else ''}':<9}  {odds * 100:>2.0f}%')
            if total != 'bust' and total < 17:
                queue.append([total, *odds_dict[total], odds])


def get_odds_dict(cards, deck):
    odds_dict = {'bust': [False, 0, None], 22: None}
    for next_rank in range(11, 1, -1):
        # have to put this card back
        next_rank_name = Card(next_rank).rankName

        next_card = deck.deal(next_rank_name)
        all_cards = cards + [next_card]
        total, soft = blackjack_sum(all_cards)
        if total <= 21:
            odds_dict[total] = [soft, deck.count(next_rank_name) + 1, all_cards]
        else:
            odds_dict['bust'][1] += deck.count(next_rank_name) + 1

        deck.cards.append(next_card)

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