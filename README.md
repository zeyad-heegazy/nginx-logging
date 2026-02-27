# Nginx Logging Pipeline

Collects nginx access and error logs from multiple sources, parses and enriches them with FluentBit, and stores them in ClickHouse for querying.

## Architecture

```
nginx (host / brokers / remote / simulator)
        │  log files
        ▼
   FluentBit  (tail → Lua enrichment → grep filter → HTTP output)
        │
        ▼
  ClickHouse  estavo.nginx_logs / estavo.nginx_error_logs
```

### Log sources

| FluentBit tag      | Log file (inside container)              | Parser         | Destination table           |
|--------------------|------------------------------------------|----------------|-----------------------------|
| `nginx.access`     | `/var/log/nginx/access.log`              | `json`         | `estavo.nginx_logs`         |
| `nginx.error`      | `/var/log/nginx/error.log`               | `nginx_error`  | `estavo.nginx_error_logs`   |
| `brokers.access`   | `/var/log/nginx/api-brokers.access.log`  | `nginx_access` | `estavo.nginx_logs`         |
| `remote.access`    | `/var/log/remote-nginx/access.log`       | `nginx_access` | `estavo.nginx_logs`         |
| `simulator.access` | `/var/log/simulator/access.log`          | `nginx_access` | stdout (debug)              |

The Lua filter (`extract_resource.lua`) runs on every access tag and populates `resource_type` and `resource_id` from the request URI. OPTIONS requests are excluded before insertion.

---

## Prerequisites

