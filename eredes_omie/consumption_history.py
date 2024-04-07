import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def find_element(driver, element):
    wait = WebDriverWait(driver, 5000)
    value = wait.until(EC.presence_of_element_located((element)))
    return value


def get_credentials() -> tuple[str, str]:
    """
    Retrieves the E-REDES username and password from environment variables.

    Returns:
        tuple[str, str]: A tuple containing the E-REDES username and password.
    """
    eredes_username = os.getenv("EREDES_USERNAME") or ""
    eredes_password = os.getenv("EREDES_PASSWORD") or ""

    return eredes_username, eredes_password


def get_driver() -> webdriver.Remote:
    """
    Connect to a Remote WebDriver.
    """
    server = os.getenv("SELENIUM_REMOTE_URL") or ""
    options = webdriver.FirefoxOptions()
    print(f"{server = }")
    driver = webdriver.Remote(command_executor=server, options=options)
    try:
        assert "firefox" in driver.command_executor._url
        print(f"{driver.command_executor._url = }")
    except Exception:
        print("Error connecting to server")
        print(f"{Exception = }")
        driver.quit()
        return None
    return driver


def download(month: str = "Março") -> str | None:
    load_dotenv()
    eredes_username, eredes_password = get_credentials()
    eredes_consumption_history_url = os.getenv("EREDES_CONSUMPTION_HISTORY_URL") or ""
    driver = get_driver()

    if driver is None:
        return None

    try:
        driver.get(eredes_consumption_history_url)

        reject_cookies = find_element(
            driver, (By.XPATH, "//button[contains(.,'Rejeitar Todos')]")
        )
        ActionChains(driver).click(reject_cookies).perform()

        private_costumer = find_element(driver, (By.XPATH, "//li/div[2]/div"))
        ActionChains(driver).click(private_costumer).perform()

        # create a new file with the name of the month
        if os.path.exists(f"./data/{month}.png"):
            with open(f"./data/{month}.png", "wb") as file:
                file.write(driver.get_screenshot_as_png())
    except Exception as e:
        print("Error downloading")
        driver.quit()
        raise e

    time.sleep(10)
    driver.quit()
    print("Done")
    return f"./data/{month}.png"
