import requests
import time
import os
import subprocess
from librouteros import connect
from librouteros.login import plain as login_plain

# Cloudflare API endpoint
cloudflare_api_url = "https://api.cloudflare.com/client/v4/ips"

# Read environment variables
router_ip = os.getenv('ROUTER_IP', '192.168.88.1')
password = os.getenv('PASSWORD')
username = os.getenv('USERNAME', 'admin')
check_interval = int(os.getenv('CHECK_INTERVAL', 3600))  # Check every hour by default
ifname = os.getenv('IFNAME')
ifListName = os.getenv('IF_LIST_NAME', 'proxyv6')
updateCloudflare = os.getenv('UPDATE_CLOUDFLARE', 'true').lower() == 'true'
# a comma separated list of hostnames to set Mikrotik AAAA Static DNS
v6dnsList = os.getenv('V6DNS_LIST', '')

def get_ipv6_address(ifname='eth0'):
    # Sanitize the input, no non-interface names allowed
    ifname = ifname.strip()

    # Check if the interface name contains any invalid characters
    invalid_chars = [';', '|', '&', '$', '`', '(', ')', '{', '}', '[', ']', '<', '>', '*', '?', '!', '\\', '\'', '\"']
    if any(char in ifname for char in invalid_chars):
        raise ValueError("Invalid characters found in interface name")

    try:
        # Execute ip -6 addr show eth0 command
        result = subprocess.run(['ip', '-6', 'addr', 'show', ifname], capture_output=True, text=True)
        output = result.stdout.strip()
        # Parse the output to extract the IPv6 address
        for line in output.split('\n'):
            if 'inet6' in line and 'scope global' in line:
                return line.split()[1].split('/')[0]  # Extract the IPv6 address
    except Exception as e:
        print(f"Error occurred while fetching eth0 IPv6 address: {e}")
    return None

def fetch_cloudflare_ips():
    response = requests.get(cloudflare_api_url)
    data = response.json()
    ipv6_ranges = set(data['result']['ipv6_cidrs'])
    ipv4_ranges = set(data['result']['ipv4_cidrs'])
    return ipv6_ranges, ipv4_ranges

def connect_to_router():
    return connect(
        username=username,
        password=password,
        host=router_ip,
        login_method=login_plain
    )

def get_existing_address_list(address_list, list_name):
    return {item['address'] for item in address_list.select('.id', 'list', 'address').where(
        {'list': list_name})}

def update_address_list(api, address_list, list_name, new_addresses):
    print(f"Updating {list_name} address list")

    # Remove old or mismatched entries
    for item in address_list.select('.id', 'list', 'address').where({'list': list_name}):
        if item.get('list') == list_name and item['address'] not in new_addresses:
            print(f"Removing {item['address']} from {list_name}")
            address_list.remove(item.get('.id'))

    # Add new entries
    existing_addresses = get_existing_address_list(address_list, list_name)
    for address in new_addresses - existing_addresses:
        print(f"Adding {address} to {list_name}")
        address_list.add(list=list_name, address=address)

def update_v4_address_list(api, list_name, new_addresses):
    address_list = api.path('ip', 'firewall', 'address-list')
    update_address_list(api, address_list, list_name, new_addresses)

def update_v6_address_list(api, list_name, new_addresses):
    address_list = api.path('ipv6', 'firewall', 'address-list')
    update_address_list(api, address_list, list_name, new_addresses)

# Given a list of hostnames, set the AAAA static DNS entries in Mikrotik
def update_v6_dns(api, v6dnsList, new_address):
    print(f"Updating AAAA static DNS entries: {v6dnsList}")
    dns = api.path('ip', 'dns', 'static')
    dnsList = dns.select('.id', 'name', 'address', 'type').where({'type': 'AAAA'})
    for entry in v6dnsList.split(','):
        if entry == '':
            continue
        existing_entry = next((item for item in dnsList if item.get('name') == entry and item.get('type') == 'AAAA'), None)
        if existing_entry:
            print(f"Removing existing DNS entry for {entry}")
            dns.remove(existing_entry.get('.id'))
        print(f"Adding new DNS entry for {entry}")
        dns.add(name=entry, address=new_address, type='AAAA')

def main():
    api = connect_to_router()
    if api is None:
        print("Failed to connect to the router")
        return 1
    
    enabled = False

    if updateCloudflare:
        print("Cloudflare address lists update enabled")
        enabled = True
    else:
        print("Cloudflare address list update disabled")

    if ifname is not None and ifname != "":
        print(f"Interface address list update enabled for {ifname}")
        enabled = True
    else:
        print("Interface address list update disabled")

    if not enabled:
        print("No address list update enabled. Exiting")
        return 1

    cached_ipv6, cached_ipv4 = {}, {}
    cached_interface_ipv6 = ""

    while True:
        try:
            if updateCloudflare:
                current_ipv6, current_ipv4 = fetch_cloudflare_ips()
                print(f"IPv6: {current_ipv6}, IPv4: {current_ipv4}")

                if current_ipv6 != cached_ipv6:
                    update_v6_address_list(api, 'cloudflarev6', current_ipv6)
                    cached_ipv6 = current_ipv6

                if current_ipv4 != cached_ipv4:
                    update_v4_address_list(api, 'cloudflarev4', current_ipv4)
                    cached_ipv4 = current_ipv4

            if ifname is not None and ifname != "":
                # Update the IPv6 address in the interface list
                interface_ipv6 = get_ipv6_address()
                if interface_ipv6:
                    print(f"Interface IPv6: {interface_ipv6}")
                else:
                    print("No IFNAME. Skipping proxyv6 address list update")

                if interface_ipv6 and interface_ipv6 != cached_interface_ipv6:
                    update_v6_address_list(api, 'proxyv6', {interface_ipv6})
                    if v6dnsList != '':
                        update_v6_dns(api, v6dnsList, interface_ipv6)
                    cached_interface_ipv6 = interface_ipv6

        except Exception as e:
            print(f"An error occurred: {e}")

        time.sleep(check_interval)

if __name__ == "__main__":
    main()
