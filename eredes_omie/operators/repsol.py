import pandas as pd
import eredes_omie.erse.losses_profiles as lp
import eredes_omie.omie.prices as pr

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
        prices = pr.get_prices()

    # If the losses dataframe is not provided, load the losses data
    if losses_profiles is None:
        losses_profiles = lp.get_losses_profiles()

    # FA (Adjustment factor) corresponds to the constant 1.03.
    af = 1.03

    # qFare = 0.01479 €/MWh - Cost of Complementary Services
    qfare = 0.01479

    df = pd.merge(prices, losses_profiles, how="inner", on="starting_datetime")

    # Calculates the final price per kWh including losses and fees
    df["€/kWh"] = (df["€/MWh"] / 1000 + 0) * (1 + df["losses_profile"]) * af + qfare

    # Write the dataframe to a single csv file
    df.to_csv("/workspace/data/repsol_prices.csv", index=False)

    return df[["starting_datetime", "€/kWh"]]
