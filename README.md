# 🔐 PQ-REACT-QA5G
Post-Quantum Cryptography Integration into a 5G Core using Open5GS and UERANSIM

Future-proofing 5G Core Network Security with Post-Quantum Cryptography (PQC)

# 🧠 Project Overview
As quantum computing continues to advance, legacy encryption methods such as RSA and ECDSA are becoming vulnerable to quantum attacks. PQ-REACT-QA5G is a forward-looking initiative to modernize the 5G core network security infrastructure by integrating Post-Quantum Cryptography (PQC) into a simulated 5G environment using Open5GS and UERANSIM.

The project establishes a self-signed PQC-based certificate authority (CA), generates quantum-resistant certificates using algorithms like Falcon, Dilithium, and Kyber, and deploys them to secure communications across the core network.

# ✨ Features
### 🔹 Network Performance Monitoring
Monitor and evaluate real-time system metrics:

**_CPU Usage (%)_**

**_RAM Usage (%)_**

**_Network Latency (ms)_**

**_Jitter (ms)_**  


  

### 🔹 UE Connection Automation
* Automate User Equipment (UE) connections via UERANSIM:

* Sequential connection of UEs with a 10-second delay between each.

* UEs stay connected indefinitely until terminated manually (via Ctrl + C).

* Automatically navigates to the UERANSIM/build directory before execution.

### 🔹 Subscriber Provisioning & UE YAML Generator
This Python script automates the creation and provisioning of 5G subscribers (UEs) into a core network via REST APIs (compatible with Open5GS or similar). It also generates corresponding YAML configuration files for each UE in a format suitable for use with UEs or simulators.

✨ Features
🔐 Authenticated Login: Secure login with CSRF token handling and session management.

🔄 IMSI Management: Random IMSI generation with configurable prefix and uniqueness check.

📡 Subscriber Provisioning: Adds new UEs to the database via HTTP POST with bearer token + CSRF + session cookie.

📁 YAML Generator: Creates a per-UE YAML file (open5gs-ueX.yaml) with properly quoted nested values for simulator compatibility.

🔍 Existence Check: Prevents duplicate subscriber creation by querying the database beforehand.

✅ Verification: Confirms subscriber creation by fetching and displaying the saved data.

📦 Requirements
* Python 3.x

* requests

* PyYAML

Install dependencies:
> pip install requests pyyaml
🚀 Usage
Simply run the script:
> python subscriber_provisioning.py
You can configure:

* num_subscribers – Number of UEs to generate

* USERNAME, PASSWORD, auth_token – For API access

* BASE_URL – Target server URL

Each IMSI will be dynamically created, checked, provisioned, verified, and then a YAML config file will be saved locally.


### 🔹 Post-Quantum Secure Key & Certificate Generation
* Secure your network using quantum-safe cryptographic primitives:

* A self-signed Post-Quantum Certificate Authority (CA).

* Key pair and certificate generation using PQC algorithms (e.g., Falcon512).

* Signed certificates for Network Functions (NFs) (e.g., AMF, SMF, UPF).

⚠️ PQC algorithms are integrated via liboqs, oqs-provider, and OpenSSL 3.0+.

# 🚀 Usage
Run Network Monitoring
> sudo ./latency_monitor.sh
Continuously monitors and displays system and network metrics.

Run UE Connection Script

> sudo ./connect_all_ues.sh

Starts and connects all UEs with a 10-second delay between each. Keeps them connected until manually stopped.

# ✅ Requirements
To run this project, make sure the following are installed:

_liboqs_

_oqsprovider_

_OpenSSL 3.0+ compiled with oqsprovider_

_Linux, WSL, or any Unix-compatible shell_

🛡️ Why Post-Quantum Now?
Quantum computers won't just break encryption overnight—but they're progressing fast. Deploying quantum-safe infrastructure now is a proactive step toward securing critical networks like 5G, before vulnerabilities are exploited.

Feel free to fork, test, and contribute.

🔗 Project License: Eight Bells Ltd
📫 Contact: vasilisfountas@gmail.com