- Docker and Docker Compose
- nginx running on the host writing logs to `/var/log/nginx/` (either JSON `json_combined` format or the custom combined format — see [Log Formats](#log-formats))
- macOS: grant Docker Desktop read access to `/var/log/nginx` in **Settings → Resources → File Sharing**

---

## Deployment

### 1. Clone the repository

```bash
git clone <repo-url>
cd nginx-logging
```

### 2. Create required local directories

FluentBit needs writable state and log directories present before the container starts:

```bash
mkdir -p fluentbit/state logs remote-nginx-logs
```

### 3. Start the stack

```bash
docker compose up -d
```

This starts:
- **clickhouse** — HTTP on port `8123`, native on port `9000`
- **fluentbit** — mounts `/var/log/nginx` from the host, `./logs` as the simulator source, and `./remote-nginx-logs` as the remote source

### 4. Verify the stack is healthy

```bash
docker compose ps
docker compose logs fluentbit --tail=30
docker compose logs clickhouse --tail=20
```

FluentBit should print `[engine] started` with no parser or config errors. ClickHouse should print `Ready for connections`.

### 5. Confirm tables exist

```bash
docker compose exec clickhouse clickhouse-client \
  -q "SHOW TABLES FROM estavo"
```

Expected output: `nginx_error_logs` and `nginx_logs`.

---

## Testing

### Option A — Inject a row directly into ClickHouse (schema smoke test)

```bash
# Access log row
echo '{"time_local":"27/Feb/2026:12:00:00 +0000","remote_addr":"1.2.3.4","request_method":"GET","request_uri":"/api/users/42","resource_type":"users","resource_id":42,"status":200,"body_bytes_sent":512,"request_time":0.05,"http_referer":"-","http_user_agent":"curl/8.0","real_ip":"1.2.3.4","uid":null}' \
  | docker compose exec -T clickhouse clickhouse-client \
      -q "INSERT INTO estavo.nginx_logs FORMAT JSONEachRow"

# Error log row
echo '{"time":"2026-02-27 12:00:00","level":"error","pid":1,"tid":2,"cid":0,"message":"upstream timed out"}' \
  | docker compose exec -T clickhouse clickhouse-client \
      -q "INSERT INTO estavo.nginx_error_logs FORMAT JSONEachRow"
```

Verify:
```bash
docker compose exec clickhouse clickhouse-client \
  -q "SELECT count() FROM estavo.nginx_logs; SELECT count() FROM estavo.nginx_error_logs"
```

### Option B — End-to-end via FluentBit (simulator source)

FluentBit tails `logs/access.log` as the `simulator.access` tag and prints matched records to stdout:

```bash
echo '1.2.3.4 - - [27/Feb/2026:12:00:00 +0000] "GET /api/orders/7 HTTP/1.1" 200 1024 rt:0.05 "-" "curl/8.0" "1.2.3.4" uid:99' \
  >> logs/access.log

docker compose logs fluentbit --tail=10
```

You should see the parsed JSON record printed within a second or two.

### Option C — End-to-end via FluentBit (brokers source)

```bash
echo '1.2.3.4 - - [27/Feb/2026:12:00:00 +0000] "POST /api/brokers/3 HTTP/1.1" 201 256 rt:0.12 "-" "Mozilla/5.0" "1.2.3.4" uid:5' \
  >> logs/api-brokers.access.log

# Wait ~2 s then query ClickHouse
docker compose exec clickhouse clickhouse-client \
  -q "SELECT request_method, request_uri, resource_type, resource_id, status FROM estavo.nginx_logs ORDER BY time_local DESC LIMIT 5"
```

### Option D — Bulk-load an existing log file

```bash
docker compose exec -T clickhouse clickhouse-client \
  -q "INSERT INTO estavo.nginx_logs FORMAT JSONEachRow" \
  < /path/to/pre-converted.jsonl
```

---

## Querying ClickHouse

### Interactive shell

```bash
docker compose exec clickhouse clickhouse-client
```

### HTTP API

```bash
curl -s "http://localhost:8123/?query=SELECT+count()+FROM+estavo.nginx_logs"
```

### Useful queries

```sql
-- Row counts
SELECT count() FROM estavo.nginx_logs;
SELECT count() FROM estavo.nginx_error_logs;

-- Recent access logs
SELECT time_local, remote_addr, request_method, request_uri, status
FROM estavo.nginx_logs
ORDER BY time_local DESC
LIMIT 20;

-- Top resources by request count
SELECT resource_type, count() AS hits
FROM estavo.nginx_logs
WHERE resource_type IS NOT NULL
GROUP BY resource_type
ORDER BY hits DESC
LIMIT 10;

-- Status code distribution
SELECT status, count() AS n
FROM estavo.nginx_logs
GROUP BY status
ORDER BY status;

-- Slow requests (> 1 s)
SELECT time_local, request_method, request_uri, request_time
FROM estavo.nginx_logs
WHERE request_time > 1
ORDER BY request_time DESC
LIMIT 20;

-- Recent errors
SELECT time, level, message
FROM estavo.nginx_error_logs
ORDER BY time DESC
LIMIT 20;
```

---

## Log Formats

### `nginx_access` parser (brokers / remote / simulator sources)

Expected `log_format` in nginx:

```nginx
log_format nginx_access '$remote_addr - $remote_user [$time_local] '
                        '"$request_method $request_uri $server_protocol" '
                        '$status $body_bytes_sent '
                        'rt:$request_time '
                        '"$http_referer" "$http_user_agent" '
                        '"$realip_remote_addr" '
                        'uid:$uid_got';
```

Example line:

```
1.2.3.4 - - [27/Feb/2026:12:00:00 +0000] "GET /api/users/42 HTTP/1.1" 200 512 rt:0.05 "-" "curl/8.0" "1.2.3.4" uid:99
```

### `nginx_error` parser

Standard nginx error format:

```
2026/02/27 12:00:00 [error] 1234#56: *789 upstream timed out (110)
```

### `json` parser (nginx.access source)

When nginx writes JSON (`json_combined` log_format), the record is parsed directly. The Lua filter extracts `request_method` and `request_uri` from the `request` string if they are not already top-level fields.

---

## Troubleshooting

| Symptom | Check |
|---------|-------|
| FluentBit exits immediately | `docker compose logs fluentbit` — usually a config syntax error |
| No rows in ClickHouse | Confirm `fluentbit/state/` is writable; check FluentBit logs for HTTP 4xx from ClickHouse |
| Parser not matching | Run FluentBit with `Log_Level debug` and inspect raw records |
| ClickHouse rejects rows | Schema mismatch — compare field names with `DESCRIBE TABLE estavo.nginx_logs` |
| `simulator.access` not appearing | Confirm `logs/access.log` exists and the `./logs` volume mount is active |
| `remote.access` not appearing | Populate `./remote-nginx-logs/access.log`; check the volume mount |
| macOS: host nginx logs not visible | Add `/var/log/nginx` to Docker Desktop file sharing |

### Re-read all logs from the beginning

```bash
docker compose down
rm -rf fluentbit/state/*
docker compose up -d
```

### Truncate ClickHouse tables

```bash
docker compose exec clickhouse clickhouse-client \
  -q "TRUNCATE TABLE estavo.nginx_logs; TRUNCATE TABLE estavo.nginx_error_logs;"
```
