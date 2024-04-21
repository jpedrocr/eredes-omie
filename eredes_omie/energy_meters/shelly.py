# Fix, improve, refactor and add comments, as needed, in English
from dataclasses import dataclass
from enum import Enum
from time import sleep

import pandas as pd
import requests
from tqdm import tqdm


@dataclass
class EnergyLabel:
    """
    Dataclass to represent an energy label.
    """

    id: int
    id_label: str
    energy_in_label: str
    energy_out_label: str


class EnergySource(EnergyLabel, Enum):
    """
    Enum class to represent different energy sources.
    Each energy source is an instance of EnergyLabel.
    """

    GRID = 0, "grid", "consumed", "returned"
    SOLAR = 1, "solar", "produced", None

    def download_data(
        self,
        origin: str = "http://10.15.40.2",
        save_path: str = "/workspace/data/shelly",
        debug: bool = False,
    ) -> None:
        """
        Download energy data from a CSV file.

        Args:
            save_path (str): Path to save the downloaded data.
            debug (bool): If True, print debug information. Defaults to False.
        """
        # Download the CSV file containing the energy data
        self.__download_csv__(
            url=f"{origin}/emeter/{self.id}/em_data.csv",
            filename=f"em_data.{self.id_label}.csv",
            save_path=save_path,
            debug=debug,
        )

    def get_data(
        self, save_path: str = "/workspace/data/shelly", debug: bool = False
    ) -> pd.DataFrame:
        """
        Load the energy data from a CSV file into a pandas DataFrame.

        Args:
            debug (bool): If True, print debug information. Defaults to False.

        Returns:
            pd.DataFrame: DataFrame containing the energy data.
        """
        # Define the column names and types for the DataFrame
        column_names = [
            "timestamp_utc",
            f"{self.id_label}_{self.energy_in_label}_energy_Wh",
            f"{self.id_label}_{self.energy_out_label}_energy_Wh",
            f"{self.id_label}_voltage_min_V",
            f"{self.id_label}_voltage_max_V",
        ]
        column_types = {
            f"{self.id_label}_{self.energy_in_label}_energy_Wh": "Float64",
            f"{self.id_label}_{self.energy_out_label}_energy_Wh": "Float64",
            f"{self.id_label}_voltage_min_V": "Float64",
            f"{self.id_label}_voltage_max_V": "Float64",
        }

        # Load the CSV file into a DataFrame
        df = pd.read_csv(
            f"{save_path}/em_data.{self.id_label}.csv",
            sep=",",
            names=column_names,
            dtype=column_types,
            parse_dates=["timestamp_utc"],
            header=0,
            index_col=False,
        )

        # Set the DataFrame index to the timestamp column, localized to UTC
        df.index = pd.to_datetime(df["timestamp_utc"]).dt.tz_localize("UTC")
        df.drop(columns=["timestamp_utc"], inplace=True)

        return df

    def __download_csv__(
        self, url, filename, save_path="/workspace/data/shelly", debug: bool = False
    ):
        # Construct the full path with the provided destination filename
        full_path = save_path + "/" + filename

        # Start the download
        response = requests.get(url, stream=True)

        # Check for the specific error message before downloading
        if "Another file transfer is in progress!" in response.text:
            print("\nDownload failed: Another file transfer is in progress!")
            return

        # Get the total size of the file from the response headers
        total_size_in_bytes = int(response.headers.get("content-length", 0))
        block_size = 1024  # 1 Kibibyte

        try:
            print(f"\nDownloading {filename}...")

            # Initialize the progress bar
            progress_bar = tqdm(total=total_size_in_bytes, unit="iB", unit_scale=True)

            with open(full_path, "wb") as file:
                for data in response.iter_content(block_size):
                    file.write(data)
                    progress_bar.update(len(data))
                    sleep(0.01)
                progress_bar.close()

            # Check if the download was completed
            if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                print("\nERROR, something went wrong")
            else:
                print(f"\nDownload completed. File saved as {full_path}")
        except Exception as e:
            print(f"\nAn error occurred: {e}")

def process_energy_history(debug: bool = False) -> pd.DataFrame:
    """
    This function downloads and processes energy history data from Shelly devices.

    Parameters:
        debug (bool): Whether to enable debug mode or not. Defaults to False.

    Returns:
        df (pd.DataFrame): A DataFrame containing the processed energy history data.
    """

    if debug:
        print("Starting the function process_energy_history...")

    # Download energy data for grid and solar sources
    if debug:
        print("Downloading energy data...")
    EnergySource.GRID.download_data(debug=debug)
    EnergySource.SOLAR.download_data(debug=debug)

    # Get the energy data for both grid and solar energy sources
    if debug:
        print("Getting energy data...")
    grid_df = EnergySource.GRID.get_data(debug=debug)
    solar_df = EnergySource.SOLAR.get_data(debug=debug)

    # Concatenate the grid and solar DataFrames along the columns (axis=1)
    df = pd.concat([grid_df, solar_df], axis=1)

    # Resample the data every 15 minutes and sum the values
    if debug:
        print("Resampling data...")
    df = df.resample("15min").sum()

    # Calculate the net grid energy by subtracting the returned energy from the consumed energy
    df.loc[:, "grid_Wh"] = df["grid_consumed_energy_Wh"] - df["grid_returned_energy_Wh"]

    # Calculate the total consumed energy by adding the net grid energy and the solar produced energy
    df.loc[:, "consumed_Wh"] = df["grid_Wh"] + df["solar_produced_energy_Wh"]

    # Select the columns of interest
    if debug:
        print("Selecting columns...")
    df = df[["grid_Wh", "solar_produced_energy_Wh", "consumed_Wh"]]

    # Convert the energy values from Wh to kWh (divide by 1000)
    if debug:
        print("Converting units...")
    df = df / 1000

    # Rename the columns to reflect the new units
    if debug:
        print("Renaming columns...")
    df.rename(
        columns={
            "grid_Wh": "grid_kWh",
            "solar_produced_energy_Wh": "solar_kWh",
            "consumed_Wh": "consumed_kWh",
        },
        inplace=True,
    )

    # Round the energy values to 6 decimal places
    if debug:
        print("Rounding values...")
    df["grid_kWh"] = df["grid_kWh"].round(6)
    df["solar_kWh"] = df["solar_kWh"].round(6)
    df["consumed_kWh"] = df["consumed_kWh"].round(6)

    # Export the processed data to a CSV file
    if debug:
        print("Exporting data...")
    df.to_csv("/workspace/data/shelly_energy_history.csv")

    return df


