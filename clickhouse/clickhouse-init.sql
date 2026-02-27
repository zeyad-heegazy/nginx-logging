CREATE DATABASE IF NOT EXISTS estavo;

CREATE TABLE IF NOT EXISTS estavo.nginx_logs (
    time_local String,
    remote_addr String,
    request_method String,
    request_uri String,
    resource_type Nullable(String),
    resource_id Nullable(UInt32),
    status UInt16,
    body_bytes_sent UInt64,
    request_time Float32,
    http_referer String,
    http_user_agent String,
    real_ip String,
    uid Nullable(UInt32)
) ENGINE = MergeTree
ORDER BY time_local;

CREATE TABLE IF NOT EXISTS estavo.nginx_error_logs (
    time DateTime,
    level String,
    pid UInt32,
    tid UInt32,
    cid UInt32 DEFAULT 0,
    message String
) ENGINE = MergeTree
ORDER BY time;