# Nginx Logs Simulator

A Python script that generates realistic nginx access and error logs for testing FluentBit log ingestion to ClickHouse.

## Features

- Generates nginx access logs matching the format expected by FluentBit's `nginx_access` parser
- Generates nginx error logs matching the format expected by FluentBit's `nginx_error` parser
- Closes files after each write to trigger file change notifications on macOS
- Configurable duration and interval between log entries
- Realistic sample data (IPs, endpoints, status codes, user agents, etc.)

## Usage

### Basic Usage

Generate logs continuously (press Ctrl+C to stop):
```bash
python3 logs-simulator.py
```

### With Duration

Run for a specific duration (in seconds):
```bash
python3 logs-simulator.py -d 60
```

### With Custom Interval

Generate logs every 0.5 seconds:
```bash
python3 logs-simulator.py -i 0.5
```

### Combined Options

Run for 30 seconds with 0.3s interval:
```bash
python3 logs-simulator.py -d 30 -i 0.3
```

## Output

Logs are written to:
- `logs/access.log` - Nginx access logs
- `logs/error.log` - Nginx error logs

## Docker Integration

The logs are mounted into the FluentBit container at `/var/log/simulator/` and are automatically:
1. Read by FluentBit's tail input
2. Parsed using the `nginx_access` and `nginx_error` parsers
3. Sent to ClickHouse via HTTP

## Log Formats

### Access Log Format
```
<remote_addr> <remote_user> [<time_local>] "<request>" <status> <body_bytes_sent> "<http_referer>" "<http_user_agent>" <request_length> <request_time>
```

Example:
```
192.168.1.100 - [12/Feb/2026:19:58:28 +0200] "GET /api/users HTTP/1.1" 200 1234 "https://google.com" "curl/7.68.0" 500 0.123
```

### Error Log Format
```
<timestamp> [<level>] <pid>#<tid>: *<cid> <message>
```

Example:
```
2026/02/12 19:58:28 [error] 1234#56: *789 connect() failed (111: Connection refused)
```

## Viewing Logs in ClickHouse

```bash
# Count total logs
docker exec clickhouse clickhouse-client --query "SELECT count(*) FROM estavo.nginx_logs"

# View sample logs
docker exec clickhouse clickhouse-client --query "SELECT * FROM estavo.nginx_logs LIMIT 10"

# Statistics
docker exec clickhouse clickhouse-client --query "SELECT countDistinct(remote_addr) as unique_ips, countDistinct(status) as status_codes FROM estavo.nginx_logs"
```

## Notes

- The script closes the file after each write to ensure macOS file watchers detect changes
- FluentBit uses `Refresh_Interval 1` to poll for file changes every second
- ClickHouse stores `time_local` as a String to avoid timezone parsing issues
