from glob import glob
import pandas as pd


def update_losses_profiles() -> pd.DataFrame:
    """
    Updates and saves the losses profiles data from Excel files in the "/workspace/data/losses_profiles/" directory.

    Returns:
        pd.DataFrame: The updated losses profiles data.
    """
    # Get the list of losses profiles files
    files = sorted(glob("/workspace/data/losses_profiles/*.xlsx"))

    # Initialize a list of dataframes
    dfs = []

    # Loop through the files
    for file in files:
        print(f"\nProcessing {file}")
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

    # Set column names to date, time, losses_profile
    df.columns = ["date", "time", "losses_profile"]

    # Convert the 'date' column to datetime
    df["date"] = pd.to_datetime(df["date"])

    # Append ':00' to 'time' column and convert it to timedelta
    df["time"] = pd.to_timedelta(df["time"] + ":00")

    # Subtract 15 minutes to get the starting time of the interval
    df["starting_time"] = df["time"] - pd.Timedelta(minutes=15)

    # Combine the 'date' and 'starting_time' to create a 'starting_datetime' column
    df["starting_datetime"] = df["date"] + df["starting_time"]

    # Set the 'starting_datetime' column as UTC
    df["starting_datetime"] = df["starting_datetime"].dt.tz_localize("UTC")

    # Set only the final columns
    df = df[["starting_datetime", "losses_profile"]]

    # Save the dataframe to a CSV file
    df.to_csv("/workspace/data/losses_profiles.csv", index=False)

    # Return the dataframe
    return df


def get_losses_profiles() -> pd.DataFrame:
    """
    Loads the losses profiles data from a CSV file.

    Returns:
        pd.DataFrame: A DataFrame containing the losses profiles data.
    """
    # Load the dataframe from a CSV file
    df = pd.read_csv("/workspace/data/losses_profiles.csv")

    # Return the dataframe
    return df
