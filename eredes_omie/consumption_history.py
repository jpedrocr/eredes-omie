from datetime import date, datetime
from glob import glob
import os
import time
import pandas as pd

import months
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def get_driver(debug: bool = False) -> webdriver.Remote:
    """
    Connects to a Remote WebDriver and returns the driver instance.

    This function sets up a Firefox WebDriver in headless mode and
    connects to a remote Selenium server specified by the `SELENIUM_REMOTE_URL`
    environment variable. If there is an error connecting to the server, it
    prints the error message and raises the exception.

    Returns:
        webdriver.Remote: The connected WebDriver instance.
    """
    # Creating a FirefoxOptions object
    options = webdriver.FirefoxOptions()

    # If not in debug mode
    if not debug:
        # Adding the "--headless" argument to the options
        options.add_argument("--headless")

    driver = None
    try:
        # Creating a Remote WebDriver instance and connecting to the Selenium server
        driver = webdriver.Remote(
            command_executor=os.getenv("SELENIUM_REMOTE_URL"), options=options
        )
        return driver
    except Exception as e:
        # Printing the error message
        print("Error connecting to server:", e)

        # Quitting the driver if it was initialized
        if driver:
            driver.quit()

        # Raising the exception
        raise e


def get_credentials() -> tuple[str, str]:
    """
    Retrieves the E-REDES username and password from environment variables.

    Returns:
        tuple[str, str]: A tuple containing the E-REDES username and password.
    """
    # Getting the E-REDES username from the "EREDES_USERNAME" environment variable
    # If the environment variable is not set, return an empty string
    eredes_username = os.getenv("EREDES_USERNAME", "")

    # Getting the E-REDES password from the "EREDES_PASSWORD" environment variable
    # If the environment variable is not set, return an empty string
    eredes_password = os.getenv("EREDES_PASSWORD", "")

    # Return a tuple containing the E-REDES username and password
    return eredes_username, eredes_password


def find_element(
    driver: webdriver.Remote, by: By, value: str, delay: int = 5
) -> WebElement:
    """
    Finds an element on the web page using the specified driver and element locator.

    Args:
        driver (webdriver.Remote): The Selenium WebDriver instance to use.
        by (By): The locator strategy (e.g., By.XPATH, By.CSS_SELECTOR).
        value (str): The locator value.
        delay (int, optional): The maximum number of seconds to wait for the
        element to be present on the page. Defaults to 5.

    Returns:
        WebElement: The found element.
    """
    # Creating a WebDriverWait object with the specified delay time
    wait = WebDriverWait(driver, delay)

    # Using the until method of the WebDriverWait object to wait until the element is found
    element = wait.until(EC.presence_of_element_located((by, value)))

    # Returning the found element
    return element


def access_eredes_login_page(driver: webdriver.Remote) -> None:
    """Accesses the E-Redes login page."""
    # Click on the 'Reject All' button
    find_element(
        driver=driver, by=By.XPATH, value="//button[contains(.,'Rejeitar Todos')]"
    ).click()

    # Click on the second div inside a list item
    find_element(driver=driver, by=By.XPATH, value="//li/div[2]/div").click()


def login_to_eredes(
    driver: webdriver.Remote, eredes_username: str, eredes_password: str
) -> None:
    """Logs into Eredes with the provided username and password."""
    find_element(driver=driver, by=By.ID, value="username").send_keys(eredes_username)
    find_element(driver=driver, by=By.ID, value="labelPassword").send_keys(
        eredes_password
    )
    find_element(
        driver=driver, by=By.XPATH, value="//button[contains(.,'Entrar')]"
    ).click()


def navigate_to_history(driver: webdriver.Remote) -> None:
    """Navigates to the consumption history page."""
    find_element(
        driver=driver, by=By.XPATH, value="//nz-card/div/div[2]/div", delay=120
    ).click()


def select_month(
    driver: webdriver.Remote, month: int, year: int = date.today().year
) -> None:
    """Navigates to the selected month and year on a webpage using Selenium WebDriver.

    Args:
        driver (webdriver.Remote): The WebDriver instance to interact with the webpage.
        month (int): The month to navigate to (1 for January, 12 for December).
        year (int, optional): The year to navigate to. Defaults to the current year.

    Returns:
        None
    """
    # Calculate the row and column of the month in the date picker
    row = (month - 1) // 3 + 1
    col = (month - 1) % 3 + 1

    # Initialize a WebDriverWait instance with a timeout of 120 seconds
    wait = WebDriverWait(driver, 120)

    # Wait until the month input field is clickable, then click it
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//nz-date-picker[@id='period']/div/input")
        )
    ).click()

    # Get the currently selected year
    selected_year = date.today().year

    # Loop until the selected year matches the desired year
    while year != selected_year:
        # Get the currently selected year from the year button
        selected_year = int(
            find_element(
                driver=driver, by=By.XPATH, value="//month-header/div/div/button"
            ).text
        )

        # If the desired year is less than the selected year, click the previous year button
        if year < selected_year:
            find_element(
                driver=driver, by=By.XPATH, value="//month-header/div/button[1]"
            ).click()
        # If the desired year is greater than the selected year, click the next year button
        elif year > selected_year:
            find_element(
                driver=driver, by=By.XPATH, value="//month-header/div/button[4]"
            ).click()

    # Once the correct year is selected, click the desired month
    find_element(
        driver=driver, by=By.XPATH, value=f"//tr[{row}]/td[{col}]/div", delay=120
    ).click()

    # Wait for 5 seconds to ensure the month is fully loaded
    time.sleep(5)


def export_to_excel(driver: webdriver.Remote) -> None:
    """Exports the consumption history to Excel."""
    find_element(
        driver=driver,
        by=By.XPATH,
        value="//strong[contains(.,'Exportar excel')]",
        delay=120,
    ).click()


