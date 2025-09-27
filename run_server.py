#!/usr/bin/env python3
import os
import subprocess
import sys

def main():
    # Get port from environment or use default
    port = os.environ.get('PORT', '8000')
    
    # Validate port is numeric
    try:
        port_int = int(port)
        if port_int <= 0 or port_int > 65535:
            raise ValueError("Port out of range")
    except ValueError:
        print(f"❌ Invalid PORT value: {port}, using default 8000")
        port = '8000'
    
    print(f"🚀 Starting Music Atlas on port {port}")
    
    # Start uvicorn
    cmd = [
        'uvicorn', 
        'backend.main:app', 
        '--host', '0.0.0.0', 
        '--port', port
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
