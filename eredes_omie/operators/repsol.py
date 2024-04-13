import os

import numpy as np

import erse.losses_profiles
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import omie.energy_prices
import pandas as pd
import utils


def update_prices(
    prices: pd.DataFrame = None, losses_profiles: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Update the Repsol price per kWh including losses and fees.

    Args:
        prices (pandas.DataFrame): Dataframe containing prices data.
        losses_profiles (pandas.DataFrame): Dataframe containing losses data.

    Returns:
        pandas.DataFrame: Dataframe with Repsol price per kWh added.
    """
    # If the prices dataframe is not provided, load the prices data
    if prices is None:
        prices = omie.energy_prices.get_prices()

    # If the losses dataframe is not provided, load the losses data
    if losses_profiles is None:
        losses_profiles = erse.losses_profiles.get_losses_profiles()

    # FA (Adjustment factor) corresponds to the constant 1.03.
    af = 1.03

    # qFare = 0.01479 €/MWh - Cost of Complementary Services
    qfare = 0.01479

    df = pd.merge(prices, losses_profiles, how="inner", on="starting_datetime")

    # Calculates the final price per kWh including losses and fees
    df["€/kWh"] = (df["€/MWh"] / 1000 + 0) * (1 + df["losses_profile"]) * af + qfare

    # Set starting_datetime column dtype to datetime
    df["starting_datetime"] = pd.to_datetime(df["starting_datetime"])

    # Set the exporting columns
    df = df[["starting_datetime", "€/kWh"]]

    # Write the dataframe to a single csv file
    df.to_csv("/workspace/data/repsol_prices.csv", index=False)

    # Group by year and calculate the maximum and minimum price
    max_min_prices = df.groupby(df["starting_datetime"].dt.year)["€/kWh"].agg(
        ["max", "min", "mean"]
    )

    # Print the maximum and minimum price for each year
    print(f"Repsol indexed prices per year (€/kWh):\n{max_min_prices}\n")

    return df


def get_prices() -> pd.DataFrame:
    """
    Loads the Repsol indexed prices data from a CSV file.
    """
    # Load the dataframe from a CSV file
    df = pd.read_csv(
        "/workspace/data/repsol_prices.csv", parse_dates=["starting_datetime"]
    )

    # Return the dataframe
    return df


def plot_day_prices(
    day_df: pd.DataFrame, current_date: pd.Timestamp, save_dir: str
) -> str:
    """
    Plots the Repsol indexed prices for a given day and saves the plot as a PNG file.

    Args:
        day_df (pd.DataFrame): The prices data for the day.
        current_date (pd.Timestamp): The date for which the prices are plotted.
        save_dir (str): The directory where the plot image will be saved.

    Returns:
        str: The path to the generated price plot image.
    """
    # Create a new figure with specified dimensions
    plt.figure(figsize=(10, 6))

    # Plot the '€/kWh' data for the current day
    plt.plot(day_df.index, day_df["€/kWh"], label="Price per kWh")

    # Set the title of the plot
    plt.title(f"Repsol price per kWh on {current_date}")

    # Label the x and y axes
    plt.xlabel("Time")
    plt.ylabel("Price per kWh (€)")

    # Set the y-axis limit
    plt.ylim([0.0, 0.2])

    # Set the x-axis limit
    plt.xlim([day_df.index[0], day_df.index[-1] + pd.Timedelta(minutes=15)])

    # Set the x-axis tick interval to 1 hour
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))

    # Format x-axis ticks as hh:mm
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    # Rotate the x-axis labels for better visibility
    plt.xticks(rotation=45)

    # Calculate statistics
    data_max = np.max(day_df)
    data_min = np.min(day_df)
    data_mean = np.mean(day_df)

    # Create histogram of data
    plt.hist(
        day_df,
        bins=30,
        label=f"Max: {data_max:.6f} €\nMin: {data_min:.6f} €\nMean: {data_mean:.6f} €",
    )
    
    # Add a legend to the plot with right alignment
    legend = plt.legend(loc='upper right', title_fontsize='13', borderaxespad=0., frameon=True)
    plt.setp(legend.get_texts(), ha='right')  # Align text to the right

    # Add a grid to the plot for easier reading
    plt.grid(True)

    # Define the path where the current plot image will be saved
    image_path = f"{save_dir}/repsol/{current_date}.png"

    # Save the current plot as a PNG image at the specified path
    plt.savefig(image_path)

    # Print a message to the console indicating that the plot image has been saved
    print(f"Price plot for {current_date} saved to {image_path}")

    # Close the current plot figure to free up memory
    plt.close()

    return image_path


def plot_prices(
    override: bool = False,
    start_date: str = None,
    debug: bool = False,
) -> str:
    """
    Plots the Repsol indexed prices for each day since a given start date
    and saves each plot as a separate PNG file.

    Args:
        override (bool): If True, overrides the existing plot images.
        start_date (str): The start date to filter the prices data. Defaults to None.
        debug (bool): If True, prints debug information. Defaults to False.

    Returns:
        str: The path to the latest generated price plot image.
    """
    # If start_date is not provided, set it to tomorrow
    if start_date is None:
        start_date = utils.tomorrow()
    else:
        # Convert the provided start_date to a format compatible with Repsol data
        start_date = utils.repsol_start_date(start_date)

    # If the start_date is set to tomorrow and tomorrow's prices are not available yet,
    # set the start_date to today
    if start_date == utils.tomorrow() and not omie.energy_prices.is_available(
        start_date
    ):
        start_date = utils.today()

    # Retrieve the prices data
    df = get_prices()

    # Specify the directory where the plot images will be saved
    save_dir = "/workspace/data/images"

    # Filter the dataframe to include only data from the start_date onwards
    df = df[df["starting_datetime"] >= start_date]

    # Ensure the directory for saving the plot images exists, create it if it doesn't
    os.makedirs(save_dir, exist_ok=True)

    # Initialize the variable to hold the path of the most recently generated image
    latest_image = ""

    # Iterate over each unique day in the dataframe
    for current_date, day_df in df.groupby(df["starting_datetime"].dt.date):
        # Check if an image for the current day already exists
        if not override and os.path.exists(f"{save_dir}/{current_date}.png"):
            # If so, skip this iteration and move to the next day
            continue

        # Set "starting_datetime" column to be the index
        day_df.index = pd.to_datetime(day_df["starting_datetime"])

        # Plot the day's prices and get the image path
        latest_image = plot_day_prices(day_df[["€/kWh"]], current_date, save_dir)

    # Return the path of the most recently generated image
    return latest_image
