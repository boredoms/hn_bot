def read_token() -> str:
    with open("bot-token") as f:
        token = f.readline()
        return token


def main():
    print("Hello from hn-bot!")
    token = read_token()
    print(f"Token: {token}")


if __name__ == "__main__":
    main()
