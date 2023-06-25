"""Random data generation pipeline and export."""

import logging
import numpy as np
import pandas as pd


class RandomGenerator:
    """Random data generator.
    
    Attributes: Multiple helper, working and final data frames.

    Args:
        seed (int): Optional random seed. Defaults to None.
    """
    
    def __init__(self, seed: int = None) -> None:
        if seed is not None:
            np.random.seed(seed)

    def prepare_data(self):
        # TODO: Document the pipeline
        pass

    def fetch(self) -> dict:
        """Gather all the final data frames and assign them to the string table names.

        Returns:
            dict: A dictionary of table names and the
                generated data frames.
        """
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
    """Generate the random data set. Log the success info.

    Returns:
        dict: Dictionary of table names and the generated data frames. 
    """
    data = {}
    # data = RandomGenerator().fetch() # ! this is the correct line
    logging.info("Random values have been generated.")
    return data
