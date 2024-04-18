from time import sleep

import pandas as pd
import requests
from tqdm import tqdm


def download_csv(url, filename, save_path="/workspace/data/shelly/"):
    # Construct the full path with the provided destination filename
    full_path = save_path + filename

    # Start the download
    response = requests.get(url, stream=True)

    # Check for the specific error message before downloading
    if "Another file transfer is in progress!" in response.text:
        print("Download failed: Another file transfer is in progress!")
        return

    # Get the total size of the file from the response headers
    total_size_in_bytes = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1 Kibibyte

    # Initialize the progress bar
    progress_bar = tqdm(total=total_size_in_bytes, unit="iB", unit_scale=True)

    try:
        with open(full_path, "wb") as file:
            for data in response.iter_content(block_size):
                file.write(data)
                progress_bar.update(len(data))
                sleep(0.01)
            progress_bar.close()

        # Check if the download was completed
        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print("ERROR, something went wrong")
        else:
            print(f"Download completed. File saved as {full_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


def save_yesterday_solar_production():
    """
    Downloads yesterday's solar production data from Shelly's website.
    """
    # Download the CSV file containing the solar data
    download_csv(
        "http://10.15.40.2/emeter/1/em_data.csv",
        filename="em_data.solar.csv",
        save_path="/workspace/data/shelly/",
    )

    # Load the solar data from the downloaded CSV file
    solar_df = pd.read_csv(
        "/workspace/data/shelly/em_data.solar.csv",
        sep=",",
        names=["timestamp_utc", "solar_Wh", "f2", "f3", "f4"],
        dtype={
            "timestamp_utc": "str",
            "solar_Wh": "Float64",
            "f2": "Float64",
            "f3": "Float64",
            "f4": "Float64",
        },
        header=0,
        index_col=False,
    )

    # Convert the timestamp to datetime and set the timezone to UTC
    solar_df["timestamp_utc"] = pd.to_datetime(
        solar_df["timestamp_utc"]
    ).dt.tz_localize("UTC")

    # Add a new column 'date' by normalizing the timestamp to the date
    solar_df["date"] = solar_df["timestamp_utc"].dt.normalize()

    # # Get yesterday's date in UTC
    yesterday = pd.Timestamp.today() - pd.Timedelta(days=1)
    yesterday = yesterday.normalize().tz_localize("UTC")

    # Filter the data for yesterday
    yesterday_solar_df = solar_df[solar_df["date"] == yesterday].copy()

    # Sort the data by timestamp and reset the index
    yesterday_solar_df.sort_values(by=["timestamp_utc"], inplace=True)
    yesterday_solar_df.reset_index(inplace=True, drop=True)

    # Keep only the timestamp and solar production columns
    yesterday_solar_df = yesterday_solar_df[["timestamp_utc", "solar_Wh"]]

    # Load the full solar data
    full_solar_df = pd.read_csv(
        "/workspace/data/solar.csv",
        sep=",",
        names=["timestamp_utc", "solar_Wh"],
        dtype={"timestamp_utc": "str", "solar_Wh": "Float64"},
        header=0,
        index_col=False,
    )

    # Convert the timestamp to datetime
    full_solar_df["timestamp_utc"] = pd.to_datetime(full_solar_df["timestamp_utc"])

    # Concatenate the new data with the existing data
    full_solar_df = pd.concat([full_solar_df, yesterday_solar_df])

    # Sort the data by timestamp
    full_solar_df.sort_values(by=["timestamp_utc"], inplace=True)

    # Remove any duplicates
    full_solar_df.drop_duplicates(subset=["timestamp_utc", "solar_Wh"], inplace=True)

    # Save the updated data to a CSV file
    full_solar_df.to_csv("/workspace/data/solar.csv", index=False)

    # Reset the index
    full_solar_df.reset_index(inplace=True, drop=True)

    # Set 'timestamp_utc' as the index
    yesterday_solar_df.set_index("timestamp_utc", inplace=True)

    # Now you can resample
    print(f"Yesterday's solar production: \n{yesterday_solar_df.resample('1D').sum()}")
