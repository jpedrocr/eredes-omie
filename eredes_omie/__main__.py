# Import the consumption_history module
import argparse
import shutil
from datetime import date

from e_redes import consumption_history
from erse import losses_profiles
from omie import energy_prices
from operators import repsol


def download_consumption_history(debug: bool = False) -> None:
    """
    Download the consumption history from the E-REDES website.
    """
    # If the current day is 2, download the previous month
    if date.today().day == 2:
        consumption_history.download(previous_month=True, debug=debug)

    # Call the download function from the consumption_history module
    consumption_history.download(previous_month=False, debug=debug)

    # Print the URL
    print("Downloaded data.")


def process_consumption_history(debug: bool = False) -> None:
    """
    Process the consumption history.
    """
    consumption_history.process_consumption_history()


def update_losses_profiles(debug: bool = False) -> None:
    """
    Update the losses profiles.
    """
    losses_profiles.update_losses_profiles()


def update_prices(debug: bool = False) -> None:
    """
    Update the prices.
    """
    energy_prices.update_prices()
    repsol.update_prices()


def plot_repsol_prices(debug: bool = False) -> None:
    """
    Plot the Repsol prices.
    """
    # Load the latest plot figure location
    location = repsol.plot_prices()

    # Copy the figure to the folder /workspace/ folder with filename as repsol_prices.png
    if location != "":
        shutil.copy(location, "/workspace/repsol_latest_prices.png")


def main(history: bool = True, losses: bool = False, debug: bool = False) -> None:
    """
    Main function that orchestrates the download of consumption history and prints the URL.
    """
    if losses:
        update_losses_profiles(debug=debug)

    if history:
        download_consumption_history(debug=debug)
        process_consumption_history(debug=debug)

    update_prices(debug=debug)
    plot_repsol_prices(debug=debug)


# This condition checks if this script is being run directly or imported by another script
# If it is run directly, it calls the main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Turn on debug mode")
    parser.add_argument("--losses", action="store_true", help="Update losses profiles")
    parser.add_argument(
        "--no-history", action="store_true", help="Do not update consumption history"
    )
    args = parser.parse_args()
    main(history=not args.no_history, losses=args.losses, debug=args.debug)
