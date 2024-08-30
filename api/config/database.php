<?php

return [

    'default' => env('DB_CONNECTION', 'mongodb'),

    'connections' => [
        'mongodb' => [
            'driver' => 'mongodb', 
            'dsn' => env('DB_DSN', 'mongodb://127.0.0.1:27017'),
            'database' => env('DB_DATABASE', 'contacts_db'),
        ],
    ],

    'migrations' => 'migrations',

];
