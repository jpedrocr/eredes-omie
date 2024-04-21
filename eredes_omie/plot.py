from datetime import datetime, timedelta
import shutil

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import providers.repsol as repsol

def weekly_energy_consumption(debug: bool = False) -> None:
    """
    Plots the weekly energy consumption for the current month.
    """


    current_month_consumption_history_df = pd.read_csv(
        "/workspace/data/current_month_consumption_history.csv",
        sep=",",
        header=0,
        index_col=0,
        names=["timestamp_utc", "Consumption (kWh)", "Injection (kWh)"],
        dtype={"Consumption (kWh)": "Float64", "Injection (kWh)": "Float64"},
        parse_dates=["timestamp_utc"],
    )
    shelly_consumption_history_df = pd.read_csv(
        "/workspace/data/shelly_consumption_history.csv",
        sep=",",
        header=0,
        index_col=0,
        names=["timestamp_utc", "Grid (kWh)", "Solar (kWh)", "Consumed (kWh)"],
        dtype={
            "Grid (kWh)": "Float64",
            "Solar (kWh)": "Float64",
            "Consumed (kWh)": "Float64",
        },
        parse_dates=["timestamp_utc"],
    )
    e_redes_df = pd.DataFrame()
    e_redes_df.loc[:, "Grid (kWh)"] = (
        +current_month_consumption_history_df.loc[:, "Consumption (kWh)"]
        - current_month_consumption_history_df.loc[:, "Injection (kWh)"]
    )
    combine_df = e_redes_df.combine_first(shelly_consumption_history_df)[["Grid (kWh)"]]
    energy_consumtion_history_df = combine_df.join(
        shelly_consumption_history_df[["Solar (kWh)"]], how="left"
    )
    # Get the current date and time
    today = datetime.now().date()

    # Calculate the date and time for days ago
    days_ago = today - timedelta(days=7)
    days_ago = pd.Timestamp(days_ago).normalize().tz_localize("UTC")

    # Calculate the end of today
    end_of_today = (
        pd.Timestamp(today).normalize().tz_localize("UTC")
        + pd.Timedelta(days=1)
        - pd.Timedelta(seconds=1)
    )

    # Filter the DataFrame to only include data since two days ago
    energy_consumtion_history_df_last_days = energy_consumtion_history_df[
        energy_consumtion_history_df.index >= days_ago
    ]

    repsol_prices_df = repsol.get_prices()
    repsol_prices_df.index = repsol_prices_df["starting_datetime"]
    repsol_prices_df.drop(columns=["starting_datetime"], inplace=True)

    energy_consumtion_history_df_last_days = energy_consumtion_history_df_last_days.join(
        repsol_prices_df, how="left"
    )

    energy_consumtion_history_df_last_days.loc[:, "Grid (€)"] = (
        energy_consumtion_history_df_last_days["€/kWh"]
        * energy_consumtion_history_df_last_days["Grid (kWh)"]
    ).clip(lower=0)

    # Assuming that energy_consumtion_history_df_last_days is your DataFrame
    df = energy_consumtion_history_df_last_days.resample("1h").sum()

    # Calculate the cumulative sum of the 'Grid (€)' column for each day
    df["Grid (€)"] = df.groupby(df.index.day)["Grid (€)"].cumsum()

    # Calculate the date and time for two days ago
    latest_real_timestamp = current_month_consumption_history_df.index.max()

    # Set the style of seaborn
    sns.set_style("whitegrid")

    res: tuple[Figure, tuple[plt.Axes, plt.Axes]] = plt.subplots(
        2, 1, figsize=(15, 10), sharex=True
    )
    fig, (ax1, ax3) = res
    fig.suptitle(
        f"Energy consumption and prices - {days_ago.date()} to {today}", fontsize=16
    )

    ax1.set_xlabel("Time")
    ax1.set_ylabel("Energy (kWh)", color="tab:blue")
    ax1.plot(
        df[df.index <= latest_real_timestamp].index,
        df[df.index <= latest_real_timestamp]["Grid (kWh)"],
        color="tab:blue",
        label="Grid (kWh)",
    )
    ax1.plot(
        df.index,
        df["Solar (kWh)"],
        color="tab:orange",
        label="Solar (kWh)",
    )
    ax1.plot(
        df[df.index > latest_real_timestamp].index,
        df[df.index > latest_real_timestamp]["Grid (kWh)"],
        color="tab:blue",
        linestyle="dashed",
    )
    ax1.tick_params(axis="y", labelcolor="tab:blue")
    ax1.set_ylim(-1.2, 3)  # Set limits for the first y-axis

    # Calculate the max, mean, and min for Grid (kWh)
    max_grid = np.max(df["Grid (kWh)"])
    mean_grid = np.mean(df["Grid (kWh)"])
    min_grid = np.min(df["Grid (kWh)"])

    # Calculate the max, mean, and min for Solar (kWh)
    max_solar = np.max(df["Solar (kWh)"])
    mean_solar = np.mean(df["Solar (kWh)"])

    # Add legends
    legend1 = ax1.legend(
        [
            f"Grid (kWh): Max={max_grid:.6f}, Mean={mean_grid:.6f}, Min={min_grid:.6f}",
            f"Solar (kWh): Max={max_solar:.6f}, Mean={mean_solar:.6f}",
        ],
        loc="upper left",
        framealpha=0.5,
    )

    # Set x-axis limits
    ax1.set_xlim([days_ago, end_of_today])

    # Add the legend manually to the current Axes.
    ax1.add_artist(legend1)

    ax2 = ax1.twinx()
    color = "tab:red"
    ax2.set_ylabel("Cost (€)", color=color)
    # Plot with different styles based on the date
    ax2.plot(
        df[df.index <= latest_real_timestamp].index,
        df[df.index <= latest_real_timestamp]["Grid (€)"],
        color=color,
        label="Grid (€)",
    )
    ax2.plot(
        df[df.index > latest_real_timestamp].index,
        df[df.index > latest_real_timestamp]["Grid (€)"],
        color=color,
        linestyle="dashed",
    )
    ax2.tick_params(axis="y", labelcolor=color)
    ax2.set_ylim(0, 0.6)  # Set limits for the second y-axis

    # Calculate the max, mean, and min for Grid (€)
    max_grid_euro = np.max(
        energy_consumtion_history_df_last_days["Grid (€)"].resample("1D").sum()
    )
    mean_grid_euro = np.mean(
        energy_consumtion_history_df_last_days["Grid (€)"].resample("1D").sum()
    )

    # Add legend
    ax2.legend(
        [f"Grid (€): Max={max_grid_euro:.6f}, Mean={mean_grid_euro:.6f}"],
        loc="upper right",
        framealpha=0.5,
    )

    # Move the third axis to the right side
    # ax3.spines["right"].set_position(("outward", 60))

    # Plot the €/kWh on the third y-axis
    ax3.plot(
        repsol_prices_df.index,
        repsol_prices_df["€/kWh"],
        color="tab:green",
        linewidth=1,
        label="€/kWh",
        alpha=0.7,
    )
    ax3.set_ylabel("Price (€/kWh)", color="tab:green")
    ax3.yaxis.tick_right()
    ax3.yaxis.set_label_position("right")
    ax3.tick_params(axis="y", labelcolor="tab:green")

    # filter repsol_prices_df to the last 7 days
    repsol_prices_df = repsol_prices_df[repsol_prices_df.index >= days_ago]

    # Calculate the max, mean, and min for €/kWh
    max_euro_per_kwh = np.max(repsol_prices_df["€/kWh"])
    mean_euro_per_kwh = np.mean(repsol_prices_df["€/kWh"])
    min_euro_per_kwh = np.min(repsol_prices_df["€/kWh"])

    # Set limits to the third y-axis
    ax3.set_ylim(0.01, max_euro_per_kwh + 0.005)

    # Add legend for the third y-axis
    ax3.legend(
        [
            f"€/kWh: Max={max_euro_per_kwh:.6f}, Mean={mean_euro_per_kwh:.6f}, Min={min_euro_per_kwh:.6f}"
        ],
        loc="upper right",
        framealpha=0.5,
    )

    fig.tight_layout()
    # Save the current plot as a PNG image at the specified path
    plt.savefig("/workspace/weekly_energy.png")
    plt.show()


def providers_indexed_prices(
    start_date: str = None, override: bool = False, debug: bool = False
) -> None:
    """
    Plot the Repsol prices and save the plot to the workspace.
    """
    location = repsol.plot_prices(start_date=start_date, override=override, debug=debug)
    if location != "":
        shutil.copy(location, "/workspace/repsol_latest_prices.png")