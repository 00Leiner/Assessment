<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ContactController;


// Route::get('/test', function () {
//     return response()->json(['message' => 'API is working!']);
// });

// upload to 'storage/app/contacts/' 
Route::post('/upload', [ContactController::class, 'upload']);

// get all contacts with pagination
Route::get('/contacts', [ContactController::class, 'contacts']);

// create contacts
Route::post('/add', [ContactController::class, 'add']);

// get contact by ID
Route::get('/retrieve/{id}', [ContactController::class, 'retrieve']);

// update contact by ID
Route::put('/update/{id}', [ContactController::class, 'update']);

// delete contact by ID
Route::delete('/delete/{id}', [ContactController::class, 'delete']);