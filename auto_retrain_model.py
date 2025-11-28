"""
Automated ML Model Retraining Script
This script can be run on a schedule (weekly/monthly) to automatically:
1. Export training data from Firebase
2. Retrain the Random Forest model
3. Update smart_scheduler.pkl
4. Optionally restart the ML service

Can be scheduled using:
- Cron (Linux/Mac)
- Task Scheduler (Windows)
- Cloud Functions
- GitHub Actions
- Cloud Run Jobs
"""

import os
import sys
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder
import firebase_admin
from firebase_admin import credentials, firestore
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('retraining.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
SERVICE_ACCOUNT_KEY = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY', 'path/to/serviceAccountKey.json')
# Try to find CSV in current directory or parent directories
_script_dir = os.path.dirname(__file__)
# List of synthetic CSV files to load
SYNTHETIC_CSV_FILES = [
    os.path.join(_script_dir, 'durations-synthetic-1.csv'),
    os.path.join(_script_dir, 'durations-synthetic-2.csv'),
    os.path.join(_script_dir, 'durations-synthetic-3.csv'),
]
# Fallback to original CSV if synthetic files don't exist
_csv_paths = [
    os.path.join(_script_dir, 'dental_procedure_durations_500.csv'),
    os.path.join(_script_dir, '..', 'dental_procedure_durations_500.csv'),
    os.path.join(_script_dir, '..', 'smart scheduling', 'dental_procedure_durations_500.csv'),
]
ORIGINAL_CSV = next((p for p in _csv_paths if os.path.exists(p)), None)
MODEL_PATH = os.path.join(_script_dir, 'smart_scheduler.pkl')
BACKUP_MODEL_PATH = os.path.join(_script_dir, 'smart_scheduler_backup.pkl')
MIN_TRAINING_SAMPLES = 50  # Minimum samples needed to retrain
TEST_SIZE = 0.2  # 20% for testing

def initialize_firebase():
    """Initialize Firebase Admin SDK. Returns True if successful, False if error, None if not configured."""
    try:
        if os.path.exists(SERVICE_ACCOUNT_KEY):
            cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully")
            return True
        else:
            logger.warning(f"Service account key not found at {SERVICE_ACCOUNT_KEY}")
            logger.info("Firebase not configured - will train from CSV files only")
            logger.info("To enable Firebase data export, set FIREBASE_SERVICE_ACCOUNT_KEY environment variable")
            return None  # Not an error, just not configured
    except Exception as e:
        logger.error(f"Error initializing Firebase: {e}")
        return False

def export_training_data():
    """Export training data from Firebase mlTrainingData collection."""
    try:
        db = firestore.client()
    except Exception as e:
        logger.warning(f"Firebase not initialized - skipping Firebase data export: {e}")
        return []
    
    training_data = []
    
    try:
        # Get all unused training data
        docs = db.collection('mlTrainingData').where('usedForTraining', '==', False).stream()
        
        for doc in docs:
            data = doc.to_dict()
            # Generate appointment_id if not present (for Firebase data)
            appointment_id = data.get('appointmentId') or data.get('appointment_id') or f"firebase_{doc.id}"
            training_data.append({
                'appointmentId': appointment_id,
                'procedureType': data.get('procedureType', '').lower(),
                'patientType': data.get('patientType', 'Adult'),
                'dayOfWeek': data.get('dayOfWeek', ''),
                'timePeriod': data.get('timePeriod', ''),
                'actualDurationMinutes': data.get('actualDurationMinutes', 0),
                'isCustomProcedure': data.get('isCustomProcedure', False),
            })
        
        logger.info(f"Exported {len(training_data)} new training records from Firebase")
        return training_data
        
    except Exception as e:
        logger.error(f"Error exporting training data: {e}")
        return []

def load_csv_file(csv_path, source_name="CSV"):
    """Load training data from a single CSV file."""
    training_data = []
    
    try:
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            
            # Map CSV columns to training format
            # Support both appointment_id and generate one if missing
            for idx, row in df.iterrows():
                # Get appointment_id if present, otherwise generate one
                appointment_id = str(row.get('appointment_id', row.get('appointmentId', f"{source_name}_{idx}")))
                
                training_data.append({
                    'appointmentId': appointment_id,
                    'procedureType': str(row.get('service_type', '')).lower(),
                    'patientType': str(row.get('patient_type', 'Adult')),
                    'dayOfWeek': str(row.get('day_of_week', '')),
                    'timePeriod': str(row.get('appointment_time', 'Afternoon')),
                    'actualDurationMinutes': float(row.get('avg_duration', 0)),
                    'isCustomProcedure': False,
                })
            
            logger.info(f"Loaded {len(training_data)} records from {source_name}: {csv_path}")
        else:
            logger.warning(f"CSV file not found: {csv_path}")
            
    except Exception as e:
        logger.error(f"Error loading {source_name} CSV ({csv_path}): {e}")
    
    return training_data

def load_initial_training_data():
    """
    Load initial/fundamental training data from synthetic CSV files.
    These are only used for bootstrapping the model when no real data exists.
    """
    all_training_data = []
    
    # Load synthetic CSV files (fundamental training data)
    synthetic_loaded = False
    for csv_file in SYNTHETIC_CSV_FILES:
        if os.path.exists(csv_file):
            data = load_csv_file(csv_file, source_name=os.path.basename(csv_file))
            all_training_data.extend(data)
            synthetic_loaded = True
    
    if synthetic_loaded:
        logger.info(f"Loaded {sum(1 for f in SYNTHETIC_CSV_FILES if os.path.exists(f))} synthetic CSV file(s) for initial training")
    else:
        # Fallback to original CSV if synthetic files don't exist
        if ORIGINAL_CSV:
            data = load_csv_file(ORIGINAL_CSV, source_name="original CSV")
            all_training_data.extend(data)
            logger.info("Loaded original CSV for initial training")
        else:
            logger.warning("No initial training CSV files found.")
    
    return all_training_data

def prepare_features(df):
    """Prepare features for model training."""
    # Create label encoders
    encoders = {
        'procedureType': LabelEncoder(),
        'patientType': LabelEncoder(),
        'dayOfWeek': LabelEncoder(),
        'timePeriod': LabelEncoder(),
    }
    
    # Fit encoders
    for col, encoder in encoders.items():
        df[col + '_encoded'] = encoder.fit_transform(df[col].astype(str))
    
    # Feature matrix
    X = df[['procedureType_encoded', 'patientType_encoded', 'dayOfWeek_encoded', 'timePeriod_encoded']].values
    y = df['actualDurationMinutes'].values
    
    return X, y, encoders

def train_model(X, y, encoders):
    """Train Random Forest model."""
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=42
    )
    
    # Train model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    
    logger.info(f"Training model with {len(X_train)} samples...")
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    
    logger.info(f"Training MAE: {train_mae:.2f} minutes, R²: {train_r2:.3f}")
    logger.info(f"Testing MAE: {test_mae:.2f} minutes, R²: {test_r2:.3f}")
    
    return model, {
        'train_mae': train_mae,
        'test_mae': test_mae,
        'train_r2': train_r2,
        'test_r2': test_r2,
        'train_samples': len(X_train),
        'test_samples': len(X_test),
    }

