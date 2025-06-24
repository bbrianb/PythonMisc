import random

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

    def __int__(self):
        if self.rank.rankNumber == 14:
            return 11
        else:
            return min(self.rank.rankNumber, 10)

class Hand:
    def __init__(self, hand_type='player'):
        self.type = hand_type
        self.cards = []
        if self.type == 'dealer':
            self.mode = 1
        else:
            self.mode = 2
        self.total = 0
        self.soft = False

    def __getitem__(self, item):
        return self.cards[item]

    def __repr__(self):
        output = ''
        for card in self.cards[:self.mode]:
            output += str(card) + " "
        return output[:-1]

    def get_total(self):
        self.total = sum(int(card) for card in self.cards[:self.mode])
        if 'A' in self.cards[:self.mode]:
            if self.total <= 21:
                self.soft = True
            elif self.total > 21:
                aces_count = self.cards[:self.mode].count('A')
                aces_found = 0
                for card in self.cards[:self.mode]:
                    if card == 'A':
                        aces_found += 1
                        self.total -= 10
                        if self.total <= 21 and aces_found < aces_count:
                            self.soft = True
                        break
                else:
                    self.soft = False
        else:
            self.soft = False
        if self.soft:
            soft_output = ' (soft)'
        else:
            soft_output = ''
        return str(self.total) + soft_output

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

def main():
    deck = Deck()

    print(deck)

    deck.shuffle()

    player, dealer = Hand(), Hand('dealer')
    for _ in range(2):
        deck.deal(player)
        deck.deal(dealer)

    print(f'{'Dealer':<12}  {dealer}\n'
          f'Dealer total  {dealer.get_total()}\n'
          f'{'Player':<12}  {player[0]} {player[1]}\n'
          f'Player total  {player.get_total()}')

    ranks = '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'
    possibilities = {}

if __name__ == '__main__':
    main()