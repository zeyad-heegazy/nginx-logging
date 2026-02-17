<?php

return [
    'host' => env('CLICKHOUSE_HOST', '127.0.0.1'),
    'port' => env('CLICKHOUSE_PORT', 8123),
    'database' => env('CLICKHOUSE_DATABASE', 'estavo'),
    'username' => env('CLICKHOUSE_USERNAME', env('CLICKHOUSE_USER', 'default')),
    'password' => env('CLICKHOUSE_PASSWORD', ''),

    'tables' => [
        'access_logs' => 'nginx_logs',
    ],
];
