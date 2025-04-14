import requests
import json
import random
import yaml

BASE_URL = "http://127.0.0.1:9999"  # Change to your real base URL

# Manual Bearer token
auth_token = "<_TOKEN_>"

# Login credentials
USERNAME = "admin"
PASSWORD = "1423"

def get_csrf_token(session):
    print("Fetching CSRF token...")
    resp = session.get(f"{BASE_URL}/api/auth/csrf", timeout=10)
    resp.raise_for_status()
    token = resp.json().get('csrfToken')
    if not token:
        raise Exception("CSRF token not found.")
    return token

def login(session, csrf_token):
    print("Logging in...")
    login_data = {
        "username": USERNAME,
        "password": PASSWORD,
        "_csrf": csrf_token
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    resp = session.post(
        f"{BASE_URL}/api/auth/login",
        data=login_data,
        headers=headers,
        timeout=10
    )
    if resp.status_code != 200:
        raise Exception(f"Login failed: {resp.status_code} - {resp.text}")
    return session.cookies.get('connect.sid')

def check_imsi_exists(imsi):
    url = f"{BASE_URL}/api/db/Subscriber/{imsi}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {auth_token}"})
    if resp.status_code == 200:
        print(f"IMSI {imsi} already exists.")
        return True
    elif resp.status_code == 404:
        return False
    else:
        print(f"Unexpected error checking IMSI: {resp.status_code}")
        return False

def add_subscriber(session, imsi, connect_sid, csrf_token):
    print(f"Adding new UE with IMSI {imsi}...")

    new_ue_data = {
        "imsi": imsi,
        "security": {
            "k": "465B5CE8B199B49FAA5F0A2EE238A6BC",
            "amf": "8000",
            "op_type": 0,
            "op_value": "E8ED289DEBA952E4283B54E88E6183CA",
            "opc": "E8ED289DEBA952E4283B54E88E6183CA"
        },
        "ambr": {
            "downlink": {"value": 1, "unit": 3},
            "uplink": {"value": 1, "unit": 3}
        },
        "subscriber_status": 0,
        "operator_determined_barring": 0,
        "slice": [{
            "sst": 1,
            "default_indicator": True,
            "session": [{
                "name": "internet",
                "type": 3,
                "ambr": {"downlink": {"value": 1, "unit": 3}, "uplink": {"value": 1, "unit": 3}},
                "qos": {"index": 9, "arp": {"priority_level": 8, "pre_emption_capability": 1, "pre_emption_vulnerability": 1}}
            }]}]
    }

    headers = {
        "Content-Type": "application/json",
        "X-CSRF-TOKEN": csrf_token,
        "Authorization": f"Bearer {auth_token}",
        "Cookie": f"connect.sid={connect_sid}"
    }

    resp = session.post(
        f"{BASE_URL}/api/db/Subscriber",
        json=new_ue_data,
        headers=headers,
        timeout=10
    )

    if resp.status_code == 201:
        print(f"✅ IMSI {imsi} added successfully.")
    else:
        print(f"❌ Failed to add IMSI {imsi}: {resp.status_code} - {resp.text}")

def verify_subscriber(imsi):
    url = f"{BASE_URL}/api/db/Subscriber/{imsi}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {auth_token}"})
    if resp.status_code == 200:
        print("Verification successful. Subscriber data:")
        print(json.dumps(resp.json(), indent=2))
    else:
        print(f"Verification failed for IMSI {imsi}: {resp.status_code}")

def generate_yaml_for_ue(imsi, ue_number):
    """Generate YAML file for each UE"""
    data = {
        "supi": f"imsi-{imsi}",
        "mcc": "999",
        "mnc": "70",
        "protectionScheme": 0,
        "homeNetworkPublicKey": "5a8d38864820197c3394b92613b20b91633cbd897119273bf8e4a6f4eec0a650",
        "homeNetworkPublicKeyId": 1,
        "routingIndicator": "0000",
        "key": "465B5CE8B199B49FAA5F0A2EE238A6BC",
        "op": "E8ED289DEBA952E4283B54E88E6183CA",
        "opType": "OPC",
        "amf": "8000",
        "imei": "356938035643803",
        "imeiSv": "4370816125816151",
        "tunNetmask": "255.255.255.0",
        "gnbSearchList": ["127.0.0.1"],
        "uacAic": {
            "mps": False,
            "mcs": False
        },
        "uacAcc": {
            "normalClass": 0,
            "class11": False,
            "class12": False,
            "class13": False,
            "class14": False,
            "class15": False
        },
        "sessions": [{
            "type": "IPv4",
            "apn": "internet",
            "slice": {
                "sst": 1
            }
        }],
        "configured-nssai": [{
            "sst": 1
        }],
        "default-nssai": [{
            "sst": 1,
            "sd": 1
        }],
        "integrity": {
            "IA1": True,
            "IA2": True,
            "IA3": True
        },
        "ciphering": {
            "EA1": True,
            "EA2": True,
            "EA3": True
        },
        "integrityMaxRate": {
            "uplink": "full",
            "downlink": "full"
        }
    }

    # Write YAML file
    filename = f"open5gs-ue{ue_number}.yaml"
    with open(filename, "w") as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)
    print(f"Generated {filename} for IMSI {imsi}.")

def process_imsi(imsi, ue_number):
    with requests.Session() as session:
        try:
            csrf_token = get_csrf_token(session)
            connect_sid = login(session, csrf_token)
            csrf_token = get_csrf_token(session)  # Refresh after login

            if check_imsi_exists(imsi):
                print(f"Skipping IMSI {imsi}, already exists.")
                return

            add_subscriber(session, imsi, connect_sid, csrf_token)
            verify_subscriber(imsi)
            generate_yaml_for_ue(imsi, ue_number)  # Generate the YAML file after successful addition

        except Exception as e:
            print(f"Error processing IMSI {imsi}: {e}")

# === MAIN: Dynamic IMSI Loop with Randomization ===

def generate_random_imsi(prefix="999706", length=15):
    """Generate a random IMSI with the given prefix and total length."""
    remaining_digits = length - len(prefix)
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(remaining_digits)])
    return prefix + suffix

num_subscribers = 10  # Adjust as needed
generated_imsis = set()

for i in range(1, num_subscribers + 1):
    while True:
        current_imsi = generate_random_imsi()
        if current_imsi not in generated_imsis:
            generated_imsis.add(current_imsi)
            break
    print(f"\n=== Processing IMSI {current_imsi} ===")
    process_imsi(current_imsi, i)
