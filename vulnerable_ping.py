from flask import Flask, request, render_template_string
import subprocess
import platform

app = Flask(__name__)

@app.route('/')
def index():
    return '''
        <h1>Network Diagnostic Portal</h1>
        <p>Enter an IP address to check connectivity:</p>
        <form action="/ping" method="get">
            <input type="text" name="target" placeholder="127.0.0.1">
            <input type="submit" value="Run Diagnostics">
        </form>
    '''

@app.route('/ping')
def ping():
    target = request.args.get('target', '127.0.0.1')
    
    # Determine the correct ping flag based on the OS (Windows vs Linux/Mac)
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    
    # FATAL VULNERABILITY: Passing unsanitized user input directly into a system command
    command = f"ping {param} 1 {target}"
    
    try:
        # shell=True allows shell operators like &&, ;, and | to be processed
        output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
        return f"<h3>Diagnostic Results:</h3><pre>{output}</pre>"
    except subprocess.CalledProcessError as e:
        return f"<h3>Diagnostic Failed:</h3><pre>{e.output}</pre>"

if __name__ == '__main__':
    app.run(port=5055)