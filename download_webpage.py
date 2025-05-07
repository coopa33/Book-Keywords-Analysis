from requests import get, RequestException
from contextlib import closing
import time

def simple_get(url, max_retries=3):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    Retry up to `max_retries` times on HTTP errors with a 1-second delay.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'
        }
        for _ in range(max_retries):
            with closing(get(url, stream=True, headers=headers)) as resp:
                if is_good_response(resp):
                    return resp.content
                else:
                    print(f"Recieved a HTTP {resp.status_code} ERROR for {url}.")
                    print("Retrying in 1 second...")
                    time.sleep(1)
        print("-------------------------------------")
        print(f"Retrieving {url} FAILED. Visit this URL in your browser to confirm correctness.")
        print("-------------------------------------")
        return None
    except RequestException as e:
        print(f"The following error occurred during HTTP GET request to {url}: {str(e)}")
        return None

def is_good_response(resp):
    """
    Returns true if the response seems to be HTML, false otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1) 
