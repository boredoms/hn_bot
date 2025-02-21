import hnapi


def read_token() -> str:
    with open("bot-token") as f:
        token = f.readline()
        return token.strip()


def main():
    print("Hello from hn-bot!")
    token = read_token()


if __name__ == "__main__":
    main()
