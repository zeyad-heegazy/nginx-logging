<?php

namespace App\Http\Controllers;

use App\Services\ClickHouse\NginxAccessLogService;
use Illuminate\Http\Request;

class LogController extends Controller
{
    private NginxAccessLogService $service;

    public function __construct(NginxAccessLogService $service)
    {
        $this->service = $service;
    }

    public function index(Request $req)
    {
        $filters = $req->only([
            'ip',
            'status',
            'method',
            'start_date',
            'end_date'
        ]);

        $limit = (int) $req->input('limit', 100);
        $offset = (int) $req->input('offset', 0);

        $page = max(1, (int) $req->input('page', 1));
        $offset = ($page - 1) * $limit;

        $total = $this->service->count($filters);
        $data = $this->service->getLogs($filters, $limit, $offset);

        $totalPages = (int) ceil($total / $limit);

        return response()->json([
            'success' => true,
            'data' => $data,
            'meta' => [
                'total' => $total,
                'per_page' => $limit,
                'current_page' => $page,
                'total_pages' => $totalPages,
                'from' => $offset + 1,
                'to' => $offset + count($data),
                'has_more' => $page < $totalPages,
            ],
        ]);
    }

    public function stats()
    {
        return response()->json([
            'success' => true,
            'data' => $this->service->stats()
        ]);
    }
}
