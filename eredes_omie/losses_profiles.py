from glob import glob
import pandas as pd


def get_losses_profiles() -> pd.DataFrame:
    """
    Get the losses profiles from E-REDES.
    """

    # Get the list of consumption history files
    files = sorted(glob("/workspace/data/losses_profiles/*.xlsx"))

    # Initialize a list of dataframes
    dfs = []

    # Loop through the files
    for file in files:
        print(f"Processing {file}")
        # Load the file into a dataframe
        df = pd.read_excel(
            file,
            skiprows=2,
        )

        # Append the dataframe to the list
        dfs.append(df)

    # Concatenate the dataframes
    df = pd.concat(dfs)

    # Use only columns 1, 3 and 4, index 0
    df = df.iloc[:, [1, 3, 4]]

    # Set column names to date, time, value
    df.columns = ["date", "time", "value"]

    # Convert the 'date' column to datetime
    df["date"] = pd.to_datetime(df["date"])

    # Append ':00' to 'time' column and convert it to timedelta
    df["time"] = pd.to_timedelta(df["time"] + ':00')

    # Subtract 15 minutes to get the starting time of the interval
    df["starting_time"] = df["time"] - pd.Timedelta(minutes=15)

    # Combine the 'date' and 'starting_time' to create a 'starting_datetime' column
    df["starting_datetime"] = df["date"] + df["starting_time"]

    # Set the datetime column as UTC
    df["starting_datetime"] = df["starting_datetime"].dt.tz_localize("UTC")

    # Set only the final columns
    df = df[["starting_datetime", "value"]]

    # Save the dataframe to a CSV file
    df.to_csv("./data/losses_profiles.csv", index=False)

    # Return the dataframe
    return df
