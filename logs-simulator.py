#!/usr/bin/env python3
"""
Nginx Logs Simulator
Generates realistic nginx access and error logs for FluentBit testing
"""

import random
import time
from datetime import datetime, timezone
import os

# Directories for logs
LOG_DIR = "logs"
ACCESS_LOG = os.path.join(LOG_DIR, "access.log")
ERROR_LOG = os.path.join(LOG_DIR, "error.log")

# Sample data for realistic logs
REMOTE_ADDRS = [
    "192.168.1.100", "10.0.0.50", "172.16.0.25", "203.0.113.45",
    "198.51.100.10", "192.0.2.100", "8.8.8.8", "1.1.1.1"
]

ENDPOINTS = [
    "/", "/api/users", "/api/products", "/api/orders",
    "/static/css/style.css", "/static/js/app.js",
    "/images/logo.png", "/health", "/metrics",
    "/api/v1/search", "/api/v1/checkout", "/admin/dashboard"
]

HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "curl/7.68.0",
    "Python-urllib/3.9",
    "Go-http-client/1.1"
]

REFERERS = [
    "https://google.com", "https://github.com", "https://stackoverflow.com",
    "-", "https://example.com", "https://localhost:3000"
]

STATUS_CODES = [200, 200, 200, 201, 204, 301, 302, 400, 401, 403, 404, 500, 502, 503]

ERROR_LEVELS = ["error", "warn", "notice", "info", "crit"]

ERROR_MESSAGES = [
    "connect() failed (111: Connection refused) while connecting to upstream",
    "upstream timed out (110: Connection timed out) while reading response header from upstream",
    "client intended to send too large body",
    "SSL_do_handshake() failed",
    "no live upstreams while connecting to upstream",
    "recv() failed (104: Connection reset by peer)",
    "open() \"/var/www/html/favicon.ico\" failed (2: No such file or directory)",
    "access forbidden by rule"
]


def generate_access_log():
    """Generate a single nginx access log entry"""
    remote_addr = random.choice(REMOTE_ADDRS)
    remote_user = "-"
    # Use local timezone with proper formatting
    now = datetime.now().astimezone()
    time_local = now.strftime("%d/%b/%Y:%H:%M:%S %z")
    method = random.choice(HTTP_METHODS)
    endpoint = random.choice(ENDPOINTS)
    protocol = "HTTP/1.1"
    request = f"{method} {endpoint} {protocol}"
    status = random.choice(STATUS_CODES)
    body_bytes_sent = random.randint(100, 50000)
    http_referer = random.choice(REFERERS)
    http_user_agent = random.choice(USER_AGENTS)
    request_length = random.randint(200, 1500)
    request_time = round(random.uniform(0.001, 2.5), 3)
    
    log_line = (
        f'{remote_addr} {remote_user} [{time_local}] '
        f'"{request}" {status} {body_bytes_sent} '
        f'"{http_referer}" "{http_user_agent}" '
        f'{request_length} {request_time}\n'
    )
    return log_line


def generate_error_log():
    """Generate a single nginx error log entry"""
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    level = random.choice(ERROR_LEVELS)
    pid = random.randint(1000, 9999)
    tid = random.randint(0, 99)
    cid = random.randint(100, 999) if random.random() > 0.3 else None
    message = random.choice(ERROR_MESSAGES)
    
    if cid:
        log_line = f"{timestamp} [{level}] {pid}#{tid}: *{cid} {message}\n"
    else:
        log_line = f"{timestamp} [{level}] {pid}#{tid}: {message}\n"
    
    return log_line


def ensure_log_directory():
    """Create logs directory if it doesn't exist"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print(f"Created directory: {LOG_DIR}")


def simulate_logs(duration=None, interval=1):
    """
    Simulate nginx logs continuously
    
    Args:
        duration: How long to run (seconds). None = run forever
        interval: Time between log entries (seconds)
    """
    ensure_log_directory()
    
    print(f"Starting nginx log simulator...")
    print(f"Access logs: {ACCESS_LOG}")
    print(f"Error logs: {ERROR_LOG}")
    print(f"Interval: {interval}s")
    print(f"Duration: {'∞' if duration is None else f'{duration}s'}")
    print("Press Ctrl+C to stop\n")
    
    start_time = time.time()
    count = 0
    
    try:
        while True:
            # Generate access log (more frequent)
            # Open and close file for each write to trigger macOS file watcher
            with open(ACCESS_LOG, 'a') as access_file:
                access_line = generate_access_log()
                access_file.write(access_line)
                access_file.flush()
            count += 1
            
            # Generate error log occasionally (20% chance)
            if random.random() < 0.2:
                with open(ERROR_LOG, 'a') as error_file:
                    error_line = generate_error_log()
                    error_file.write(error_line)
                    error_file.flush()
                print(f"[{count}] Generated access + error log")
            else:
                print(f"[{count}] Generated access log")
            
            # Check if we should stop
            if duration and (time.time() - start_time) >= duration:
                print(f"\nCompleted! Generated {count} log entries in {duration}s")
                break
            
            time.sleep(interval)
                
    except KeyboardInterrupt:
        print(f"\n\nStopped by user. Generated {count} log entries in {time.time() - start_time:.1f}s")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Nginx Logs Simulator for FluentBit")
    parser.add_argument(
        "-d", "--duration",
        type=int,
        help="How long to run (seconds). Default: run forever"
    )
    parser.add_argument(
        "-i", "--interval",
        type=float,
        default=1.0,
        help="Interval between log entries (seconds). Default: 1.0"
    )
    
    args = parser.parse_args()
    
    simulate_logs(duration=args.duration, interval=args.interval)
