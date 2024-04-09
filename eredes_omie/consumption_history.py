import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


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


def get_driver() -> webdriver.Remote:
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


def access_eredes_login_page(driver):
    """Accesses the E-Redes login page."""
    # Click on the 'Reject All' button
    find_element(driver, (By.XPATH, "//button[contains(.,'Rejeitar Todos')]")).click()

    # Click on the second div inside a list item
    find_element(driver, (By.XPATH, "//li/div[2]/div")).click()


def login_to_eredes(driver, eredes_username, eredes_password):
    """Logs into Eredes with the provided username and password."""
    find_element(driver, (By.ID, "username")).send_keys(eredes_username)
    find_element(driver, (By.ID, "labelPassword")).send_keys(eredes_password)
    find_element(driver, (By.XPATH, "//button[contains(.,'Entrar')]")).click()


def navigate_to_history(driver):
    """Navigates to the consumption history page."""
    find_element(driver, (By.XPATH, "//nz-card/div/div[2]/div")).click()


def export_to_excel(driver):
    """Exports the consumption history to Excel."""
    find_element(
        driver, (By.XPATH, "//strong[contains(.,'Exportar excel')]"), 120
    ).click()


def save_screenshot(driver):
    """Saves a screenshot of the current page if the file exists."""
    if os.path.exists("./data/page_status.png"):
        with open("./data/page_status.png", "wb") as file:
            file.write(driver.get_screenshot_as_png())


def download() -> None:
    # Load environment variables
    load_dotenv()

    # Get credentials for Eredes
    eredes_username, eredes_password = get_credentials()

    # Get the URL for Eredes consumption history
    eredes_consumption_history_url = os.getenv("EREDES_CONSUMPTION_HISTORY_URL") or ""

    # Get the web driver
    driver = get_driver()

    # If the driver is None, exit the function
    if driver is None:
        return None

    try:
        # Open the Eredes consumption history URL
        driver.get(eredes_consumption_history_url)

        # Access the E-Redes login page
        access_eredes_login_page(driver)

        # Log into Eredes
        login_to_eredes(driver, eredes_username, eredes_password)

        # Navigate to the consumption history page
        navigate_to_history(driver)

        # Export the consumption history to Excel
        export_to_excel(driver)

        # Save a screenshot of the current page
        save_screenshot(driver)

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
