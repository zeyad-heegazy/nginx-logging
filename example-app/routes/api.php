<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\LogController;

Route::get('/logs', [LogController::class, 'index']);
Route::get('/logs/stats', [LogController::class, 'stats']);
