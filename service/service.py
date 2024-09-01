import os
import time
import json
import re
import pymongo
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from jsonschema import validate, ValidationError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB configuration
DB_CONNECTION = os.getenv("DB_CONNECTION")
DB_DSN = os.getenv("DB_DSN")
DB_DATABASE = os.getenv("DB_DATABASE")

# connection
def connect_to_mongo():
    client = pymongo.MongoClient(DB_DSN)
    db = client[DB_DATABASE]
    return db

#schedma or model
contact_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},  
        "email": {"type": "string", "format": "email"}, 
        "phone": {"type": "string"},  
    },
    "required": ["name", "email", "phone"] 
}

# Phone number format
def normalize_phone(phone):
    # Pattern to match +1-XXX-XXX-XXXX format
    pattern_1 = re.compile(r'\+1-(\d{3})-(\d{3})-(\d{4})')
    # Pattern to match XXX-XXX-XXXX format
    pattern_2 = re.compile(r'(\d{3})-(\d{3})-(\d{4})')
    
    match_1 = pattern_1.match(phone)
    match_2 = pattern_2.match(phone)
    
    if match_1:
        return f"({match_1.group(1)}) {match_1.group(2)}-{match_1.group(3)}"
    elif match_2:
        return f"({match_2.group(1)}) {match_2.group(2)}-{match_2.group(3)}"
    
    return phone

# Handle file events
class ContactFileHandler(FileSystemEventHandler):
    def __init__(self, db, watch_directory):
        self.db = db
        self.watch_directory = watch_directory
        self.process_last_file()  

    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            threading.Thread(target=self.process_file, args=(event.src_path,)).start()

    # If the storage/app/contacts/ directory is not empty, get the last file for processing
    def process_last_file(self):
        files = os.listdir(self.watch_directory)
        if files:
            latest_file = max([os.path.join(self.watch_directory, f) for f in files], key=os.path.getmtime)
            print(f"Processing the last file: {latest_file}")
            self.process_file(latest_file)

    # Parse the contact json
    def process_file(self, file_path):
        try:
            # Read the JSON file
            with open(file_path, 'r') as file:
                contacts = json.load(file)

            # Validate and process
            for contact in contacts:
                try:
                    # Validate data format
                    validate(instance=contact, schema=contact_schema)

                    # Phone number validation
                    contact['phone'] = normalize_phone(contact['phone'])

                    # Check for unique email
                    if self.db.contacts.find_one({"email": contact['email']}):
                        print(f"Email {contact['email']} is already in the database.")
                        continue

                    # Insert into MongoDB
                    self.db.contacts.insert_one(contact)
                    print(f"Inserted contact: {contact}")

                except ValidationError as e:
                    print(f"Validation error for contact {contact}: {e.message}")
                except Exception as e:
                    print(f"Error processing contact {contact}: {e}")

        except json.JSONDecodeError:
            print(f"Error reading JSON file: {file_path}")
        finally:
            # Remove the processed file 
            os.remove(file_path)
         
def start_observer(observer):
    observer.start()
    print(f"Watching for new files in: {watch_directory}")

if __name__ == "__main__":
    db = connect_to_mongo()

    watch_directory = os.path.abspath("../api/storage/app/contacts/")

    # Check if the directory exists
    if not os.path.exists(watch_directory):
        # Create directory
        os.makedirs(watch_directory)
        print(f"Created directory: {watch_directory}")

    observer = Observer()
    handler = ContactFileHandler(db, watch_directory)
    observer.schedule(handler, watch_directory, recursive=False)

    observer_thread = threading.Thread(target=start_observer, args=(observer,))
    observer_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()