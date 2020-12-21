import requests
from collections import Counter

URL = 'https://ip-ranges.amazonaws.com/ip-ranges.json'
REQUEST_TIMEOUT = 5  # seconds
SYNC_FILE = 'last_file_time.txt'


def get_aws_public_addresses():
    request_response = requests.get(URL, timeout=REQUEST_TIMEOUT)
    request_response.raise_for_status()
    if request_response.status_code == requests.codes.ok:
        ip_ranges = request_response.json()
        return ip_ranges
    return None


def get_last_file_time():
    last_file_time = 0  # seconds from epoch
    try:
        with open(SYNC_FILE, 'r') as f:
            last_file_time = int(f.read())
    except FileNotFoundError:
        with open(SYNC_FILE, 'w') as f:
            f.write(str(0))
    return last_file_time


def put_last_file_time(sync_time):
    with open(SYNC_FILE, 'w') as f:
        f.write(str(sync_time))


def process_ip_ranges(ip_ranges):
    ip4_prefixes_count = Counter([(prefix['region'], prefix['service']) for prefix in ip_ranges['prefixes']])
    ip6_prefixes_count = Counter([(prefix['region'], prefix['service']) for prefix in ip_ranges['ipv6_prefixes']])
    prefixes_count = ip4_prefixes_count + ip6_prefixes_count
    return prefixes_count


# Tasks
def aws_public_addresses_task():
    ip_ranges = get_aws_public_addresses()
    if ip_ranges and int(ip_ranges.get('syncToken', '0')) > get_last_file_time():
        prefixes_count = process_ip_ranges(ip_ranges)
        print(prefixes_count)  # TODO: Do something with results ....
        put_last_file_time(ip_ranges['syncToken'])
        return prefixes_count


if __name__ == '__main__':
    aws_public_addresses_task()