import logging
import numpy as np
import pandas as pd


class RandomGenerator:
    def __init__(self, seed: int = None) -> None:
        if seed is not None:
            np.random.seed(seed)

    def prepare_data(self):
        pass

    def fetch(self):
        self.prepare_data()
        return {
            "city": self.city,
            "customers": self.customers,
            "expense_titles": self.expense_titles,
            "expense_types": self.expense_types,
            "games": self.games,
            "game_categories": self.game_categories,
            "game_prices": self.cugame_pricess,
            "game_types": self.game_types,
            "inventory": self.inventory,
            "invoices": self.invoices,
            "maintenance_expenses": self.maintenance_expenses,
            "participations": self.participations,
            "partners": self.partners,
            "payments": self.payments,
            "relationships": self.relationships,
            "rental": self.rental,
            "sales": self.sales,
            "staff": self.staff,
            "tournaments": self.tournaments,
        }


def generate_data() -> dict:
    data = {}
    # data = RandomGenerator().fetch() # ! this is the correct line
    logging.info("Random values have been generated.")
    return data
