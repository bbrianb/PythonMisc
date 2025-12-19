class Rank:
    def __init__(self, symbol: str) -> None:
        self.symbol: str = symbol
        symbol_to_value: dict[str, int] = {'T': 10, 'J': 10,'Q': 10, 'K': 10, 'A': 11}
        if self.symbol in symbol_to_value:
            self.value = symbol_to_value[self.symbol]
        else:
            self.value = str(self.symbol)

class Suit:
    def __init__(self) -> None:
        pass

class Card:
    def __init__(self) -> None:
        pass

class Deck:
    def __init__(self) -> None:
        pass

def main() -> None:
    deck: Deck = Deck()

if __name__ == '__main__':
    main()