def save_model(model, encoders, metrics):
    """Save model and encoders to PKL file with backup."""
    try:
        # Backup existing model
        if os.path.exists(MODEL_PATH):
            import shutil
            shutil.copy(MODEL_PATH, BACKUP_MODEL_PATH)
            logger.info(f"Backed up existing model to {BACKUP_MODEL_PATH}")
        
        # Save new model
        model_data = {
            'model': model,
            'encoders': encoders,
            'metrics': metrics,
            'trained_at': datetime.now().isoformat(),
            'version': datetime.now().strftime('%Y%m%d_%H%M%S'),
        }
        
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {MODEL_PATH}")
        logger.info(f"Model version: {model_data['version']}")
        logger.info(f"Metrics: MAE={metrics['test_mae']:.2f} min, R²={metrics['test_r2']:.3f}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error saving model: {e}")
        # Restore backup if save failed
        if os.path.exists(BACKUP_MODEL_PATH):
            import shutil
            shutil.copy(BACKUP_MODEL_PATH, MODEL_PATH)
            logger.warning("Restored backup model due to save error")
        return False

def mark_data_as_used(training_data_count):
    """Mark exported training data as used in Firebase."""
    db = firestore.client()
    
    try:
        # Get all unused training data
        docs = list(db.collection('mlTrainingData').where('usedForTraining', '==', False).limit(training_data_count).stream())
        
        # Mark as used in batches
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
        
        logger.info(f"Marked {count} records as used for training")
        return True
        
    except Exception as e:
        logger.error(f"Error marking data as used: {e}")
        return False

