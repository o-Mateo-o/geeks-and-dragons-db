"""Random data generation pipeline and export."""

import logging
import datetime
from pathlib import Path
import itertools
import holidays
import numpy as np
import pandas as pd
import json
from faker import Faker

from src.randutils import RandomHelpers


class RandomGenerator:
    """Random data generator.

    Attributes: Multiple helper, working and final data frames.

    Args:
        seed (int): Optional random seed. Defaults to None.
    """

    def __init__(self, seed: int = None) -> None:
        if seed is not None:
            np.random.seed(seed)
        self.random_helpers: RandomHelpers = None
        with open(Path("config/random.settings.json"), "r") as f:
            self.config = json.load(f)

        self.prompt_games = pd.DataFrame()
        self.prompt_first_names_males = pd.DataFrame()
        self.prompt_last_names_males = pd.DataFrame()
        self.prompt_first_names_females = pd.DataFrame()
        self.prompt_last_names_females = pd.DataFrame()
        self.prompt_cities = pd.DataFrame()
        self.prompt_emails = pd.DataFrame()
        self.prompt_tournaments = pd.DataFrame()

    def _assign_random_helpers(self) -> None:
        self.random_helpers = RandomHelpers(
            self.config,
            {
                "prompt_first_names_males": self.prompt_first_names_males,
                "prompt_last_names_males": self.prompt_last_names_males,
                "prompt_first_names_females": self.prompt_first_names_females,
                "prompt_last_names_females": self.prompt_last_names_females,
                "prompt_dates": self.prompt_dates,
                "prompt_emails": self.prompt_emails,
            },
        )

    def read_prompts(self) -> None:
        self.prompt_games = pd.read_csv(Path("config/prompts/games.csv"))
        self.prompt_first_names_males = pd.read_csv(
            Path("config/prompts/names_males.csv")
        )
        self.prompt_last_names_males = pd.read_csv(
            Path("config/prompts/lastnames_males.csv")
        )
        self.prompt_first_names_females = pd.read_csv(
            Path("config/prompts/names_females.csv")
        )
        self.prompt_last_names_females = pd.read_csv(
            Path("config/prompts/lastnames_females.csv")
        )
        self.prompt_cities = pd.read_csv(Path("config/prompts/cities.csv"))
        self.prompt_emails = pd.read_csv(Path("config/prompts/domains.csv"))
        self.prompt_tournaments = pd.read_csv(Path("config/prompts/tournaments.csv"))

    def gen_prompt_dates(self) -> None:
        # all the dates
        self.prompt_dates = pd.DataFrame(
            {
                "date": pd.date_range(
                    end=datetime.datetime.now().date(),
                    periods=365 * self.config["shop_lifetime_years"],
                )
            }
        )
        # weekdays
        self.prompt_dates["weekday"] = self.prompt_dates["date"].apply(
            lambda date: date.weekday()
        )
        self.prompt_dates["weekday_name"] = self.prompt_dates["weekday"].astype(str).map(
            self.config["weekday_dict"]
        )
        # filtering sundays and holidays
        holidays_pl = holidays.Poland()
        holiday_mask = self.prompt_dates["date"].apply(lambda date: date in holidays_pl)
        self.prompt_dates = self.prompt_dates[
            (self.prompt_dates["weekday"] != 6) & ~holiday_mask
        ]
        # adding the base traffic volume
        ### initial numbe
        self.prompt_dates["volume_base"] = self.config["initial_customer_n"]
        ### a linear trend
        self.prompt_dates["volume_base"] += (
            np.repeat(
                self.config["daily_customer_increment"], self.prompt_dates.shape[0]
            )
            .cumsum()
            .round()
        )
        ### additional traffic for each day
        self.prompt_dates["volume_base"] += (
            self.prompt_dates["weekday"].astype(str).map(self.config["weekly_extras"])
            * self.config["weekly_extras_multip"]
        )
        # adding sales and rental traffic
        ### sales = base + noise
        self.prompt_dates["volume_sales"] = (
            self.prompt_dates["volume_base"]
            + np.random.normal(
                loc=0, scale=self.config["traffic_std"], size=self.prompt_dates.shape[0]
            )
        ).round()
        ### rental = base * ratio + noise
        self.prompt_dates["volume_rental"] = (
            self.prompt_dates["volume_base"] * self.config["rental_to_sales_ratio"]
            + np.random.normal(
                loc=0, scale=self.config["traffic_std"], size=self.prompt_dates.shape[0]
            )
        ).round()
        self.prompt_dates = self.prompt_dates.reset_index(drop=True)

    def gen_prompt_hours(self) -> None:
        # list of the hours when opened
        self.prompt_hours = pd.DataFrame(
            {
                "hour": np.arange(
                    start=self.config["shop_open_hours"]["from"],
                    stop=self.config["shop_open_hours"]["to"],
                )
            }
        )
        # traffic increments
        self.prompt_hours["customer_n"] = np.random.exponential(
            size=self.prompt_hours.shape[0]
        ).cumsum()
        # traffic decrements after the pick
        decrease_stage = self.prompt_hours[
            self.prompt_hours["hour"] > self.config["shop_open_hours"]["pick"]
        ]
        self.prompt_hours.loc[
            decrease_stage.index, "customer_n"
        ] -= np.random.exponential(
            scale=self.config["traffic_decrease_magnitude"],
            size=decrease_stage.shape[0],
        ).cumsum()
        # probability column
        self.prompt_hours.loc[self.prompt_hours["customer_n"] < 0, "customer_n"] = 0
        self.prompt_hours["prob"] = (
            self.prompt_hours["customer_n"] / self.prompt_hours["customer_n"].sum()
        )

    def prepar_prompt_games(self) -> None:
        # sample the games but leave the first in csv as the first there
        self.prompt_games[1:] = self.prompt_games[1:].sample(frac=1)
        # add the weights
        rng = np.linspace(0, 2, self.prompt_games["name"].shape[0])
        expon_curve = np.exp(-rng)
        self.prompt_games["weights"] = expon_curve / expon_curve.sum()

    def gen_staff(self) -> None:
        # basic info
        self.staff = pd.DataFrame(
            {
                "gender": np.random.choice(
                    ["M", "F"], size=self.config["staff_number"]
                ),
                "phone": self.random_helpers.gen_one_phone(
                    np.zeros(self.config["staff_number"])
                ),
                "to_date": self.random_helpers.gen_staff_to_date(),
            }
        )
        # details
        self.staff["city"] = np.full(self.staff.shape[0], "Wrocław")
        self.staff["from_date"] = self.random_helpers.gen_staff_form_date(self.staff)
        self.staff["first_name"] = self.random_helpers.gen_one_name(
            self.staff["gender"], "first"
        )
        self.staff["last_name"] = self.random_helpers.gen_one_name(
            self.staff["gender"], "last"
        )
        self.staff["email"] = self.random_helpers.gen_email(
            self.staff["first_name"], self.staff["last_name"]
        )
        self.staff["current_salary"] = self.random_helpers.gen_salary(self.staff)
        self.staff["is_manager"] = self.random_helpers.gen_manager_status(self.staff)
        self.staff["updated_at"] = self.random_helpers.gen_staff_update_time(self.staff)
        # indexing
        self.staff.sort_values(by=["updated_at"], inplace=True)
        self.staff = self.staff.reset_index(drop=True)
        self.staff["staff_id"] = self.staff.reset_index()["index"] + 1
        self.staff = self.staff.reindex(
            labels=[
                "staff_id",
                "first_name",
                "last_name",
                "phone",
                "email",
                "city",
                "current_salary",
                "is_manager",
                "gender",
                "from_date",
                "to_date",
                "updated_at",
            ],
            axis=1,
        )

    def gen_prompt_staff_shifts(self) -> None:
        # all the hour-day combinations
        hours = pd.DataFrame(
            {
                "hour": np.arange(
                    self.config["shop_open_hours"]["from"],
                    self.config["shop_open_hours"]["to"],
                )
            }
        )
        weekdays = pd.DataFrame({"weekday": np.arange(0, 7)})
        shifts = pd.merge(hours, weekdays, how="cross")
        # get the morning and afternoon shift hours
        morning_rows = shifts[
            (
                (
                    shifts["weekday"]
                    <= self.config["shop_open_hours"]["shift_mor_reg_ch"]
                )
                & (shifts["hour"] >= self.config["shop_open_hours"]["from"])
                & (shifts["hour"] < self.config["shop_open_hours"]["shift_mor_to_a"])
            )
            | (
                (shifts["weekday"] > self.config["shop_open_hours"]["shift_mor_reg_ch"])
                & (shifts["hour"] >= self.config["shop_open_hours"]["from"])
                & (shifts["hour"] < self.config["shop_open_hours"]["shift_mor_to_b"])
            )
        ]
        afternoon_rows = shifts[
            (
                (
                    shifts["weekday"]
                    <= self.config["shop_open_hours"]["shift_aft_reg_ch"]
                )
                & (shifts["hour"] >= self.config["shop_open_hours"]["shift_aft_from_a"])
                & (shifts["hour"] < self.config["shop_open_hours"]["to"])
            )
            | (
                (shifts["weekday"] > self.config["sh1op_open_hours"]["shift_aft_reg_ch"])
                & (shifts["hour"] >= self.config["shop_open_hours"]["shift_aft_from_b"])
                & (shifts["hour"] < self.config["shop_open_hours"]["to"])
            )
        ]
        # add the employees to each field
        afternoons = pd.merge(
            pd.DataFrame({"staff_id": self.config["staff_shifts"]["afternoon"]}),
            afternoon_rows,
            how="cross",
        )
        mornings = pd.merge(
            pd.DataFrame({"staff_id": self.config["staff_shifts"]["morning"]}),
            morning_rows,
            how="cross",
        )
        self.prompt_staff_shifts = pd.concat([mornings, afternoons]).reset_index(
            drop=True
        )

    def gen_realtionships(self) -> None:
        n = int(np.ceil(self.config["staff_number"] * self.config["relationships"]["ratio"]))
        staff_id = []
        staff_gender = []
        update = []
        current_staff = self.staff.loc[self.staff["current_salary"].isnull() == False]
        for _ in range(n):
            employee = np.random.choice(
                current_staff.staff_id.values,
                p=current_staff.current_salary.values,
            )
            staff_id.append(*employee)
            staff_gender.append(
                *current_staff["gender"]
                .loc[current_staff.staff_id == employee[0]]
                .values
            )
            update.append(
                Faker().date_between_dates(
                    pd.to_datetime(
                        current_staff.from_date.loc[
                            current_staff.staff_id == employee[0]
                        ].values[0]
                    ),
                    self.prompt_dates["date"].iloc[-1],
                )
                + pd.DateOffset(
                    hours=np.random.randint(
                        self.config["shop_open_hours"]["from"],
                        self.config["shop_open_hours"]["to"],
                    ),
                    minutes=np.random.randint(0, 60),
                    seconds=np.random.randint(0, 60),
                )
            )
        self.relationships = pd.DataFrame(
            {
                "staff_id": staff_id,
                "staff_gender": staff_gender,
                "dates_number": self.random_helpers.random_normal_bounded(
                    n=n,
                    loc=self.config["relationships"]["avg_dates_n"],
                    scale=self.config["relationships"]["std_dates_n"],
                    condition=0,
                ).astype(int),
                "updated_at": update,
            }
        )
        self.relationships.sort_values(by=["updated_at"], inplace=True)
        self.relationships = self.relationships.reset_index(drop=True)
        self.relationships["relationship_id"] = self.relationships.reset_index()["index"] + 1
        self.relationships["partner_id"] = self.relationships.reset_index()["index"] + 1
        self.relationships = self.relationships.reindex(
            labels=[
                "relationship_id",
                "staff_id",
                "staff_gender",
                "partner_id",
                "dates_number",
                "updated_at",
            ],
            axis=1,)
        

    def gen_partners(self) -> None:
        partner = self.relationships["partner_id"]
        staff_gender = self.relationships["staff_gender"].values
        gender = []
        weight = self.config["heterosexuals_ratio"]
        for el in staff_gender:
            if el == "M":
                gender.append(
                    np.random.choice(["M", "F"], weights=[1 - weight, weight])
                )
            elif el == "F":
                gender.append(
                    np.random.choice(["M", "F"], weights=[weight, 1 - weight])
                )

        self.partners = pd.DataFrame(
            {
                "partner_id": partner,
                "gender": gender,
                "updated_at": self.relationships["updated_at"],
            }
        )
        self.partners["name"] = self.random_helpers.gen_one_name(self.partners["gender"], mode="first")
        self.partners.sort_values(by=["updated_at"], inplace=True)
        self.partners = self.partners.reindex(
            labels=["partner_id", "name", "gender", "updated_at"], axis=1
        )
        self.relationships.drop(columns=["staff_gender"], inplace=True)
        self.partners =  self.partners.reset_index(drop=True)

    def gen_mock_customers(self) -> None:
        self.customers = pd.DataFrame(
            {"customer_id": [*range(1, self.config["customers_number"] + 1)]}
        )

    def gen_maintenance_expenses(self) -> None:
        self.maintenance_expenses = pd.DataFrame(
            {"date": [], "title": [], "amount": [], "type": [], "updated_at": []}
        )
        self.maintenance_expenses = pd.concat(
            [
                self.maintenance_expenses,
                self.random_helpers.gen_rent_expenses(),
                self.random_helpers.gen_energy_expenses(),
                self.random_helpers.gen_water_expenses(),
                self.random_helpers.gen_heat_expenses(),
                self.random_helpers.gen_salary_expenses(staff),
            ]
        )
        self.maintenance_expenses["updated_at"] = (
            self.maintenance_expenses["date"]
            + pd.DateOffset(
                hours=np.random.randint(
                    self.config["shop_open_hours"]["from"],
                    self.config["shop_open_hours"]["to"],
                ),
                minutes=np.random.randint(0, 60),
                seconds=np.random.randint(0, 60),
                n=self.maintenance_expenses.shape[0],
            ),
        )

        self.maintenance_expenses.sort_values(by=["updated_at"], inplace=True)
        self.maintenance_expenses = self.maintenance_expenses.reset_index(drop=True)
        self.maintenance_expenses["payment_id"] = self.maintenance_expenses.reset_index()["index"] + 1
        self.maintenance_expenses["invoice_id"] = self.maintenance_expenses.reset_index()["index"] + 1
        self.maintenance_expenses["spend_id"] = self.maintenance_expenses.reset_index()["index"] + 1
        self.maintenance_expenses = self.maintenance_expenses.reindex(
            [
                "spend_id",
                "title",
                "amount",
                "type",
                "date",
                "payment_id",
                "invoice_id",
                "updated_at",
            ],
            axis=1,
        )

    def gen_expense_types():
        df = pd.DataFrame(
            {
                "expenses_type": maintenance_expenses["type"],
                "updated_at": maintenance_expenses["updated_at"],
            }
        )
        df.drop_duplicates(subset=["expenses_type"], keep="last", inplace=True)
        df.sort_values(by=["updated_at"], inplace=True)
        df = df.reset_index(drop=True)
        df["expenses_type_id"] = df.reset_index()["index"] + 1
        df = df.reindex(["expenses_type_id", "expenses_type", "updated_at"], axis=1)
        return df

    def gen_expense_titles():
        df = pd.DataFrame(
            {
                "title": maintenance_expenses["title"],
                "expenses_type": maintenance_expenses["type"],
                "updated_at": maintenance_expenses["updated_at"],
            }
        )
        df.drop_duplicates(subset=["title"], keep="last", inplace=True)
        df = pd.merge(
            df,
            expense_types[["expenses_type_id", "expenses_type"]],
            how="left",
            on=["expenses_type"],
        )
        df.sort_values(by=["updated_at"], inplace=True)
        df = df.reset_index(drop=True)
        df["title_id"] = df.reset_index()["index"] + 1
        df = df.reindex(["title_id", "title", "expenses_type_id", "updated_at"], axis=1)
        return df

    def _gen_tournament_game():
        games = prompt_games.loc[
            prompt_games["tournament"] == "TAK", ["name", "type", "category"]
        ]
        tournament_games = pd.merge(
            games,
            prompt_tournaments,
            left_on=["type", "category"],
            right_on=["type", "category"],
            suffixes=["_game", "_tournament"],
        )
        tournament_games = tournament_games[["name_game", "name_tournament"]]
        return tournament_games

    def _gen_staff_handler():
        #
        available_staff = prompt_staff_shifts.loc[
            (prompt_staff_shifts["weekday"] == config["event_info"]["weekday"])
            & (prompt_staff_shifts["hour"] >= config["event_info"]["hour"])
        ]["staff_id"].unique()

        return np.random.choice(available_staff)

    def count_matches(x):
        total = 0
        while x >= 0:
            total += 2**x
            x -= 1
        return total

    def gen_tournaments():
        dates = pd.DataFrame(
            prompt_dates.loc[
                prompt_dates["weekday"] == config["event_info"]["weekday"], "date"
            ].iloc[
                config["event_info"]["start_offset_weeks"] :: config["event_info"][
                    "period_weeks"
                ]
            ]
        ).reset_index()["date"]
        tournament = _gen_tournament_game()
        tournament = tournament.sample(
            dates.shape[0], replace=False, ignore_index=True
        )  # cannot be the same row
        tree_levels_number = np.random.randint(
            self.config["tournament_tree_params"]["min"],
            self.config["tournament_tree_params"]["max"] + 1,
            size=dates.shape[0],
        )
        matches = map(lambda x: count_matches(x), tree_levels_number)
        df = pd.DataFrame(
            {
                "name": tournament["name_tournament"],
                "game": tournament["name_game"],
                "start_time": dates
                + datetime.timedelta(hours=self.config["event_info"]["hour"]),
                "matches": matches,
                "tree_levels": tree_levels_number,
                "fee": np.full(dates.shape[0], self.config["event_info"]["fee"]),
                "sign_up_deadline": dates
                - datetime.timedelta(
                    days=self.config["event_info"]["deadline_offset_days"]
                ),
                "staff_id": [_gen_staff_handler() for _ in range(dates.shape[0])],
                "expenses": np.round(
                    self.config["exponses_params"]["mean"]
                    + np.random.gamma(
                        shape=self.config["exponses_params"]["shape"],
                        scale=self.config["exponses_params"]["scale"],
                        size=dates.shape[0],
                    ),
                    2,
                ),
                "updated_at": dates
                + datetime.timedelta(hours=self.config["event_info"]["hour"]),
            }
        )
        df.sort_values(by=["updated_at"], inplace=True)
        df = df.reset_index(drop=True)
        df["tournament_id"] = df.reset_index()["index"] + 1
        df["invoice_id"] = df["tournament_id"]
        df = df.reindex(
            [
                "tournament_id",
                "name",
                "game",
                "start_time",
                "matches",
                "tree_levels",
                "fee",
                "sign_up_deadline",
                "staff_id",
                "expenses",
                "invoice_id",
                "updated_at",
            ],
            axis=1,
        )
        return df

    def _sign_up_date_generator(deadline):
        deadline = pd.to_datetime(deadline)
        date = pd.to_datetime(
            prompt_dates["date"]
            .loc[
                (prompt_dates["date"] < deadline)
                & (
                    prompt_dates["date"]
                    > deadline
                    - pd.DateOffset(
                        days=self.config["event_info"]["can_sign_up_offset_days"]
                    )
                )
            ]
            .sample(1, ignore_index=True)
            .values[0]
        )
        date += pd.DateOffset(
            hours=np.random.randint(
                self.config["shop_open_hours"]["from"],
                self.config["shop_open_hours"]["to"],
            ),
            minutes=np.random.randint(0, 60),
            seconds=np.random.randint(0, 60),
            n=df.shape[0],
        )
        return date

    def gen_participations():
        # participants number
        players = pd.merge(
            tournaments[
                ["game", "tree_levels", "tournament_id", "fee", "sign_up_deadline"]
            ],
            prompt_games[["name", "participants_number"]],
            left_on=["game"],
            right_on=["name"],
            how="left",
        )
        players["participants_number"] = players["participants_number"].astype("int")
        players_number = players["participants_number"] * (2 ** players["tree_levels"])
        players["players"] = players_number

        # customer_id and place
        participants = map(
            lambda x: customers["customer_id"]
            .sample(x, replace=False, ignore_index=True)
            .values,
            players_number,
        )
        players["place"] = players["players"].apply(lambda x: [*range(1, x + 1)])
        players["customer_id"] = list(participants)

        df = players[
            ["tournament_id", "customer_id", "fee", "sign_up_deadline", "place"]
        ]
        df = df.explode(["customer_id", "place"], ignore_index=True)
        df["sign_up_date"] = df["sign_up_deadline"].apply(_sign_up_date_generator)
        df["updated_at"] = df["sign_up_date"].copy()
        df.sort_values(by=["updated_at"], inplace=True)
        df = df.reset_index(drop=True)
        df["particip_id"] = df.reset_index()["index"] + 1
        df["invoice_id"] = df.reset_index()["index"] + 1
        df = df.reindex(
            [
                "particip_id",
                "tournament_id",
                "customer_id",
                "place",
                "sign_up_date",
                "fee",
                "invoice_id",
                "updated_at",
            ],
            axis=1,
        )
        return df

    v_repeat = np.vectorize(lambda date, volume: itertools.repeat(date, int(volume)))

    def _gen_sell_inventory() -> pd.DataFrame:
        # evaluate a total game number
        total_games_n = np.round(
            prompt_dates["volume_sales"].sum()
            * (config["inventory_multiplier"] + np.random.exponential())
        )
        game_counts = list(map(round, prompt_games["weights"] * total_games_n))
        # repeat the games
        games_gener = itertools.chain(*v_repeat(prompt_games["name"], game_counts))
        games = np.array(list(games_gener))
        # add the basic details to the data frame
        s_inventory = pd.DataFrame(
            {
                "game": np.random.permutation(games),
                "destination": np.full(games.size, "S"),
                "active": np.full(games.size, True),
            }
        )
        # add the prices from the prompt table
        s_inventory = (
            pd.merge(
                s_inventory,
                prompt_games[["name", "purchase"]],
                left_on="game",
                right_on="name",
                how="inner",
            )
            .rename(columns={"purchase": "price"})
            .drop(columns="name")
        )
        # add the procurment prices as some fraction of the standard one
        s_inventory["purchase_payment"] = (
            s_inventory["price"] * config["bulk_ratio"]
        ).round(2)
        s_inventory = s_inventory.sample(n=s_inventory.shape[0]).reset_index(drop=True)
        # get the delivery dates
        delivery_count = (
            config["avg_supply_yearly_rate"] * config["shop_lifetime_years"]
        )
        delivery_dates = prompt_dates["date"][
            :: int(prompt_dates.shape[0] / delivery_count)
        ].copy()
        delivery_dates += datetime.timedelta(
            hours=self.config["shop_open_hours"]["from"]
        )
        # the final grouping
        group_dates = np.repeat(
            delivery_dates.to_numpy(), np.ceil(total_games_n / delivery_count)
        )[: sum(game_counts)]
        s_inventory = s_inventory.reset_index(drop=True)
        s_inventory["delivery_date"] = group_dates
        return s_inventory

    def _gen_rent_inventory() -> pd.DataFrame:
        total_games_n = config["rental_games_n"]
        game_counts = list(map(round, prompt_games["weights"] * total_games_n))
        # repeat the games
        games_gener = itertools.chain(*v_repeat(prompt_games["name"], game_counts))
        games = np.array(list(games_gener))
        # active statuses
        active_status = np.full(games.size, True)
        active_status[: config["inactive_rental_games"]] = False
        active_status = np.random.permutation(active_status)
        # add the basic details to the data frame
        r_inventory = pd.DataFrame(
            {
                "game": np.random.permutation(games),
                "destination": np.full(games.size, "R"),
                "active": active_status,
            }
        )
        # add the prices from the prompt table; temporarily prices are full
        r_inventory = (
            pd.merge(
                r_inventory,
                prompt_games[["name", "purchase"]],
                left_on="game",
                right_on="name",
                how="inner",
            )
            .rename(columns={"purchase": "price"})
            .drop(columns="name")
        )
        # add the procurment prices as some fraction of the standard one
        r_inventory["purchase_payment"] = (
            r_inventory["price"] * config["bulk_ratio"]
        ).round(2)
        # the delivery dates
        r_inventory["delivery_date"] = prompt_dates["date"].iloc[
            0
        ] + datetime.timedelta(hours=self.config["shop_open_hours"]["from"])
        r_inventory["price"] = (
            r_inventory["price"] * config["rental_price_ratio"]
        ).round(2)
        return r_inventory

    def _gen_tournament_inventory() -> pd.DataFrame:
        # find the required game counts
        game_counts_tournaments = (
            tournaments[["game", "tree_levels"]]
            .groupby("game")
            .max()
            .apply(lambda x: 2**x)
        ).reset_index()
        # repeat the games
        games_gener = itertools.chain(
            *v_repeat(
                game_counts_tournaments["game"], game_counts_tournaments["tree_levels"]
            )
        )
        games = np.array(list(games_gener))

        # add the basic details to the data frame
        t_inventory = pd.DataFrame(
            {
                "game": np.random.permutation(games),
                "destination": np.full(games.size, "T"),
                "active": np.full(games.size, True),
            }
        )
        t_inventory = (
            pd.merge(
                t_inventory,
                prompt_games[["name", "purchase"]],
                left_on="game",
                right_on="name",
                how="inner",
            )
            .rename(columns={"purchase": "price"})
            .drop(columns="name")
        )
        # add the procurment prices as some fraction of the standard one
        t_inventory["purchase_payment"] = (
            t_inventory["price"] * config["bulk_ratio"]
        ).round(2)
        # the delivery dates
        t_inventory["delivery_date"] = prompt_dates["date"].iloc[
            0
        ] + datetime.timedelta(hours=self.config["shop_open_hours"]["from"])
        t_inventory["price"] = np.nan
        return t_inventory

    def gen_inventory():
        # concat the parts
        inventory = pd.concat(
            [_gen_sell_inventory(), _gen_rent_inventory(), _gen_tournament_inventory()]
        )
        # add updated at value
        inventory["updated_at"] = inventory["delivery_date"]
        inventory = inventory.sort_values(by=["updated_at"])
        # index it
        inventory = inventory.reset_index(drop=True)
        inventory["inventory_id"] = inventory.reset_index()["index"] + 1
        # add invoice numbers
        uniq_dates = np.sort(np.unique(inventory["delivery_date"]))
        invoice_translator = dict(zip(uniq_dates, np.arange(uniq_dates.size) + 1))
        inventory["invoice_id"] = inventory["delivery_date"].map(invoice_translator)
        # export it
        inventory = inventory.reindex(
            [
                "inventory_id",
                "game",
                "destination",
                "price",
                "active",
                "purchase_payment",
                "invoice_id",
                "delivery_date",
                "updated_at",
            ],
            axis=1,
        )
        return inventory

    def gen_game_prices():
        df = inventory.drop_duplicates(
            subset=["price"], keep="last", ignore_index=True
        )[["price", "updated_at"]]
        df.rename(columns={"price": "current_price"}, inplace=True)
        df = df.sort_values(["updated_at"])
        # set id
        df = df.reset_index(drop=True)
        df["price_id"] = df.reset_index()["index"] + 1
        df = df.reindex(["price_id", "current_price", "updated_at"], axis=1)
        return df

    def gen_sales():
        v_repeat = np.vectorize(
            lambda date, volume: itertools.repeat(date, int(volume))
        )
        v_timedelta = np.vectorize(
            lambda h, m, s: datetime.timedelta(
                hours=int(h), minutes=int(m), seconds=int(s)
            )
        )

        @np.vectorize
        def v_get_staff_id(timestamp):
            available_staff = prompt_staff_shifts[
                (prompt_staff_shifts["weekday"] == timestamp.weekday())
                & (prompt_staff_shifts["hour"] == timestamp.hour)
            ]["staff_id"]
            return np.random.choice(available_staff)

        # get a list of dates for each customer
        dates_gener = itertools.chain(
            *v_repeat(prompt_dates["date"], prompt_dates["volume_sales"])
        )
        dates = np.array(list(dates_gener))
        # add random time to the date
        hours = np.array(
            np.random.choice(
                prompt_hours["hour"], p=prompt_hours["prob"], size=dates.size
            )
        )
        minutes = np.random.randint(0, 60, size=dates.size)
        seconds = np.random.randint(0, 60, size=dates.size)
        timestamps = dates + v_timedelta(hours, minutes, seconds)
        timestamps.sort()
        # staff ids
        staff = v_get_staff_id(timestamps)
        # how many at once are bought
        pcs = np.random.choice(
            list(config["customer_pcs_probas"].keys()),
            p=list(config["customer_pcs_probas"].values()),
            size=dates.size,
        ).astype(int)
        # make a data frame and add invoices as ix
        sales = pd.DataFrame({"date": timestamps, "staff_id": staff, "pcs": pcs})
        sales = sales.reset_index().rename(columns={"index": "invoice"})
        # additional rows when the pieces number is larger than one
        for pcs_n in config["customer_pcs_probas"].keys():
            selection = sales[sales["pcs"] == int(pcs_n)]
            sales = pd.concat([sales] + [selection] * (int(pcs_n) - 1))
        sales = sales.reset_index(drop=True).drop("pcs", axis="columns")
        # pre-filter the inventory table
        global inventory  # DELETE THAT!!!!!!!!!!!
        sales_inventory = inventory[inventory["destination"] == "S"]
        sales = pd.concat(
            [
                sales,
                sales_inventory.iloc[: sales.shape[0]].reset_index()[
                    ["inventory_id", "price", "delivery_date"]
                ],
            ],
            axis=1,
        )
        sales = sales[~(sales["date"] < sales["delivery_date"])]
        sales = sales.drop(columns=["delivery_date"])
        inventory.loc[sales["inventory_id"], "active"] = False

        # other details
        sales["updated_at"] = sales["date"]
        sales["return_oper"] = False
        # export
        sales.sort_values("updated_at", inplace=True)
        # fix
        sales = sales.reset_index(drop=True)
        sales["sale_id"] = sales.reset_index()["index"] + 1
        sales = sales.reindex(
            [
                "sale_id",
                "inventory_id",
                "staff_id",
                "price",
                "date",
                "invoice",
                "return_oper",
                "updated_at",
            ],
            axis=1,
        )
        return sales

    def gen_rental():
        rental_date = []
        return_dates = []
        customer = []
        price = []
        staff = []
        inventory_ids = []
        rate = []
        update = []
        penalty = []
        invoice = []
        penalty_invoice = []

        @np.vectorize
        def v_get_staff_id(timestamp):
            available_staff = prompt_staff_shifts[
                (prompt_staff_shifts["weekday"] == timestamp.weekday())
                & (prompt_staff_shifts["hour"] == timestamp.hour)
            ]["staff_id"]
            return np.random.choice(available_staff)

        def v_proper_return_date(timestamp, date):
            if (timestamp.day == date.day) & (timestamp.hour < date.hour):
                return timestamp.replace(hour=config["shop_open_hours"]["from"])
            elif timestamp.hour < config["shop_open_hours"]["from"]:
                return timestamp.replace(hour=config["shop_open_hours"]["from"])
            elif timestamp.hour >= config["shop_open_hours"]["to"]:
                return timestamp.replace(hour=config["shop_open_hours"]["to"] - 1)
            else:
                return timestamp

        for j in range(prompt_dates["date"].shape[0]):
            for i in range(int(prompt_dates["volume_rental"][j])):
                hour = np.random.choice(prompt_hours["hour"], p=prompt_hours["prob"])
                date = prompt_dates["date"][j] + datetime.timedelta(
                    hours=int(hour),
                    minutes=np.random.randint(0, 60),
                    seconds=np.random.randint(0, 60),
                )
                game = np.random.choice(prompt_games["name"], p=prompt_games["weights"])
                staff_id = v_get_staff_id(date)
                holding_time = np.random.gamma(
                    self.config["holding_time_params"]["shape"],
                    scale=self.config["holding_time_params"]["scale"],
                )
                return_date_t = prompt_dates["date"][j] + datetime.timedelta(
                    days=int(holding_time),
                    hours=round(abs(holding_time) % 1 * 24, 2),
                    minutes=np.random.randint(0, 60),
                    seconds=np.random.randint(0, 60),
                )
                return_date = v_proper_return_date(return_date_t, date)

                mask = (
                    (inventory["game"] == game)
                    & (inventory["delivery_date"] < date)
                    & (inventory["destination"] == "R")
                    & (inventory["active"] == True)
                )
                if mask.any():
                    customer.append(int(np.random.choice(customers["customer_id"])))
                    price.append(inventory["price"].loc[mask.idxmax()])
                    rental_date.append(date)
                    staff.append(staff_id)
                    game_inventory_id = inventory["inventory_id"].loc[mask.idxmax()]
                    inventory_ids.append(game_inventory_id)
                    invoice.append(f"{i}{j}")
                    if return_date > datetime.datetime.today():
                        return_dates.append(np.nan)
                        update.append(date)
                        inventory.loc[mask.idxmax(), "active"] = False
                        penalty.append(np.nan)
                        penalty_invoice.append(np.nan)
                    else:
                        return_dates.append(return_date)
                        update.append(return_date)
                        delta = return_date - date
                        if delta.days > config["rental_allowed_days"]:
                            penalty.append(
                                (
                                    (
                                        inventory[
                                            inventory["inventory_id"]
                                            == game_inventory_id
                                        ]["price"]
                                    )
                                    * config["penalty_ratio"]
                                )
                                .to_numpy()[0]
                                .round(2)
                                * delta.days
                            )
                            penalty_invoice.append(f"P{i}_{j}")
                        else:
                            penalty.append(np.nan)
                            penalty_invoice.append(np.nan)
                    rate.append(np.random.randint(1, 11))

        df = pd.DataFrame(
            {
                "inventory_id": inventory_ids,
                "customer_id": customer,
                "rental_date": rental_date,
                "return_date": return_dates,
                "staff_id": staff,
                "price": price,
                "invoice": invoice,
                "penalty_payment": penalty,
                "penalty_invoice": penalty_invoice,
                "rate": rate,
                "updated_at": update,
            }
        )
        df.sort_values("updated_at", inplace=True)
        df = df.reset_index(drop=True)
        df["rental_id"] = df.reset_index()["index"] + 1
        df = df.reindex(
            [
                "rental_id",
                "inventory_id",
                "customer_id",
                "rental_date",
                "return_date",
                "staff_id",
                "price",
                "invoice",
                "penalty_payment",
                "penalty_invoice",
                "rate",
                "updated_at",
            ],
            axis=1,
        )
        return df

    def gen_games():
        update = inventory[["game", "delivery_date"]].groupby(["game"]).min()
        games = pd.merge(prompt_games, update, left_on=["name"], right_on=["game"])
        games = games[
            ["name", "description", "category", "type", "tournament", "delivery_date"]
        ]
        games.rename(
            columns={
                "name": "title",
                "description": "description",
                "category": "category",
                "type": "type",
                "tournament": "competitivity",
                "delivery_date": "updated_at",
            },
            inplace=True,
        )
        games["competitivity"] = games["competitivity"].apply(
            lambda x: True if x == "TAK" else False
        )
        games.sort_values(["updated_at"], inplace=True)
        games = games.reset_index(drop=True)
        games["game_id"] = games.reset_index()["index"] + 1
        games = games.reindex(
            [
                "game_id",
                "title",
                "description",
                "category",
                "type",
                "competitivity",
                "updated_at",
            ],
            axis=1,
        )
        return games

    def gen_game_categories():
        df = games[["category", "updated_at"]].drop_duplicates("category", keep="first")
        df.rename(columns={"category": "game_category"}, inplace=True)
        df = df.reset_index(drop=True)
        df["category_id"] = df.reset_index()["index"] + 1
        df = df.reindex(["category_id", "game_category", "updated_at"], axis=1)
        return df

    def gen_game_types():
        df = games[["type", "updated_at"]].drop_duplicates("type", keep="first")
        df.rename(columns={"type": "game_type"}, inplace=True)
        df = df.reset_index(drop=True)
        df["type_id"] = df.reset_index()["index"] + 1
        df = df.reindex(["type_id", "game_type", "updated_at"], axis=1)
        return df

    def _customers_updated():
        global customers
        active_customers = pd.concat(
            [
                rental[["customer_id", "updated_at"]],
                participations[["customer_id", "updated_at"]],
            ],
            ignore_index=True,
        )
        customers = pd.merge(
            customers,
            active_customers.groupby(by="customer_id").min(),
            on="customer_id",
        )
        customers.sort_values("updated_at", inplace=True)
        customers.reset_index(drop=True, inplace=True)
        return customers

    def gen_real_customers():
        global customers
        customers = _customers_updated()
        customers["gender"] = np.random.choice(["M", "F"], size=customers.shape[0])
        customers["phone"] = gen_one_phone(np.zeros(customers.shape[0]))
        customers["city"] = np.random.choice(
            prompt_cities["city"], p=prompt_cities["prob"], size=customers.shape[0]
        )
        customers["first_name"] = gen_one_name(customers["gender"], "first")
        customers["last_name"] = gen_one_name(customers["gender"], "last")
        customers["email"] = gen_email(customers["first_name"], customers["last_name"])
        customers["previous_customer_id"] = customers["customer_id"]
        customers["customer_id"] = customers.reset_index()["index"] + 1
        customers = customers.reindex(
            columns=[
                "customer_id",
                "previous_customer_id",
                "first_name",
                "last_name",
                "phone",
                "email",
                "city",
                "updated_at",
            ]
        )
        return customers

    def gen_cities():
        merged_df = pd.concat([customers, staff], ignore_index=True)
        merged_df.sort_values(["updated_at"], inplace=True)
        merged_df.drop_duplicates(subset=["city"], keep="first", inplace=True)
        city = pd.DataFrame(
            {
                "city": merged_df["city"],
                "updated_at": merged_df["updated_at"],
            }
        )
        city = city.reset_index(drop=True)
        city["city_id"] = city.reset_index()["index"] + 1
        city = city.reindex(["city_id", "city", "updated_at"], axis=1)
        return city

    def _gen_working_payments():
        # inventory
        df_inv = inventory[["purchase_payment", "invoice_id", "updated_at"]].rename(
            columns={
                "purchase_payment": "amount",
                "invoice_id": "invoice",
                "updated_at": "date",
            }
        )
        df_inv["invoice"] = "I" + df_inv["invoice"].astype(str)
        df_inv["amount"] = -df_inv["amount"]
        # sales
        df_sales = sales[["price", "invoice", "date"]].rename(
            columns={"price": "amount"}
        )
        df_sales["invoice"] = "S" + df_sales["invoice"].astype(str)
        # rent
        df_rent = rental[["price", "invoice", "rental_date"]].rename(
            columns={"price": "amount", "rental_date": "date"}
        )
        df_rent["invoice"] = "R" + df_rent["invoice"].astype(str)
        # rent penalty
        df_rent_penalty = (
            rental[["penalty_payment", "penalty_invoice", "return_date"]]
            .dropna()
            .rename(
                columns={
                    "penalty_payment": "amount",
                    "penalty_invoice": "invoice",
                    "return_date": "date",
                }
            )
        )
        df_rent_penalty["invoice"] = "R" + df_rent_penalty["invoice"].astype(str)
        # expenses
        df_exp = maintenance_expenses[["amount", "invoice_id", "updated_at"]].rename(
            columns={"updated_at": "date", "invoice_id": "invoice"}
        )
        df_exp["invoice"] = "ME" + df_exp["invoice"].astype(str)
        df_exp["amount"] = -df_exp["amount"]
        # tour
        df_tour = tournaments[["expenses", "invoice_id", "updated_at"]].rename(
            columns={
                "expenses": "amount",
                "invoice_id": "invoice",
                "updated_at": "date",
            }
        )
        df_tour["invoice"] = "T" + df_tour["invoice"].astype(str)
        df_tour["amount"] = -df_tour["amount"]
        # participations
        df_part = participations[["fee", "invoice_id", "updated_at"]].rename(
            columns={"fee": "amount", "invoice_id": "invoice", "updated_at": "date"}
        )
        df_part["invoice"] = "P" + df_part["invoice"].astype(str)
        df = pd.concat(
            [df_inv, df_sales, df_rent, df_rent_penalty, df_exp, df_tour, df_part],
            ignore_index=True,
        )
        return df

    def gen_invoices():
        df = working_payments[["invoice", "date"]]
        df = df.drop_duplicates("invoice")
        df["updated_at"] = df.loc[:, "date"]
        df = df.reset_index(drop=True)
        df["invoice_id"] = df.reset_index()["index"] + 1
        df = df.reindex(["invoice_id", "invoice", "date", "updated_at"], axis=1)
        return df

    def gen_payments():
        df = pd.merge(working_payments, invoices, on="invoice")[
            ["amount", "invoice_id", "updated_at"]
        ]
        df = df.reset_index(drop=True)
        df["payment_id"] = df.reset_index()["index"] + 1
        df = df.reindex(["payment_id", "amount", "invoice_id", "updated_at"], axis=1)
        return df

    def customers_cleaning():
        global customers
        customers["city"] = customers["city"].map(
            dict(zip(city["city"], city["city_id"]))
        )
        customers = customers.rename(columns={"city": "city_id"})
        customers.drop(columns=["previous_customer_id"], inplace=True)

    def participations_cleaning():
        global participations
        participations.rename(columns={"fee": "fee_payment_id"}, inplace=True)
        participations["customer_id"] = participations["customer_id"].map(
            dict(zip(customers["previous_customer_id"], customers["customer_id"]))
        )
        participations["fee_payment_id"] = participations["updated_at"].map(
            dict(zip(payments["updated_at"], payments["payment_id"]))
        )
        participations.drop(columns=["invoice_id"], inplace=True)

    def tournaments_cleaning():
        global tournaments
        tournaments["game"] = tournaments["game"].map(
            dict(zip(games["title"], games["game_id"]))
        )
        tournaments = tournaments.rename(
            columns={"game": "game_id", "expenses": "expenses_payments_id"}
        )
        tournaments["expenses_payments_id"] = tournaments["updated_at"].map(
            dict(zip(payments["updated_at"], payments["payment_id"]))
        )
        tournaments.drop(columns=["tree_levels", "invoice_id"], inplace=True)

    def rental_cleaning():
        global rental
        rental["customer_id"] = rental["customer_id"].map(
            dict(zip(customers["previous_customer_id"], customers["customer_id"]))
        )
        rental = rental.rename(
            columns={"penalty_payment": "penalty_payment_id", "price": "payment_id"}
        )
        rental.drop(columns=["invoice", "penalty_invoice"], inplace=True)

    def inventory_cleaning():
        global inventory
        inventory["game"] = inventory["game"].map(
            dict(zip(games["title"], games["game_id"]))
        )
        inventory = inventory.rename(
            columns={
                "game": "game_id",
                "price": "price_id",
                "purchase_payment": "purchase_payment_id",
            }
        )
        inventory["purchase_payment_id"] = inventory["updated_at"].map(
            dict(zip(payments["updated_at"], payments["payment_id"]))
        )
        inventory["price_id"] = inventory["price_id"].map(
            dict(zip(game_prices["current_price"], game_prices["price_id"]))
        )
        inventory.drop(columns=["invoice_id"], inplace=True)

    def staff_cleaning():
        global staff
        temp = dict(zip(city["city"], city["city_id"]))
        staff["city"] = staff["city"].map(temp)
        staff.rename(columns={"city": "city_id"}, inplace=True)

    def invoices_cleaning():
        global invoices
        invoices.drop(columns=["invoice"], inplace=True)

    def maintenance_expenses_cleaning():
        global maintenance_expenses
        maintenance_expenses["title"] = maintenance_expenses["title"].map(
            dict(zip(expense_titles["title"], expense_titles["title_id"]))
        )
        maintenance_expenses = maintenance_expenses.drop(
            columns=["invoice_id", "amount", "type"]
        )
        maintenance_expenses = maintenance_expenses.rename(
            columns={"title": "title_id"}
        )
        maintenance_expenses["payment_id"] = maintenance_expenses["updated_at"].map(
            dict(zip(payments["updated_at"], payments["payment_id"]))
        )
        maintenance_expenses = maintenance_expenses.reindex(
            ["spend_id", "title_id", "payment_id", "date", "updated_at"], axis=1
        )

    def sales_cleaning():
        global sales
        sales = sales.rename(columns={"price": "payment_id"})
        sales["payment_id"] = sales["date"].map(
            dict(zip(payments["updated_at"], payments["payment_id"]))
        )
        sales.drop(columns=["invoice"], inplace=True)

    def games_cleaning():
        global games
        games["category"] = games["category"].map(
            dict(zip(game_categories["game_category"], game_categories["category_id"]))
        )
        games["type"] = games["type"].map(
            dict(zip(game_types["game_type"], game_types["type_id"]))
        )
        games = games.rename(columns={"category": "category_id", "type": "type_id"})

    def prepare_data(self):
        self.read_prompts()
        self.gen_prompt_dates()
        self.gen_prompt_hours()
        self.prepar_prompt_games()
        self._assign_random_helpers()
        self.gen_staff()
        self.gen_prompt_staff_shifts()
        self.gen_realtionships()
        self.gen_partners()
        self.gen_mock_customers()
        self.gen_maintenance_expenses()
        self.gen_expense_types()
        self.gen_expense_titles()
        self.gen_tournaments()
        self.gen_participations()
        self.gen_inventory()
        self.gen_game_prices()
        self.gen_sales()
        self.gen_rental()
        self.gen_games()
        self.gen_game_categories()
        self.gen_game_types()
        self.gen_real_customers()
        self.gen_cities()
        self._gen_working_payments()
        self.gen_invoices()
        self.gen_payments()
        self.participations_cleaning()
        self.tournaments_cleaning()
        self.rental_cleaning()
        self.customers_cleaning()
        self.inventory_cleaning()
        self.staff_cleaning()
        self.invoices_cleaning()
        self.maintenance_expenses_cleaning()
        self.sales_cleaning()
        self.games_cleaning()

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
