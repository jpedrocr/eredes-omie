# Import the consumption_history module
import argparse
import consumption_history as ch


def main(debug: bool) -> None:
    """
    Main function that orchestrates the download of consumption history and prints the URL.
    """
    # Call the download function from the consumption_history module
    # This function is expected to return the URL of the downloaded data
    ch.download(previous_month=True, debug=debug)

    # Print the URL
    print("Downloaded data.")


# This condition checks if this script is being run directly or imported by another script
# If it is run directly, it calls the main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Turn on debug mode")
    args = parser.parse_args()
    main(args.debug)
