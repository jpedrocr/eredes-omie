import consumption_history as consumption_history

def main():
    url = consumption_history.download()
    print(f"{url = }")


if __name__ == "__main__":
    main()
