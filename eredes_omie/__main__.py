import shutil
from datetime import date

import utils
from e_redes import consumption_history
from erse import losses_profiles
from omie import energy_prices
from operators import repsol


def download_consumption_history(debug: bool = False) -> None:
    """
    Download the consumption history from the E-REDES website.
    If the current day is 2, download the previous month's data as well.
    """
    if date.today().day == 2:
        consumption_history.download(previous_month=True, debug=debug)

    consumption_history.download(previous_month=False, debug=debug)
    print("Downloaded data.")


def process_consumption_history(debug: bool = False) -> None:
    """
    Process the downloaded consumption history.
    """
    consumption_history.process_consumption_history()


def update_losses_profiles(debug: bool = False) -> None:
    """
    Update the losses profiles from the ERSE module.
    """
    losses_profiles.update_losses_profiles()


def update_prices(debug: bool = False) -> None:
    """
    Update the energy prices from the OMIE and REPSOL modules.
    """
    energy_prices.update_prices()
    repsol.update_prices()


def plot_repsol_prices(
    override: bool = False, start_date: str = None, debug: bool = False
) -> None:
    """
    Plot the Repsol prices and save the plot to the workspace.
    """
    location = repsol.plot_prices(start_date=start_date, override=override, debug=debug)
    if location != "":
        shutil.copy(location, "/workspace/repsol_latest_prices.png")


def main(
    history: bool = True,
    prices: bool = True,
    losses: bool = False,
    override: bool = False,
    start_date: str = None,
    debug: bool = False,
) -> None:
    """
    Main function that orchestrates the download and processing of consumption history,
    updating of losses profiles and prices, and plotting of Repsol prices.
    """
    if losses:
        update_losses_profiles(debug=debug)

    if history:
        download_consumption_history(debug=debug)
        process_consumption_history(debug=debug)

    if prices:
        update_prices(debug=debug)

    plot_repsol_prices(override=override, start_date=start_date, debug=debug)


if __name__ == "__main__":
    args = utils.parser_args()
    main(
        history=not args.no_history,
        prices=not args.no_prices,
        losses=args.losses,
        override=args.override,
        start_date=args.start_date,
        debug=args.debug,
    )
