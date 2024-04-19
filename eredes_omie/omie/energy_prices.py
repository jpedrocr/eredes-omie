import glob
import os

import pandas as pd
import requests
import utils
from typing import Optional
from requests.exceptions import SSLError, RequestException


def download_prices(requested_date: Optional[pd.Timestamp] = None) -> None:
    """
    Downloads the prices data from the OMIE's website and saves it to a file.

    Args:
        requested_date (pd.Timestamp, optional): The date for which the prices data is to be downloaded. Defaults to tomorrow's date.
    """
    # If no date is provided, default to tomorrow's date
    if requested_date is None:
        requested_date = utils.tomorrow()

    # Convert requested date to the format YYYYMMDD
    requested_date_str = requested_date.strftime("%Y%m%d")

    # Define the URL for the OMIE's website
    url = f"https://www.omie.es/pt/file-download?parents%5B0%5D=marginalpdbcpt&filename=marginalpdbcpt_{requested_date_str}.1"

    try:
        # Send a GET request to the URL
        response = requests.get(url, verify=True)

        # Check if the request was successful
        if response.status_code == 200 and response.content != b"":
            print(f"\nDownloaded energy prices for date: {requested_date_str}")

            # Define the directory for saving the file
            dir_path = "/workspace/data/energy_prices/"
            # Create the directory if it does not exist
            os.makedirs(dir_path, exist_ok=True)

            # Save the content to a file
            with open(
                os.path.join(dir_path, f"marginalpdbcpt_{requested_date_str}.1"), "wb"
            ) as file:
                file.write(response.content)
        else:
            print(f"\nFailed to download energy prices for date: {requested_date_str}")
    except SSLError as e:
        print(
            f"\nSSL error occurred while trying to download energy prices for date: {requested_date_str}. Error details: {e}"
        )
    except RequestException as e:
        print(
            f"\nAn error occurred while trying to download energy prices for date: {requested_date_str}. Error details: {e}"
        )


def check_and_download(
    start_date: pd.Timestamp = utils.check_start(),
    end_date: pd.Timestamp = utils.tomorrow(),
) -> None:
    """
    Checks if the price data files for the given date range exist, and downloads the missing files.

    Args:
        start_date (pd.Timestamp): The start date of the date range to check. Defaults to `__check_start__`.
        end_date (pd.Timestamp): The end date of the date range to check. Defaults to `__tomorrow__`.

    Raises:
        None
    """
    # Iterate over the dates from start_date to end_date
    current_date = start_date
    while current_date <= end_date:
        # Convert date to the format YYYYMMDD
        date_str = current_date.strftime("%Y%m%d")

        # Define the file path
        file_path = f"/workspace/data/energy_prices/marginalpdbcpt_{date_str}.1"

        # Check if the file exists
        if not os.path.exists(file_path):
            # If the file doesn't exist, download the data for this date
            download_prices(current_date)

        # Move to the next date
        current_date += pd.Timedelta(days=1)


def add_missing_timeslots(temp_df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds missing time slots to the end of the day in the energy prices data.

    Args:
        temp_df (pd.DataFrame): The energy prices data.

    Returns:
        pd.DataFrame: The energy prices data with added time slots.
    """
    # Check if the last time slot is less than 23:45
    last_time_slot = temp_df.index[-1].time()
    if last_time_slot < pd.Timestamp("23:45").time():
        # If so, add new rows for the missing time slots
        end_of_day = pd.date_range(
            start=temp_df.index[-1] + pd.Timedelta(minutes=15),
            end=temp_df.index[-1].normalize() + pd.Timedelta(hours=23, minutes=45),
            freq="15min",
        )
        empty_df = pd.DataFrame(index=end_of_day)
        temp_df = pd.concat([temp_df, empty_df])
        temp_df = temp_df.ffill()

    return temp_df


def update_prices() -> pd.DataFrame:
    """
    Updates the energy prices data by reading in all the CSV files in
    the "/workspace/data/energy_prices/" directory, concatenating the data
    into a single DataFrame, and writing the result to a CSV file
    at "/workspace/data/energy_prices.csv". The function also calculates
    the maximum and minimum price for each year and prints the results.

    Returns:
        pd.DataFrame: The updated energy prices data.
    """
    # Assure all available prices are downloaded
    check_and_download()

    # Get a list of all the files in the data folder
    files = sorted(glob.glob(os.path.join("/workspace/data/energy_prices", "*.1")))

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

        # Add the missing time slots
        temp_df = add_missing_timeslots(temp_df)

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
    print(f"\nEnergy prices per year (€/MWh):\n{max_min_prices}")

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


def is_available(date: pd.Timestamp) -> bool:
    """
    Checks if the energy prices data is available for the given date.
    """
    # Convert date to the format YYYYMMDD
    date_str = date.strftime("%Y%m%d")

    # Define the file path
    file_path = f"/workspace/data/energy_prices/marginalpdbcpt_{date_str}.1"

    # Check if the file exists
    if os.path.exists(file_path):
        return True
    else:
        return False
