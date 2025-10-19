import os
import re
import platform
import socket
import subprocess
from flask import Flask, render_template, request, jsonify, abort

app = Flask(__name__, static_folder='static', template_folder='templates')

# validate host: allow letters numbers dots hyphens and colons (for IPv6) and no long input
HOST_REGEX = re.compile(r"^[A-Za-z0-9\.\-:\[\]]{1,255}$")

def validate_host(host: str) -> bool:
    if not host or len(host) > 255:
        return False
    return bool(HOST_REGEX.match(host))


def run_ping(host: str):
    if not validate_host(host):
        return 'Invalid host'
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    cmd = ['ping', param, '4', host]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True, timeout=20)
        return out
    except subprocess.CalledProcessError as e:
        return e.output
    except subprocess.TimeoutExpired:
        return 'Ping timed out'


def run_traceroute(host: str):
    if not validate_host(host):
        return 'Invalid host'
    if platform.system().lower() == 'windows':
        cmd = ['tracert', host]
    else:
        cmd = ['traceroute', host]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True, timeout=60)
        return out
    except subprocess.CalledProcessError as e:
        return e.output
    except subprocess.TimeoutExpired:
        return 'Traceroute timed out'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/ping', methods=['POST'])
def api_ping():
    host = request.json.get('host') if request.is_json else request.form.get('host')
    if not host:
        return jsonify({'error': 'host required'}), 400
    result = run_ping(host)
    return jsonify({'output': result})


@app.route('/api/traceroute', methods=['POST'])
def api_traceroute():
    host = request.json.get('host') if request.is_json else request.form.get('host')
    if not host:
        return jsonify({'error': 'host required'}), 400
    result = run_traceroute(host)
    return jsonify({'output': result})


@app.route('/api/server-info')
def api_server_info():
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
    except Exception:
        ip_address = 'unknown'
    os_info = platform.platform()
    return jsonify({'hostname': hostname, 'ip_address': ip_address, 'os_info': os_info})


@app.route('/api/server-speedtest')
def api_server_speedtest():
    # disabled by default; enable with ALLOW_SERVER_SPEEDTEST=1 env var
    if os.environ.get('ALLOW_SERVER_SPEEDTEST') != '1':
        return jsonify({'error': 'server speedtest disabled'}), 403
    try:
        import speedtest
        st = speedtest.Speedtest()
        download = st.download() / 1_000_000
        upload = st.upload() / 1_000_000
        return jsonify({'download_mbps': round(download,2), 'upload_mbps': round(upload,2)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
