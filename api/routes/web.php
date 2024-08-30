<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ContactController;
use Illuminate\Http\Request;

Route::get('/', function () {
    return view('welcome');
});

Route::get('/test', function () {
    return response()->json(['message' => 'API is working!']);
});

// upload to 'storage/app/contacts/' 
Route::post('/upload', [ContactController::class, 'upload']);

// get all contacts with pagination
Route::get('/contacts', [ContactController::class, 'index']);

// create contacts
Route::post('/contacts', [ContactController::class, 'store']);

// get contact by ID
Route::get('/contacts/{id}', [ContactController::class, 'show']);

// update contact by ID
Route::put('/contacts/{id}', [ContactController::class, 'update']);

// delete contact by ID
Route::delete('/contacts/{id}', [ContactController::class, 'destroy']);