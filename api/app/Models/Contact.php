<?php

namespace App\Models;

use MongoDB\Laravel\Eloquent\Model;

class Contact extends Model
{
    // Collection name
    protected $collection = 'contacts';

    // Attributes
    protected $fillable = [
        'name',
        'email',
        'phone',
    ];

    // Validation rules
    public static $rules = [
        'name' => 'required|string|max:255',
        'email' => 'required|email|unique:contacts,email',
        'phone' => 'required|string',
    ];
}