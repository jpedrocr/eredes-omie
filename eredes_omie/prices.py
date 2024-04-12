import pandas as pd
import glob
import os


def process_and_save():
    # Get a list of all the files in the data folder
    files = sorted(glob.glob(os.path.join("/workspace/data/prices/", "*.1")))

    # Initialize a list to store the dataframes
    dfs = []

    # Iterate over each file
    for file in files:
        # Read the file into a dataframe, ignoring the last line
        temp_df = pd.read_csv(
            file,
            sep=";",
            skiprows=1,
            skipfooter=1,
            names=[
                "year",
                "month",
                "day",
                "duration",
                "spain€/kWh",
                "portugal€/kWh",
                "value",
            ],
            engine="python",
        )

        # Convert the year, month, and day columns to a datetime
        temp_df["datetime"] = pd.to_datetime(
            temp_df["year"].astype(str).str.zfill(4)
            + "-"
            + temp_df["month"].astype(str).str.zfill(2)
            + "-"
            + temp_df["day"].astype(str).str.zfill(2),
            format="%Y-%m-%d",
        )

        # Add the duration as hours to the datetime
        temp_df["datetime"] += pd.to_timedelta((temp_df["duration"] - 1), unit="h")

        # Resample the data to quarters of hour and forward fill the missing values
        temp_df.set_index("datetime", inplace=True)
        temp_df = temp_df.resample("15min").ffill()

        # Append the dataframe to the list
        dfs.append(temp_df[["portugal€/kWh"]])

    # Concatenate all dataframes in the list
    df = pd.concat(dfs)

    # Reset the index
    df.reset_index(inplace=True)

    df.columns = ["starting_datetime", "€/kWh"]

    # Write the dataframe to a single csv file
    df.to_csv("/workspace/data/energy_prices.csv", index=False)

    # Group by year and calculate the maximum and minimum price
    max_min_prices = df.groupby(df["starting_datetime"].dt.year)["€/kWh"].agg(
        ["max", "min"]
    )

    # Print the maximum and minimum price for each year
    print(max_min_prices)

    # Return the dataframe
    return df


def calculate_kwh_cost(prices: pd.DataFrame, losses: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the final cost per kWh including losses and fees.

    Args:
        prices (pandas.DataFrame): Dataframe containing prices data.
        losses (pandas.DataFrame): Dataframe containing losses data.

    Returns:
        pandas.DataFrame: Dataframe with final cost per kWh added.
    """
    # FA (Adjustment factor) corresponds to the constant 1.03.
    af = 1.03

    # qFare = 0.01479 €/kWh - Cost of Complementary Services
    qfare = 0.01479
    
    df = pd.DataFrame()

    # Calculates the final price per kWh including losses and fees
    df["€€€/kWh"] = (prices["€/kWh"] + 0) * (1 + losses["value"]) * af + qfare

    return df
