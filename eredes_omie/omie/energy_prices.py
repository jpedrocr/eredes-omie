import glob
import os
from datetime import datetime, timedelta

import pandas as pd
import requests


__check_start__ = datetime.fromisoformat("2024-04-01")
__tomorrow__ = datetime.now() + timedelta(days=1)


def download_prices(requested_date: datetime = __tomorrow__) -> None:
    """
    Downloads the prices data from the OMIE's website and saves it to a file.
    """
    # Convert requested date to the format YYYYMMDD
    requested_date = requested_date.strftime("%Y%m%d")

    # Define the URL
    url = f"https://www.omie.es/en/file-download?parents%5B0%5D=marginalpdbcpt&filename=marginalpdbcpt_{requested_date}.1"
    
    print(f"Downloaded energy prices for date: {requested_date}")

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Save the content to a file
        with open(
            f"/workspace/data/prices/marginalpdbcpt_{requested_date}.1", "wb"
        ) as file:
            file.write(response.content)
    else:
        print(f"Failed to download energy prices for date: {requested_date}")


def check_and_download(
    start_date: datetime = __check_start__, end_date: datetime = __tomorrow__
) -> None:
    """
    Checks if the price data files for the given date range exist, and downloads the missing files.

    Args:
        start_date (datetime): The start date of the date range to check. Defaults to `__check_start__`.
        end_date (datetime): The end date of the date range to check. Defaults to `__tomorrow__`.

    Raises:
        None
    """
    # Iterate over the dates from start_date to end_date
    date = start_date
    while date <= end_date:
        # Convert date to the format YYYYMMDD
        date_str = date.strftime("%Y%m%d")

        # Define the file path
        file_path = f"/workspace/data/prices/marginalpdbcpt_{date_str}.1"

        # Check if the file exists
        if not os.path.exists(file_path):
            # If the file doesn't exist, download the data for this date
            download_prices(date)

        # Move to the next date
        date += timedelta(days=1)


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
    # Assure all available prices are downloaded
    check_and_download()
    
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

    # Set the 'starting_datetime' column as UTC
    df["starting_datetime"] = df["starting_datetime"].dt.tz_localize("UTC")

    # Write the dataframe to a single csv file
    df.to_csv("/workspace/data/energy_prices.csv", index=False)

    # Group by year and calculate the maximum and minimum price
    max_min_prices = df.groupby(df["starting_datetime"].dt.year)["€/MWh"].agg(
        ["max", "min", "mean"]
    )

    # Print the maximum and minimum price for each year
    print(f"Energy prices per year (€/MWh):\n{max_min_prices}\n")

    # Return the dataframe
    return df


def get_prices() -> pd.DataFrame:
    """
    Loads the losses profiles data from a CSV file.

    Returns:
        pd.DataFrame: A DataFrame containing the losses profiles data.
    """
    # Load the dataframe from a CSV file
    df = pd.read_csv("/workspace/data/energy_prices.csv")

    # Return the dataframe
    return df
