# Import the consumption_history module
# import argparse
from datetime import date
import consumption_history as ch
import losses_profiles as lp


def main(debug: bool) -> None:
    """
    Main function that orchestrates the download of consumption history and prints the URL.
    """

    # If the current day is 2, download the previous month
    if date.today().day == 2:
        ch.download(previous_month=True, debug=debug)

    # Call the download function from the consumption_history module
    ch.download(previous_month=False, debug=debug)

    # Print the URL
    print("Downloaded data.")


# This condition checks if this script is being run directly or imported by another script
# If it is run directly, it calls the main function
if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--debug", action="store_true", help="Turn on debug mode")
    # args = parser.parse_args()
    # main(args.debug)
    # ch.process_consumption_history()
    lp.get_losses_profiles()
