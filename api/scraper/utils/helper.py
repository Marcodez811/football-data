from io import StringIO
import time, random, requests

HEADERS = open("user-agents.txt", "r").read().splitlines()

def delay_seconds(seconds: int) -> None:
    """
    Delay for the specified number of seconds, used for scraping purposes
    """
    for i in range(seconds):
        print(f"Delaying for {seconds - i} second(s)...")
        time.sleep(1)

def create_header() -> str:
    """
    Create a random header for web scraping
    """
    return {
        "User-Agent": random.choice(HEADERS)
    }

def parse_html(response: requests.Response) -> StringIO:
    return StringIO(response.text)

