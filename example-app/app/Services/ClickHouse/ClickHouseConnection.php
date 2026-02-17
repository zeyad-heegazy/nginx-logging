<?php

namespace App\Services\ClickHouse;

use Illuminate\Support\Facades\Http;

class ClickHouseConnection
{
    private string $baseUrl;
    private string $database;
    private string $user;
    private string $password;

    public function __construct()
    {
        $host = config('clickhouse.host');
        $port = config('clickhouse.port');

        $this->database = config('clickhouse.database');
        $this->user = config('clickhouse.username');
        $this->password = config('clickhouse.password');

        $this->baseUrl = "http://{$host}:{$port}";
    }

    public function select(string $sql): array
    {
        $sql .= " FORMAT JSON";

        $response = Http::withBasicAuth($this->user, $this->password)
            ->withHeaders([
                'X-ClickHouse-Database' => $this->database,
            ])
            ->send('POST', $this->baseUrl, [
                'body' => $sql,
            ]);

        if (!$response->successful()) {
            throw new \Exception($response->body());
        }

        return $response->json('data') ?? [];
    }

    public function getTableName(string $key): string
    {
        $tables = config('clickhouse.tables');
        return $tables[$key] ?? $key;
    }
}
