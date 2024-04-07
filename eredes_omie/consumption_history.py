import os
import dotenv


def get_credentials() -> tuple[str, str]:
    """
    Retrieves the E-REDES username and password from environment variables.

    Returns:
        tuple[str, str]: A tuple containing the E-REDES username and password.
    """
    dotenv.load_dotenv()
    eredes_username = os.getenv("EREDES_USERNAME") or ""
    eredes_password = os.getenv("EREDES_PASSWORD") or ""

    return eredes_username, eredes_password
