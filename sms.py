from twilio.rest import Client
import datetime
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_alert_sms():
    # Get credentials from environment variables
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_FROM_NUMBER')
    to_number = os.getenv('TWILIO_TO_NUMBER')

    if not all([account_sid, auth_token, from_number, to_number]):
        print("Error: Missing Twilio credentials in environment variables")
        return False
    
    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            from_=from_number,
            to=to_number,
            body="Alert!!\nSome intruder tried to get in!"
        )
        print(f"Alert SMS sent! Message SID: {message.sid}")
        return True
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False

def log_entry(face_label):
    try:
        # Use absolute path in current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(current_dir, 'door_access_log.csv')
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_entry = pd.DataFrame({
            'timestamp': [timestamp],
            'face_label': [face_label],
            'status': ['Door Opened']
        })
        
        try:
            # Check if file is writable
            if os.path.exists(log_file):
                with open(log_file, 'a'):
                    pass
            
            # Append to existing file or create new one
            if os.path.exists(log_file):
                new_entry.to_csv(log_file, mode='a', header=False, index=False)
            else:
                new_entry.to_csv(log_file, index=False)
            
            print(f"Log entry created for {face_label} at {timestamp}")
            return True
            
        except PermissionError:
            print(f"Permission denied. Please check file permissions for: {log_file}")
            print("Try running VS Code as administrator")
            return False
            
    except Exception as e:
        print(f"Error creating log entry: {str(e)}")
        return False

def process_door_access():
    while True:
        try:
            status = input("Enter door status (0: Closed/Alert, 1: Opened) or 'q' to quit: ")
            
            if status.lower() == 'q':
                print("Exiting program...")
                break
            
            status = int(status)
            
            if status == 0:
                # Door closed - send alert
                send_alert_sms()
                print("Door closed - Alert sent")
            
            elif status == 1:
                # Door opened - log entry
                face_label = input("Enter person name/face label: ")
                log_entry(face_label)
                print("Door opened - Access logged")
            
            else:
                print("Please enter only 0 or 1")
                
        except ValueError:
            print("Invalid input! Please enter 0 or 1")

if __name__ == "__main__":
    process_door_access()