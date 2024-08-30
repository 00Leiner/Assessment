<?php

namespace App\Http\Controllers;

use Illuminate\Http\JsonResponse;

abstract class Controller
{
    // success response
    protected function successResponse($data, $message = 'Success', $code = 200): JsonResponse
    {
        return response()->json([
            'message' => $message,
            'data' => $data,
        ], $code);
    }

    // error response
    protected function errorResponse($message, $code): JsonResponse
    {
        return response()->json([
            'message' => $message,
        ], $code);
    }
}
