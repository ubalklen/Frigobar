if __name__ == "__main__":
    import requests

    try:
        r = requests.get("https://www.google.com")
        input(r)
    except Exception as e:
        input(e)
