<?php

namespace App\Services\ClickHouse;

class NginxAccessLogService
{
    private ClickHouseConnection $connection;
    private string $table;

    public function __construct(ClickHouseConnection $connection)
    {
        $this->connection = $connection;
        $this->table = $connection->getTableName('access_logs');
    }

    public function getLogs(array $filters = [], int $limit = 100, int $offset = 0): array
    {
        $where = $this->buildWhere($filters);

        $sql = "
            SELECT *
            FROM {$this->table}
            {$where}
            LIMIT {$limit} OFFSET {$offset}
        ";

        $sql = preg_replace('/\s+/', ' ', $sql);
        return $this->connection->select($sql);
    }

    public function count(array $filters = []): int
    {
        $where = $this->buildWhere($filters);

        $sql = "
            SELECT count() as total
            FROM {$this->table}
            {$where}
        ";

        $sql = preg_replace('/\s+/', ' ', $sql);
        $res = $this->connection->select($sql);

        return (int) ($res[0]['total'] ?? 0);
    }

    public function stats(): array
    {
        $sql = "
        SELECT
            count() as total_requests,
            countIf(status >=400 AND status <500) as client_errors,
            countIf(status >=500) as server_errors,
            avg(response_time) as avg_response_time,
            count(DISTINCT ip) as unique_ips
        FROM {$this->table}
        ";

        $sql = preg_replace('/\s+/', ' ', $sql);
        $res = $this->connection->select($sql);

        return $res[0] ?? [];
    }

    private function buildWhere(array $filters): string
    {
        $c = [];

        if (!empty($filters['ip'])) {
            $ip = addslashes($filters['ip']);
            $c[] = "remote_addr LIKE '%{$ip}%'";
        }

        if (!empty($filters['status'])) {
            $c[] = "status = " . (int) $filters['status'];
        }

        if (!empty($filters['method'])) {
            $m = strtoupper(addslashes($filters['method']));
            $c[] = "request LIKE '{$m} %'";
        }

        if (!empty($filters['start_date'])) {
            $d = addslashes($filters['start_date']);
            $c[] = "time_local >= '{$d}'";
        }

        if (!empty($filters['end_date'])) {
            $d = addslashes($filters['end_date']);
            $c[] = "time_local <= '{$d}'";
        }

        if (!$c)
            return '';
        return 'WHERE ' . implode(' AND ', $c);
    }
}
