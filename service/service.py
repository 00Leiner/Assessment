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
    try:
        client = pymongo.MongoClient(DB_DSN)
        db = client[DB_DATABASE]
        return db
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise

# schema or model
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
    # Get only number
    cleaned_phone = re.sub(r'\D', '', phone)
    # print(cleaned_phone)
    if len(cleaned_phone) == 10: 
        return f"+1-{cleaned_phone[:3]}-{cleaned_phone[3:6]}-{cleaned_phone[6:]}"
    elif len(cleaned_phone) == 11: 
        cleaned_phone[0] == 1
        return f"+{cleaned_phone[0]}-{cleaned_phone[1:4]}-{cleaned_phone[4:7]}-{cleaned_phone[7:]}"
    
    return phone

# Validate email format
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Handle file events
class ContactFileHandler(FileSystemEventHandler):
    def __init__(self, db):
        self.db = db
    
    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            threading.Thread(target=self.process_file, args=(event.src_path,)).start()

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

                    # Additional email validation
                    if not is_valid_email(contact['email']):
                        print(f"Invalid email format: {contact['email']}.")
                        continue  # Skip to the next contact

                    # Phone number formatting 
                    contact['phone'] = normalize_phone(contact['phone'])

                    # Check for unique email
                    if self.db.contacts.find_one({"email": contact['email']}):
                        print(f"Email {contact['email']} is already in the database. Skipping this contact.")
                        continue

                    # Insert into MongoDB
                    self.db.contacts.insert_one(contact)
                    print(f"Inserted contact: {contact}")

                except ValidationError as e:
                    print(f"Validation error for contact {contact}: {e.message}. Skipping this contact.")
                except Exception as e:
                    print(f"Error processing contact {contact}: {e}. Skipping this contact.")

        except json.JSONDecodeError:
            print(f"Error reading JSON file: {file_path}")
        finally:
            # Remove the processed file 
            os.remove(file_path)
         
    def check_existing_files(self, directory):
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                print(f"Processing existing file: {file_path}")
                self.process_file(file_path)

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

    handler = ContactFileHandler(db)
    handler.check_existing_files(watch_directory)

    observer = Observer()
    observer.schedule(handler, watch_directory, recursive=False)

    observer_thread = threading.Thread(target=start_observer, args=(observer,))
    observer_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()