def main():
    """Main retraining pipeline."""
    logger.info("=" * 60)
    logger.info("Starting automated model retraining")
    logger.info("=" * 60)
    
    # Initialize Firebase (optional - can train from CSV only)
    firebase_status = initialize_firebase()
    if firebase_status is False:
        logger.error("Firebase initialization failed. Exiting.")
        sys.exit(1)
    
    # Export real training data from Firebase (only if Firebase is configured)
    real_training_data = []
    if firebase_status is True:
        real_training_data = export_training_data()
    else:
        logger.info("Skipping Firebase data export (Firebase not configured)")
    
    # Determine which data to use for training
    # Strategy: Use real Firebase data if available, otherwise use synthetic CSVs for initial training
    if len(real_training_data) > 0:
        # We have real data - use ONLY real data (skip synthetic CSVs)
        logger.info("=" * 60)
        logger.info("Using REAL appointment data from Firebase for retraining")
        logger.info("Skipping synthetic CSV files (only used for initial training)")
        logger.info("=" * 60)
        all_training_data = real_training_data
    else:
        # No real data yet - use synthetic CSVs for initial/fundamental training
        logger.info("=" * 60)
        logger.info("No real data available - using SYNTHETIC CSV files for initial training")
        logger.info("Once real appointment data is collected, future retraining will use real data only")
        logger.info("=" * 60)
        initial_training_data = load_initial_training_data()
        all_training_data = initial_training_data
    
    if len(all_training_data) < MIN_TRAINING_SAMPLES:
        logger.warning(f"Not enough training samples ({len(all_training_data)} < {MIN_TRAINING_SAMPLES}). Skipping retraining.")
        logger.info("Model will continue using existing version.")
        sys.exit(0)
    
    logger.info(f"Total training samples before deduplication: {len(all_training_data)}")
    if len(real_training_data) > 0:
        logger.info(f"  - Real data from Firebase: {len(real_training_data)}")
        logger.info(f"  - Custom procedures: {sum(1 for d in all_training_data if d.get('isCustomProcedure', False))}")
    else:
        logger.info(f"  - Initial training data (synthetic CSVs): {len(all_training_data)}")
        logger.info("  - Note: This is initial training. Future retraining will use real Firebase data.")
    
    # Convert to DataFrame
    df = pd.DataFrame(all_training_data)
    
    # Remove duplicates based on appointmentId (not on feature columns)
    # This ensures that if a patient books the same appointment twice, both are kept
    initial_count = len(df)
    if 'appointmentId' in df.columns:
        df = df.drop_duplicates(subset=['appointmentId'], keep='first')
        duplicates_removed = initial_count - len(df)
        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicate records based on appointmentId")
        logger.info(f"Total unique training samples: {len(df)}")
    else:
        logger.warning("appointmentId column not found. Cannot perform proper duplicate detection.")
        logger.warning("Consider adding appointmentId to your CSV files to avoid incorrectly removing legitimate duplicate appointments.")
    
    # Prepare features
    X, y, encoders = prepare_features(df)
    
    # Train model
    model, metrics = train_model(X, y, encoders)
    
    # Save model
    if save_model(model, encoders, metrics):
        # Mark data as used (only if Firebase is configured and we exported data)
        if firebase_status is True and len(new_training_data) > 0:
            mark_data_as_used(len(new_training_data))
        
        logger.info("=" * 60)
        logger.info("Model retraining completed successfully!")
        logger.info("=" * 60)
        logger.info("Next steps:")
        logger.info("1. Restart ML prediction service to load new model")
        logger.info("2. Monitor prediction accuracy")
        logger.info("3. Check retraining.log for details")
        
        return 0
    else:
        logger.error("Model retraining failed!")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

