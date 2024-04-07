import consumption_history as consumption_history


def main():
    eredes_username, _ = consumption_history.get_credentials()
    print(eredes_username)


if __name__ == "__main__":
    main()
