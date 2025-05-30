from flask import Flask, request, Response
import subprocess
import os
import sys

app = Flask(__name__)

# 🔧 Config
CERT_PATH = os.path.abspath("./certs/ca.crt")
CURL_IMAGE = "openquantumsafe/curl"
PORT_TO_SERVICE = {
    8081: ("127.0.0.1", "8443"),  # NRF
    8082: ("127.0.0.1", "8444"),  # AUSF
    8083: ("127.0.0.1", "8445"),  # AMF
}

@app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@app.route('/<path:path>', methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def proxy(path):
    # Determine the service based on port
    local_port = int(request.environ.get('SERVER_PORT', 0))
    upstream_info = PORT_TO_SERVICE.get(local_port)

    if not upstream_info:
        return Response("Unknown local port for upstream mapping.", status=400)

    UPSTREAM_HOST, UPSTREAM_PORT = upstream_info

    # Build full URL
    query_string = request.query_string.decode()
    upstream_url = f"https://{UPSTREAM_HOST}:{UPSTREAM_PORT}/{path}"
    if query_string:
        upstream_url += f"?{query_string}"

    curl_cmd = [
        "curl", "--cacert", "/tmp/ca.crt",
        "-X", request.method,
        "-s", "-k", "-v",
        upstream_url
    ]

    for header, value in request.headers.items():
        curl_cmd += ["-H", f"{header}: {value}"]

    if request.data:
        curl_cmd += ["--data-binary", "@-"]

    docker_cmd = [
        "sudo", "docker", "run", "--rm", "-i",
        "--network", "host",
        "-v", f"{CERT_PATH}:/tmp/ca.crt",
        CURL_IMAGE
    ] + curl_cmd

    try:
        result = subprocess.run(
            docker_cmd,
            input=request.get_data(),
            capture_output=True,
            check=True
        )
        return Response(result.stdout, status=200)
    except subprocess.CalledProcessError as e:
        return Response(f"[ERROR] curl failed:\n{e.stderr.decode()}", status=502, mimetype="text/plain")

if __name__ == "__main__":
    from werkzeug.serving import run_simple
    # Start on 3 ports simultaneously using run_simple
    from threading import Thread

    def run_proxy(port):
        run_simple('0.0.0.0', port, app, use_reloader=False)

    for port in [8081, 8082, 8083]:
        Thread(target=run_proxy, args=(port,), daemon=True).start()

    # Keep main thread alive
    import time
    while True:
        time.sleep(100)

