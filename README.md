# Contact Management Python Service

This Python service watches a specified directory for new JSON files containing contact information. When a new file is detected, it processes the file to validate, normalize, and store the contact data in a MongoDB database.

## Features

- Watches a designated directory for new contact JSON files.
- Validates contact data according to predefined schemas.
- Normalizes phone numbers to a standard format.
- Ensures email uniqueness before inserting into the database.
- Handles faulty JSON files gracefully.
- Continuously monitors the directory for new files.

## Requirements

- Python 3.x
- MongoDB
- Required Python packages:
  - `pymongo`
  - `watchdog`
  - `jsonschema`
  - `python-dotenv`

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/00Leiner/Assessment/tree/main/service
   cd service
   ```

2. Install the required packages:

   ```bash
   pip install pymongo watchdog jsonschema python-dotenv
   ```

3. Create a `.env` file in the root directory and configure your MongoDB connection settings:

   ```plaintext
   DB_CONNECTION=<your_connection_name>
   DB_DSN=<your_mongo_dsn>
   DB_DATABASE=<your_database_name>
   ```

## Code Overview

### Key Functions and Classes

- **`connect_to_mongo()`**: Establishes a connection to the MongoDB database using credentials from the `.env` file.

- **`normalize_phone(phone)`**: Normalizes phone numbers to the format `(XXX) XXX-XXXX` based on specified patterns.

- **`ContactFileHandler`**: Inherits from `FileSystemEventHandler` and handles events related to file creation.
  - **`on_created(event)`**: Triggered when a new file is created in the watched directory. Starts a new thread to process the file.
  - **`process_last_file()`**: Checks for existing files in the directory and processes the most recently modified file.
  - **`process_file(file_path)`**: Reads, validates, and processes contact data from the given JSON file. Inserts valid contacts into the MongoDB database.

### Starting the Service

Run the service by executing the following command in your terminal:

```bash
python service.py
```

The service will start watching the `storage/app/contacts/` directory for new JSON files. 

## JSON File Format

The JSON files should contain an array of contact objects in the following format:

```json
[
  {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-123-456-7890"
  },
  {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "987-654-3210"
  }
]
```

### Important Notes

- Ensure that the phone numbers in the JSON files are in the supported formats (`+1-XXX-XXX-XXXX` or `XXX-XXX-XXXX`).
- The service will automatically remove processed files from the directory.


