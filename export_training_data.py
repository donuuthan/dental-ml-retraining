"""
Export ML Training Data from Firebase for Model Retraining
This script exports actual appointment durations collected from the app
and combines them with original CSV data for continuous learning.
"""

import json
import csv
from datetime import datetime
from firebase_admin import initialize_app, credentials, firestore
import os

# Initialize Firebase Admin SDK
# Make sure to download your Firebase service account key and place it in this directory
SERVICE_ACCOUNT_KEY = 'path/to/your/serviceAccountKey.json'  # Update this path

def initialize_firebase():
    """Initialize Firebase Admin SDK."""
    try:
        if os.path.exists(SERVICE_ACCOUNT_KEY):
            cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
            initialize_app(credential=cred)
            print("Firebase initialized successfully")
            return True
        else:
            print(f"Error: Service account key not found at {SERVICE_ACCOUNT_KEY}")
            print("Please download your Firebase service account key and update SERVICE_ACCOUNT_KEY path")
            return False
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return False

def export_training_data(output_file='ml_training_data_export.csv', limit=None):
    """
    Export ML training data from Firebase to CSV.
    
    Args:
        output_file: Output CSV file path
        limit: Maximum number of records to export (None for all)
    """
    if not initialize_firebase():
        return
    
    db = firestore.client()
    
    try:
        # Query ML training data collection
        query = db.collection('mlTrainingData').where('usedForTraining', '==', False)
        
        if limit:
            query = query.limit(limit)
        
        docs = query.stream()
        
        training_data = []
        for doc in docs:
            data = doc.to_dict()
            training_data.append({
                'appointmentId': doc.id,
                'procedureType': data.get('procedureType', ''),
                'patientType': data.get('patientType', 'Adult'),
                'appointmentDate': data.get('appointmentDate').strftime('%Y-%m-%d') if data.get('appointmentDate') else '',
                'dayOfWeek': data.get('dayOfWeek', ''),
                'appointmentTime': data.get('appointmentTime', ''),
                'timePeriod': data.get('timePeriod', ''),
                'actualDurationMinutes': data.get('actualDurationMinutes', 0),
                'isCustomProcedure': data.get('isCustomProcedure', False),
                'clinicId': data.get('clinicId', ''),
            })
        
        # Write to CSV
        if training_data:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'appointmentId', 'procedureType', 'patientType', 'appointmentDate',
                    'dayOfWeek', 'appointmentTime', 'timePeriod', 'actualDurationMinutes',
                    'isCustomProcedure', 'clinicId'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(training_data)
            
            print(f"Exported {len(training_data)} training data records to {output_file}")
            
            # Mark exported records as used
            batch = db.batch()
            count = 0
            for doc in docs:
                batch.update(doc.reference, {'usedForTraining': True})
                count += 1
                if count % 500 == 0:  # Firestore batch limit
                    batch.commit()
                    batch = db.batch()
            
            if count % 500 != 0:
                batch.commit()
            
            print(f"Marked {count} records as used for training")
        else:
            print("No training data found to export")
            
    except Exception as e:
        print(f"Error exporting training data: {e}")

def combine_with_original_csv(training_csv, original_csv, output_csv):
    """
    Combine exported training data with original CSV data for retraining.
    
    Args:
        training_csv: Path to exported training data CSV
        original_csv: Path to original CSV file (e.g., dental_procedure_durations_500.csv)
        output_csv: Path to combined output CSV
    """
    try:
        combined_data = []
        
        # Read original CSV
        if os.path.exists(original_csv):
            with open(original_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert original CSV format to training format
                    combined_data.append({
                        'procedureType': row.get('service_type', ''),
                        'patientType': row.get('patient_type', 'Adult'),
                        'dayOfWeek': row.get('day_of_week', ''),
                        'timePeriod': row.get('appointment_time', ''),  # May need adjustment
                        'actualDurationMinutes': row.get('avg_duration', 0),
                        'isCustomProcedure': False,
                    })
            print(f"Loaded {len(combined_data)} records from original CSV")
        
        # Read training data CSV
        if os.path.exists(training_csv):
            with open(training_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    combined_data.append({
                        'procedureType': row.get('procedureType', ''),
                        'patientType': row.get('patientType', 'Adult'),
                        'dayOfWeek': row.get('dayOfWeek', ''),
                        'timePeriod': row.get('timePeriod', ''),
                        'actualDurationMinutes': row.get('actualDurationMinutes', 0),
                        'isCustomProcedure': row.get('isCustomProcedure', 'False').lower() == 'true',
                    })
            print(f"Loaded additional records from training data CSV")
        
        # Write combined data
        if combined_data:
            with open(output_csv, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['procedureType', 'patientType', 'dayOfWeek', 'timePeriod', 'actualDurationMinutes', 'isCustomProcedure']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(combined_data)
            
            print(f"Combined {len(combined_data)} records written to {output_csv}")
            print(f"Custom procedures: {sum(1 for d in combined_data if d.get('isCustomProcedure'))}")
        else:
            print("No data to combine")
            
    except Exception as e:
        print(f"Error combining CSVs: {e}")

if __name__ == '__main__':
    print("ML Training Data Export Script")
    print("=" * 50)
    
    # Export training data from Firebase
    export_training_data('ml_training_data_export.csv', limit=None)
    
    # Combine with original CSV (optional)
    # combine_with_original_csv(
    #     'ml_training_data_export.csv',
    #     'dental_procedure_durations_500.csv',
    #     'combined_training_data.csv'
    # )
    
    print("\nNext steps:")
    print("1. Review the exported CSV file")
    print("2. Combine with original CSV data if needed")
    print("3. Use the combined data to retrain the ML model")
    print("4. Update smart_scheduler.pkl with the new model")

