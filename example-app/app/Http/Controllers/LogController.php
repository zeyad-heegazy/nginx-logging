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

        $limit = min((int) $req->get('limit', 100), 500);
        $offset = (int) $req->get('offset', 0);

        return response()->json([
            'success' => true,
            'total' => $this->service->count($filters),
            'data' => $this->service->getLogs($filters, $limit, $offset)
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
