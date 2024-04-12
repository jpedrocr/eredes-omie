# Import the consumption_history module
# import argparse
import argparse
from datetime import date
from e_redes import consumption_history
from omie import prices
from erse import losses_profiles
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
    prices.update_prices()
    repsol.update_prices()


def main(debug: bool) -> None:
    """
    Main function that orchestrates the download of consumption history and prints the URL.
    """

    # download_consumption_history(debug=debug)
    # process_consumption_history(debug=debug)

    # update_losses_profiles(debug=debug)

    update_prices(debug=debug)


# This condition checks if this script is being run directly or imported by another script
# If it is run directly, it calls the main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Turn on debug mode")
    args = parser.parse_args()
    main(args.debug)
