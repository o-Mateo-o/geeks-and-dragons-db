"""Helper functions for data generation."""

import numpy as np
import pandas as pd
import datetime
import numpy.typing as npt
import numpy as np
import pandas as pd
from faker import Faker
from unidecode import unidecode_expect_ascii


class RandomHelpers:
    def __init__(self, config: dict, prompts: dict) -> None:
        self.config = config
        self.prompts = prompts
        self.phone_base = []
        self.email_base = []

    @np.vectorize
    def gen_one_phone(self, *args) -> str:
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

    @np.vectorize
    def gen_one_name(self, gender: str, mode: str) -> str:
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

    @np.vectorize
    def gen_email(self, first_name: str, last_name: str) -> str:
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

    def gen_staff_to_date(self) -> npt.NDArray:
        # NULL fill
        dates = np.zeros(self.config["staff_number"], dtype=np.object_)
        dates[:] = np.nan
        # find the constants
        some_employee_ix = -2
        shop_open_date = self.prompts["prompt_dates"]["date"].iloc[0]
        today = self.prompts["prompt_dates"]["date"].iloc[-1]
        # fire him
        dates[some_employee_ix] = Faker().date_between(
            shop_open_date + datetime.timedelta(days=90),
            today - datetime.timedelta(days=90),
        )
        return dates

    def gen_staff_form_date(self, staff: pd.DataFrame) -> npt.NDArray:
        # hire all of them
        dates = np.zeros(self.config["staff_number"], dtype=np.object_)
        dates[:] = self.prompts["prompt_dates"]["date"].iloc[0]
        # hire one with a time shift
        some_employee_ix = -1
        ones_end_date = (
            staff["to_date"].loc[staff["to_date"].isnull() == False].values[0]
        )
        dates[some_employee_ix] = ones_end_date + datetime.timedelta(days=30)
        return dates

    def gen_staff_update_time(self, staff: pd.DataFrame) -> npt.NDArray:
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
        mask = arr > condition
        arr[mask] = condition
        return arr.round(round_d)

    def gen_expenses_dates(self):
        base = pd.DataFrame(
            self.prompts["prompt_dates"].loc[
                (self.prompts["prompt_dates"]["date"].dt.day == self.config["payment_day"])
                | (self.prompts["prompt_dates"]["date"].dt.day == self.config["payment_day"] + 1),
                "date",
            ]
        )
        base["flag"] = base["date"].dt.to_period("M")
        base.drop_duplicates(["flag"], keep="first", inplace=True)
        base = base.reset_index()
        return base["date"]

    def gen_rent_expenses(self):
        date_df = self.prompts["prompt_dates"].loc[
            self.prompts["prompt_dates"]["date"].dt.day == self.config["payment_day"], "date"
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
            self.prompts["prompt_dates"]["date"].dt.day == self.config["payment_day"], "date"
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
            self.prompts["prompt_dates"]["date"].dt.day == self.config["payment_day"], "date"
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
            self.prompts["prompt_dates"]["date"].dt.day == self.config["payment_day"], "date"
        ]
        for j in range(
            self.prompts["prompt_dates"]["date"].iloc[0].year, self.prompts["prompt_dates"]["date"].iloc[-1].year + 1
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
    
    def gen_salary_expenses(self, staff: pd.DataFramef):
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
