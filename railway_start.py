#!/usr/bin/env python3
import os
import subprocess
import sys

print("=== VSB NFS-e Automation System ===")

# Get PORT and ensure it's a valid integer string
port = os.environ.get("PORT", "8501")
print(f"Railway PORT variable: {port}")

# Validate and convert port
try:
    port_int = int(port)
    port = str(port_int)
    print(f"Using port: {port}")
except ValueError:
    print(f"WARNING: Invalid PORT value '{port}', using default 8501")
    port = "8501"

# Clear any Streamlit environment variables that might conflict
env_vars_to_remove = [
    "STREAMLIT_SERVER_PORT",
    "STREAMLIT_SERVER_ADDRESS",
    "STREAMLIT_SERVER_HEADLESS"
]

for var in env_vars_to_remove:
    if var in os.environ:
        del os.environ[var]
        print(f"Removed conflicting env var: {var}")

# Run certificate initialization
print("\n=== Certificate Initialization ===")
result = subprocess.run([sys.executable, "railway_init.py"])
print(f"Certificate init completed with exit code: {result.returncode}\n")

# Start Streamlit with explicit arguments
print(f"=== Starting Streamlit on port {port} ===")
streamlit_cmd = [
    sys.executable, "-m", "streamlit", "run",
    "app_nfse_enhanced.py",
    "--server.port", port,
    "--server.address", "0.0.0.0",
    "--server.headless", "true",
    "--server.enableCORS", "false",
    "--server.enableXsrfProtection", "false"
]

print(f"Command: {' '.join(streamlit_cmd)}")
os.execvp(sys.executable, streamlit_cmd)