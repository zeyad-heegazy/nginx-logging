CREATE DATABASE IF NOT EXISTS estavo;

CREATE TABLE IF NOT EXISTS estavo.nginx_logs (
    time DateTime,
    remote_addr String,
    method String,
    uri String,
    status UInt16,
    body_bytes_sent UInt64,
    request_time Float32,
    http_referrer String,
    http_user_agent String
) ENGINE = MergeTree
ORDER BY time;

CREATE TABLE IF NOT EXISTS estavo.nginx_error_logs (
    timestamp DateTime DEFAULT now(),
    level String DEFAULT '',
    pid UInt32 DEFAULT 0,
    tid UInt32 DEFAULT 0,
    message String DEFAULT '',
    raw_log String DEFAULT ''
) ENGINE = MergeTree
ORDER BY timestamp;