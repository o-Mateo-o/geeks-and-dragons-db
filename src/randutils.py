"""Helper functions for data generation."""

import datetime
import itertools

import numpy as np
import numpy.typing as npt
import pandas as pd
from unidecode import unidecode_expect_ascii


class RandomHelpers:
    def __init__(self, config: dict, prompts: dict) -> None:
        self.config = config
        self.prompts = prompts
        self.phone_base = []
        self.email_base = []

    def gen_one_phone(self, *args) -> str:
        def _scalar_fun(*args):
            while True:
                # get the prefix and the rest of digits
                digits = [
                    np.random.choice(self.config["phone_num_prefixes"]),
                    *np.random.randint(0, 10, size=7),
                ]
                # concat the digits
                phone = "".join(map(str, digits))
                if not phone in self.phone_base:
                    break
            self.phone_base.append(phone)
            return phone

        return np.vectorize(_scalar_fun)(*args)

    def gen_one_name(self, gender: str, mode: str) -> str:
        def _scalar_fun(gender: str, mode: str):
            # first or last name colname mode
            if mode == "first":
                col = "first_name"
                dfs = {
                    "M": self.prompts["prompt_first_names_males"],
                    "F": self.prompts["prompt_first_names_females"],
                }
            elif mode == "last":
                col = "last_name"
                dfs = {
                    "M": self.prompts["prompt_last_names_males"],
                    "F": self.prompts["prompt_last_names_females"],
                }
            else:
                raise ValueError(f"Cannot generate a name in {mode} mode")
            # random name based on gender and stats
            df = dfs[gender]
            return np.random.choice(df[col], p=df["prob"])

        return np.vectorize(_scalar_fun)(gender, mode)

    def gen_email(self, first_name: str, last_name: str) -> str:
        def _scalar_fun(first_name: str, last_name: str):
            # join the names and cleanse it
            raw_name = f"{first_name.lower()}.{last_name.lower()}"
            cleansed_name = unidecode_expect_ascii(raw_name)
            # initially do not add the number after the name
            number = ""
            while True:
                # concat all the elements
                domain = np.random.choice(self.prompts["prompt_emails"]["domain"])
                email = f"{cleansed_name}{number}@{domain}"
                # in the second iteration add the number
                number = np.random.randint(0, 10)
                if not email in self.email_base:
                    break
            self.email_base.append(email)
            return email

        return np.vectorize(_scalar_fun)(first_name, last_name)

    def gen_staff_to_date(self) -> npt.NDArray:
        # NULL fill
        dates = np.zeros(self.config["staff_number"], dtype=pd.Timestamp)
        dates[:] = np.nan
        # find the constants
        some_employee_ix = -2
        # fire him
        dates[some_employee_ix] = np.random.choice(
            self.prompts["prompt_dates"]["date"].iloc[90:-90]
        )
        return dates

    def gen_staff_from_date(self, staff: pd.DataFrame) -> npt.NDArray:
        # hire all of them
        dates = np.zeros(self.config["staff_number"], dtype=np.object_)
        dates[:] = self.prompts["prompt_dates"]["date"].iloc[0]
        # hire one with a time shift
        some_employee_ix = -1
        ones_end_date = (
            staff["to_date"].loc[staff["to_date"].isnull() == False].values[0]
        )
        dates[some_employee_ix] = pd.Timestamp(ones_end_date) + datetime.timedelta(
            days=30
        )
        return dates

    def gen_staff_update_time(self, staff: pd.DataFrame):
        df_date = staff[["to_date", "from_date"]]
        return df_date.max(axis=1, skipna=True, numeric_only=False).apply(
            lambda date: date
            + pd.DateOffset(
                hours=np.random.randint(8, 20),
                minutes=np.random.randint(0, 60),
                seconds=np.random.randint(0, 60),
            )
        )

    def gen_salary(self, staff: pd.DataFrame) -> npt.NDArray:
        # over the base salary
        salaries = np.random.exponential(
            scale=self.config["salary_settings"]["exp_scale"],
            size=staff.shape[0],
        )
        # add the base
        salaries += self.config["salary_settings"]["minimal"]
        # round it
        salaries = salaries.round(2)
        # remove the salary for the fired ones
        ix = staff.loc[staff["to_date"].isnull() == False]
        salaries[ix.index] = np.nan
        return salaries

    def gen_manager_status(self, staff: pd.DataFrame) -> npt.NDArray:
        # on entry no managers
        status = np.full(staff.shape[0], False)
        # the one who has the greatest salary becoms a manager
        ix = staff.loc[staff["current_salary"] == staff["current_salary"].max()]
        status[ix.index] = True
        return status

    @staticmethod
    def random_normal_bounded(n, loc, scale, condition, round_d=0):
        # norm rvs with minimum value condition
        arr = np.random.normal(scale=scale, loc=loc, size=n)
        mask = arr <= condition
        arr[mask] = condition
        return arr.round(round_d)

    def gen_expenses_dates(self):
        base = pd.DataFrame(
            self.prompts["prompt_dates"].loc[
                (
                    self.prompts["prompt_dates"]["date"].dt.day
                    == self.config["payment_day"]
                )
                | (
                    self.prompts["prompt_dates"]["date"].dt.day
                    == self.config["payment_day"] + 1
                ),
                "date",
            ]
        )
        base["flag"] = base["date"].dt.to_period("M")
        base.drop_duplicates(["flag"], keep="first", inplace=True)
        base = base.reset_index()
        return base["date"]

    def gen_rent_expenses(self):
        date_df = self.prompts["prompt_dates"].loc[
            self.prompts["prompt_dates"]["date"].dt.day == self.config["payment_day"],
            "date",
        ]
        title = date_df.dt.month_name(locale="pl_PL").apply(
            lambda x: "CZYNSZ " + str(x).upper()
        )
        df = pd.DataFrame(
            {
                "date": date_df,
                "title": title,
                "amount": np.full(
                    date_df.shape[0], self.config["maintenance"]["venue_rent"]
                ),
                "type": np.full(date_df.shape[0], "CZYNSZ"),
            }
        )
        return df

    def gen_energy_expenses(self):
        date_df = self.prompts["prompt_dates"].loc[
            self.prompts["prompt_dates"]["date"].dt.day == self.config["payment_day"],
            "date",
        ]
        title = date_df.dt.month_name(locale="pl_PL").apply(
            lambda x: "ENERGIA ELEKTRYCZNA " + str(x).upper()
        )
        df = pd.DataFrame(
            {
                "date": date_df,
                "title": title,
                "amount": self.random_normal_bounded(
                    n=date_df.shape[0],
                    loc=self.config["maintenance"]["energy_loc"],
                    scale=self.config["maintenance"]["energy_scale"],
                    condition=self.config["maintenance"]["energy_min"],
                    round_d=2,
                ),
                "type": np.full(date_df.shape[0], "MEDIA"),
            }
        )
        return df

    def gen_water_expenses(self):
        date_df = self.prompts["prompt_dates"].loc[
            self.prompts["prompt_dates"]["date"].dt.day == self.config["payment_day"],
            "date",
        ]
        title = date_df.dt.month_name(locale="pl_PL").apply(
            lambda x: "WODA " + str(x).upper()
        )
        df = pd.DataFrame(
            {
                "date": date_df,
                "title": title,
                "amount": self.random_normal_bounded(
                    n=date_df.shape[0],
                    loc=self.config["maintenance"]["energy_loc"],
                    scale=self.config["maintenance"]["energy_scale"],
                    condition=self.config["maintenance"]["energy_min"],
                    round_d=2,
                ),
                "type": np.full(date_df.shape[0], "MEDIA"),
            }
        )
        return df

    def gen_heat_expenses(self):
        dates = []
        date_df = self.prompts["prompt_dates"].loc[
            self.prompts["prompt_dates"]["date"].dt.day == self.config["payment_day"],
            "date",
        ]
        for j in range(
            self.prompts["prompt_dates"]["date"].iloc[0].year,
            self.prompts["prompt_dates"]["date"].iloc[-1].year + 1,
        ):
            for i in range(
                self.config["warm_months"]["first"],
                self.config["warm_months"]["last"] + 1,
            ):
                day = datetime.datetime(j, i, self.config["payment_day"])
                dates.append(day.strftime("%Y-%m-%d"))
        for i in dates:
            date_df = date_df.drop(date_df[date_df == i].index)
        title = date_df.dt.month_name(locale="pl_PL").apply(
            lambda x: "OGRZEWANIE " + str(x).upper()
        )
        df = pd.DataFrame(
            {
                "date": date_df,
                "title": title,
                "amount": self.random_normal_bounded(
                    n=date_df.shape[0],
                    loc=self.config["maintenance"]["heat_loc"],
                    scale=self.config["maintenance"]["heat_scale"],
                    condition=self.config["maintenance"]["heat_min"],
                    round_d=2,
                ),
                "type": np.full(date_df.shape[0], "MEDIA"),
            }
        )
        return df

    def gen_salary_expenses(self, staff: pd.DataFrame):
        date_df = self.gen_expenses_dates()
        all_staff = pd.concat(
            [staff[["first_name", "last_name", "current_salary"]]] * date_df.shape[0],
            ignore_index=True,
        )
        staff_name = staff["first_name"].str.cat(staff["last_name"], sep=" ")
        names = pd.concat([staff_name] * date_df.shape[0], ignore_index=True)
        dates = np.repeat(date_df, staff_name.shape[0])
        dates = dates.reset_index()["date"]
        title_first = dates.dt.month_name(locale="pl_PL").apply(
            lambda x: "PENSJA " + str(x).upper()
        )
        title = title_first.str.cat(names, sep=" ")
        df = pd.DataFrame(
            {
                "date": dates,
                "title": title,
                "amount": all_staff["current_salary"],
                "type": np.full(title.shape[0], "PENSJA"),
            }
        )
        to_date = pd.to_datetime(
            staff["to_date"].loc[staff["to_date"].isnull() == False].values[0]
        )
        df.loc[
            (df["amount"].isnull() == True) & (df["date"] < to_date), "amount"
        ] = np.round(
            self.config["salary_settings"]["minimal"]
            + np.random.exponential(
                scale=self.config["salary_settings"]["exp_scale"],
            ),
            2,
        )
        df.dropna(inplace=True)
        return df

    def prepar_tournament_game(self):
        # all the tournament title & game options
        games = self.prompts["prompt_games"].loc[
            self.prompts["prompt_games"]["tournament"] == "TAK",
            ["name", "type", "category"],
        ]
        tournament_games = pd.merge(
            games,
            self.prompts["prompt_tournaments"],
            left_on=["type", "category"],
            right_on=["type", "category"],
            suffixes=["_game", "_tournament"],
        )
        tournament_games = tournament_games[["name_game", "name_tournament"]]
        return tournament_games

    def gen_tournament_staff(self, n=int):
        available_staff = (
            self.prompts["prompt_staff_shifts"]
            .loc[
                (
                    self.prompts["prompt_staff_shifts"]["weekday"]
                    == self.config["event_info"]["weekday"]
                )
                & (
                    self.prompts["prompt_staff_shifts"]["hour"]
                    >= self.config["event_info"]["hour"]
                )
            ]["staff_id"]
            .unique()
        )
        return np.random.choice(available_staff, size=n)

    @staticmethod
    def count_matches(x):
        total = 0
        while x >= 0:
            total += 2**x
            x -= 1
        return total

    def gen_sign_u_date(self, deadline: datetime.datetime):
        deadline = pd.to_datetime(deadline)
        date = pd.to_datetime(
            self.prompts["prompt_dates"]["date"]
            .loc[
                (self.prompts["prompt_dates"]["date"] < deadline)
                & (
                    self.prompts["prompt_dates"]["date"]
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
        )
        return date

    @staticmethod
    @np.vectorize
    def v_repeat(date: datetime.datetime, volume: int):
        return itertools.repeat(date, int(volume))

    @staticmethod
    @np.vectorize
    def v_timedelta(h: int, m: int, s: int):
        return datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))

    def v_get_staff_id(self, timestamp: pd.Timestamp):
        def _scalar_fun(timestamp: pd.Timestamp):
            # general of gen_tournament_staff
            available_staff = self.prompts["prompt_staff_shifts"][
                (self.prompts["prompt_staff_shifts"]["weekday"] == timestamp.weekday())
                & (self.prompts["prompt_staff_shifts"]["hour"] == timestamp.hour)
            ]["staff_id"]

            return np.random.choice(available_staff)

        return np.vectorize(_scalar_fun)(timestamp)

    def gen_sell_inventory(self) -> pd.DataFrame:
        # evaluate a total game number
        total_games_n = np.round(
            self.prompts["prompt_dates"]["volume_sales"].sum()
            * (self.config["inventory_multiplier"] + np.random.exponential())
        )
        game_counts = list(
            map(round, self.prompts["prompt_games"]["weights"] * total_games_n)
        )
        # repeat the games
        games_gener = itertools.chain(
            *self.v_repeat(self.prompts["prompt_games"]["name"], game_counts)
        )
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
                self.prompts["prompt_games"][["name", "purchase"]],
                left_on="game",
                right_on="name",
                how="inner",
            )
            .rename(columns={"purchase": "price"})
            .drop(columns="name")
        )
        # add the procurment prices as some fraction of the standard one
        s_inventory["purchase_payment"] = (
            s_inventory["price"] * self.config["bulk_ratio"]
        ).round(2)
        s_inventory = s_inventory.sample(n=s_inventory.shape[0]).reset_index(drop=True)
        # get the delivery dates
        delivery_count = (
            self.config["avg_supply_yearly_rate"] * self.config["shop_lifetime_years"]
        )
        delivery_dates = self.prompts["prompt_dates"]["date"][
            :: int(self.prompts["prompt_dates"].shape[0] / delivery_count)
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

    def gen_rent_inventory(self) -> pd.DataFrame:
        total_games_n = self.config["rental_games_n"]
        game_counts = list(
            map(round, self.prompts["prompt_games"]["weights"] * total_games_n)
        )
        # repeat the games
        games_gener = itertools.chain(
            *self.v_repeat(self.prompts["prompt_games"]["name"], game_counts)
        )
        games = np.array(list(games_gener))
        # active statuses
        active_status = np.full(games.size, True)
        active_status[: self.config["inactive_rental_games"]] = False
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
                self.prompts["prompt_games"][["name", "purchase"]],
                left_on="game",
                right_on="name",
                how="inner",
            )
            .rename(columns={"purchase": "price"})
            .drop(columns="name")
        )
        # add the procurment prices as some fraction of the standard one
        r_inventory["purchase_payment"] = (
            r_inventory["price"] * self.config["bulk_ratio"]
        ).round(2)
        # the delivery dates
        r_inventory["delivery_date"] = self.prompts["prompt_dates"]["date"].iloc[
            0
        ] + datetime.timedelta(hours=self.config["shop_open_hours"]["from"])
        r_inventory["price"] = (
            r_inventory["price"] * self.config["rental_price_ratio"]
        ).round(2)
        return r_inventory

    def gen_tournament_inventory(self, tournaments: pd.DataFrame) -> pd.DataFrame:
        # find the required game counts
        game_counts_tournaments = (
            tournaments[["game", "tree_levels"]]
            .groupby("game")
            .max()
            .apply(lambda x: 2**x)
        ).reset_index()
        # repeat the games
        games_gener = itertools.chain(
            *self.v_repeat(
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
                self.prompts["prompt_games"][["name", "purchase"]],
                left_on="game",
                right_on="name",
                how="inner",
            )
            .rename(columns={"purchase": "price"})
            .drop(columns="name")
        )
        # add the procurment prices as some fraction of the standard one
        t_inventory["purchase_payment"] = (
            t_inventory["price"] * self.config["bulk_ratio"]
        ).round(2)
        # the delivery dates
        t_inventory["delivery_date"] = self.prompts["prompt_dates"]["date"].iloc[
            0
        ] + datetime.timedelta(hours=self.config["shop_open_hours"]["from"])
        t_inventory["price"] = np.nan
        return t_inventory

    def proper_return_date(self, timestamp: datetime.datetime, date: datetime.datetime):
        if (timestamp.day == date.day) & (timestamp.hour < date.hour):
            return timestamp.replace(hour=self.config["shop_open_hours"]["from"])
        elif timestamp.hour < self.config["shop_open_hours"]["from"]:
            return timestamp.replace(hour=self.config["shop_open_hours"]["from"])
        elif timestamp.hour >= self.config["shop_open_hours"]["to"]:
            return timestamp.replace(hour=self.config["shop_open_hours"]["to"] - 1)
        else:
            return timestamp
