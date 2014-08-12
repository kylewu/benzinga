class CannotFindStockException(Exception):
    pass


class EmptySymbolException(Exception):
    pass


class PriceChangedException(Exception):
    pass


class NotEnoughStockInMarket(Exception):
    pass


class NotEnoughStockInHands(Exception):
    pass


class NotEnoughFundExceptin(Exception):
    pass


class NegativeQuantityException(Exception):
    pass