def download(previous_month: bool = False, debug: bool = False) -> None:
    """
    Downloads the consumption history from the Eredes website and exports it to an Excel file.

    If `previous_month` is `True`, the function will also download the consumption history for the previous month and save it to a file.

    Args:
        previous_month (bool): If `True`, the function will also download the consumption history for the previous month.
        debug (bool): If `True`, the function will use a headless browser for debugging purposes.

    Raises:
        Exception: If there is an error downloading the consumption history.
    """
    # Load environment variables
    load_dotenv()

    # Get credentials for Eredes
    eredes_username, eredes_password = get_credentials()

    # Get the URL for Eredes consumption history
    eredes_consumption_history_url = os.getenv("EREDES_CONSUMPTION_HISTORY_URL") or ""

    # Get the web driver
    driver = get_driver(debug)

    # If the driver is None, exit the function
    if driver is None:
        return None

    try:
        # Open the Eredes consumption history URL
        driver.get(eredes_consumption_history_url)

        if driver.current_url != eredes_consumption_history_url:
            raise Exception("Invalid URL")

        # Access the E-Redes login page
        access_eredes_login_page(driver)

        # Log into Eredes
        login_to_eredes(driver, eredes_username, eredes_password)

        # Navigate to the consumption history page
        navigate_to_history(driver)

        # Export the consumption history to Excel
        export_to_excel(driver)

        # rename the file
        os.rename(
            f"./downloads/Consumos_{date.today():%Y%m%d}.xlsx",
            f"./downloads/Consumos_{datetime.now():%Y%m%d%H%M%S}.xlsx",
        )

        # If a specific month is provided
        if previous_month:
            # Select the previous month on the webpage
            month = months.get_last_month()
            select_month(driver, month["month"], month["year"])

            # Export the consumption history to Excel
            export_to_excel(driver)

            # rename the file
            os.rename(
                f"./downloads/Consumos_{date.today():%Y%m%d}.xlsx",
                f"./data/consumption_history/Consumos_{month['year']:04}{month['month']:02}.xlsx",
            )

    except Exception as e:
        # Log the error
        print(f"Error downloading: {e}")

        # Quit the driver
        driver.quit()

        # Re-raise the exception
        raise

    # Add a small delay before quitting driver
    time.sleep(5)

    # Quit the driver
    driver.quit()


def process_consumption_history() -> None:
    """
    Processes the consumption history monthly data.
    Loads all the Excel files in data/consumption_history into a Pandas DataFrame and saves it to a CSV file.
    """
    # Get the list of consumption history files
    files = sorted(glob("/workspace/data/consumption_history/*.xlsx"))

    # Initialize a list of dataframes
    dfs = []

    # Loop through the files
    for file in files:
        # print(f"Processing {file}")
        # Load the file into a dataframe
        df = pd.read_excel(
            file,
            sheet_name="Leituras",
            skiprows=14,
        )

        # Append the dataframe to the list
        dfs.append(df)

    # Concatenate the dataframes
    df = pd.concat(dfs)

    # Process the dataframe and save it to a CSV file
    df = process_and_save_dataframe(df)

    # Print the number of rows and columns in the dataframe
    print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")


def process_and_save_dataframe(df: pd.DataFrame = None) -> pd.DataFrame | None:
    """
    Processes the consumption history dataframe, and saves it to a CSV file.
    """

    if df is None:
        # If the dataframe is not provided as an argument, load
        # the dataframe from a CSV file
        df = pd.read_csv("./data/consumption_history.csv")
    elif len(df.columns) == 10:
        # If the dataframe is provided as an argument, and it has
        # 10 columns, drop the columns that are not needed
        df.drop(df.columns[[2, 3, 4, 5, 7, 9]], axis=1, inplace=True)

    # Set the list of column names
    df.columns = [
        "date",
        "time",
        "consumption_kw",
        "injection_kw",
    ]

    # Convert the date and time columns to datetime object in column datetime
    df["starting_datetime"] = pd.to_datetime(df["date"] + " " + df["time"])

    # Subtract 15 minutes from the datetime column
    df["starting_datetime"] = df["starting_datetime"] - pd.Timedelta(minutes=15)

    # Set the datetime column as UTC
    df["starting_datetime"] = df["starting_datetime"].dt.tz_localize("UTC")

    # Add a new columns with the sum of the consumption and injection columns
    df["consumption_kwh"] = df["consumption_kw"] - df["injection_kw"]
    df["injection_kwh"] = df["injection_kw"] - df["consumption_kw"]

    # Set consumption_kwh and injection_kwh to 0 if it is negative
    df["consumption_kwh"] = df["consumption_kwh"].apply(lambda x: 0 if x < 0 else x)
    df["injection_kwh"] = df["injection_kwh"].apply(lambda x: 0 if x < 0 else x)

    # Convert from kW per quarter to kW per hour
    df["consumption_kwh"] = df["consumption_kwh"] / 4
    df["injection_kwh"] = df["injection_kwh"] / 4

    # Print the sum of the consumption and injection columns by year
    print(
        f"Consumption:\n{df.groupby(df["starting_datetime"].dt.year)["consumption_kwh"].sum()}"
    )
    print(
        f"Injection:\n{df.groupby(df['starting_datetime'].dt.year)['injection_kwh'].sum()}"
    )

    # Round the values to 3 decimal places
    df["consumption_kwh"] = df["consumption_kwh"].round(3)
    df["injection_kwh"] = df["injection_kwh"].round(3)

    # Set only the final columns
    df = df[["starting_datetime", "consumption_kwh", "injection_kwh"]]

    # Save the dataframe to a CSV file
    df.to_csv("./data/consumption_history.csv", index=False)

    # Return the dataframe
    return df
