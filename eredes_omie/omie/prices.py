import pandas as pd
import glob
import os


def update_prices() -> pd.DataFrame:
    """
    Updates the energy prices data by reading in all the CSV files in
    the "/workspace/data/prices/" directory, concatenating the data
    into a single DataFrame, and writing the result to a CSV file
    at "/workspace/data/energy_prices.csv". The function also calculates
    the maximum and minimum price for each year and prints the results.

    Returns:
        pd.DataFrame: The updated energy prices data.
    """
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
                "spain€/MWh",
                "portugal€/MWh",
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
        dfs.append(temp_df[["portugal€/MWh"]])

    # Concatenate all dataframes in the list
    df = pd.concat(dfs)

    # Reset the index
    df.reset_index(inplace=True)

    df.columns = ["starting_datetime", "€/MWh"]

    # Write the dataframe to a single csv file
    df.to_csv("/workspace/data/energy_prices.csv", index=False)

    # Group by year and calculate the maximum and minimum price
    max_min_prices = df.groupby(df["starting_datetime"].dt.year)["€/MWh"].agg(
        ["max", "min"]
    )

    # Print the maximum and minimum price for each year
    print(max_min_prices)

    # Return the dataframe
    return df


def get_prices() -> pd.DataFrame:
    """
    Loads the losses profiles data from a CSV file.

    Returns:
        pd.DataFrame: A DataFrame containing the losses profiles data.
    """
    # Load the dataframe from a CSV file
    df = pd.read_csv("./data/prices.csv")

    # Return the dataframe
    return df
