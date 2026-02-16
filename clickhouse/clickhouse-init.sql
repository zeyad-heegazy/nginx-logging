CREATE DATABASE IF NOT EXISTS estavo;

CREATE TABLE IF NOT EXISTS estavo.nginx_logs (
    time_local String,
    remote_addr String,
    remote_user String,
    request String,
    status UInt16,
    body_bytes_sent UInt64,
    http_referer String,
    http_user_agent String,
    request_length UInt32,
    request_time Float32
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