# Fix, improve, refactor and add comments to the code bellow, as needed, in English
def save_yesterday_solar_production(debug: bool = False) -> pd.DataFrame:
    """
    Saves the solar production data for yesterday to a CSV file and prints the total solar production for yesterday.

    This function downloads the solar data, filters out the data for yesterday, concatenates it with the full solar data, removes any duplicate rows, and saves the updated data to a CSV file. It then prints the total solar production for yesterday.

    Args:
        debug (bool): If True, prints debug messages during the function execution.

    Returns:
        pandas.DataFrame: A DataFrame containing the solar production data for yesterday.
    """

    if debug:
        print("Starting the function save_yesterday_solar_production...")

    # Download solar data
    if debug:
        print("Downloading solar data...")
    EnergySource.SOLAR.download_data(debug=debug)

    # Get solar data
    if debug:
        print("Getting solar data...")
    solar_df = EnergySource.SOLAR.get_data(debug=debug).reset_index(drop=False)

    # Add a new column "date" to the dataframe
    if debug:
        print("Adding a new column 'date' to the dataframe...")
    solar_df["date"] = solar_df["timestamp_utc"].dt.normalize()

    # Get yesterday's date
    if debug:
        print("Getting yesterday's date...")
    yesterday = pd.Timestamp.today() - pd.Timedelta(days=1)
    yesterday = yesterday.normalize().tz_localize("UTC")

    # Filter out the data for yesterday
    if debug:
        print("Filtering out the data for yesterday...")
    yesterday_solar_df = solar_df[solar_df["date"] == yesterday].copy()

    # Sort the dataframe by timestamp and reset the index
    if debug:
        print("Sorting the dataframe by timestamp and resetting the index...")
    yesterday_solar_df.sort_values(by=["timestamp_utc"], inplace=True)
    yesterday_solar_df.reset_index(inplace=True, drop=True)

    # Keep only the necessary columns
    if debug:
        print("Keeping only the necessary columns...")
    yesterday_solar_df = yesterday_solar_df[["timestamp_utc", "solar_Wh"]]

    # Read the full solar data from the CSV file
    if debug:
        print("Reading the full solar data from the CSV file...")
    full_solar_df = pd.read_csv(
        "/workspace/data/shelly_solar.csv",
        sep=",",
        names=["timestamp_utc", "solar_Wh"],
        dtype={"timestamp_utc": "str", "solar_Wh": "Float64"},
        header=0,
        index_col=False,
    )

    # Convert the timestamp column to datetime
    if debug:
        print("Converting the timestamp column to datetime...")
    full_solar_df["timestamp_utc"] = pd.to_datetime(full_solar_df["timestamp_utc"])

    # Concatenate the full solar data with yesterday's solar data
    if debug:
        print("Concatenating the full solar data with yesterday's solar data...")
    full_solar_df = pd.concat([full_solar_df, yesterday_solar_df])

    # Sort the dataframe by timestamp
    if debug:
        print("Sorting the dataframe by timestamp...")
    full_solar_df.sort_values(by=["timestamp_utc"], inplace=True)

    # Remove duplicate rows
    if debug:
        print("Removing duplicate rows...")
    full_solar_df.drop_duplicates(subset=["timestamp_utc", "solar_Wh"], inplace=True)

    # Save the dataframe to the CSV file
    if debug:
        print("Saving the dataframe to the CSV file...")
    full_solar_df.to_csv("/workspace/data/shelly_solar.csv", index=False)

    # Reset the index of the dataframe
    if debug:
        print("Resetting the index of the dataframe...")
    full_solar_df.reset_index(inplace=True, drop=True)

    # Set the index of yesterday's solar data to timestamp
    if debug:
        print("Setting the index of yesterday's solar data to timestamp...")
    yesterday_solar_df.set_index("timestamp_utc", inplace=True)

    # Print the total solar production for yesterday
    if debug:
        print("Printing the total solar production for yesterday...")
    print(
        f"\nYesterday's solar production: \n{yesterday_solar_df.resample('1D').sum()}"
    )

    return yesterday_solar_df
