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
    """Initialize Firebase Admin SDK."""
    try:
        if os.path.exists(SERVICE_ACCOUNT_KEY):
            cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully")
            return True
        else:
            logger.error(f"Service account key not found at {SERVICE_ACCOUNT_KEY}")
            logger.info("Set FIREBASE_SERVICE_ACCOUNT_KEY environment variable or update path")
            return False
    except Exception as e:
        logger.error(f"Error initializing Firebase: {e}")
        return False

def export_training_data():
    """Export training data from Firebase mlTrainingData collection."""
    db = firestore.client()
    training_data = []
    
    try:
        # Get all unused training data
        docs = db.collection('mlTrainingData').where('usedForTraining', '==', False).stream()
        
        for doc in docs:
            data = doc.to_dict()
            training_data.append({
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

def load_original_csv():
    """Load original CSV training data."""
    training_data = []
    
    try:
        if os.path.exists(ORIGINAL_CSV):
            df = pd.read_csv(ORIGINAL_CSV)
            
            # Map CSV columns to training format
            # Adjust column names based on your CSV structure
            for _, row in df.iterrows():
                training_data.append({
                    'procedureType': str(row.get('service_type', '')).lower(),
                    'patientType': str(row.get('patient_type', 'Adult')),
                    'dayOfWeek': str(row.get('day_of_week', '')),
                    'timePeriod': str(row.get('appointment_time', 'Afternoon')),
                    'actualDurationMinutes': float(row.get('avg_duration', 0)),
                    'isCustomProcedure': False,
                })
            
            logger.info(f"Loaded {len(training_data)} records from original CSV")
        else:
            logger.warning(f"Original CSV not found at {ORIGINAL_CSV}")
            
    except Exception as e:
        logger.error(f"Error loading original CSV: {e}")
    
    return training_data

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
    
    # Initialize Firebase
    if not initialize_firebase():
        logger.error("Failed to initialize Firebase. Exiting.")
        sys.exit(1)
    
    # Export new training data from Firebase
    new_training_data = export_training_data()
    
    # Load original CSV data
    original_training_data = load_original_csv()
    
    # Combine datasets
    all_training_data = original_training_data + new_training_data
    
    if len(all_training_data) < MIN_TRAINING_SAMPLES:
        logger.warning(f"Not enough training samples ({len(all_training_data)} < {MIN_TRAINING_SAMPLES}). Skipping retraining.")
        logger.info("Model will continue using existing version.")
        sys.exit(0)
    
    logger.info(f"Total training samples: {len(all_training_data)}")
    logger.info(f"  - Original CSV: {len(original_training_data)}")
    logger.info(f"  - New from Firebase: {len(new_training_data)}")
    logger.info(f"  - Custom procedures: {sum(1 for d in all_training_data if d.get('isCustomProcedure', False))}")
    
    # Convert to DataFrame
    df = pd.DataFrame(all_training_data)
    
    # Prepare features
    X, y, encoders = prepare_features(df)
    
    # Train model
    model, metrics = train_model(X, y, encoders)
    
    # Save model
    if save_model(model, encoders, metrics):
        # Mark data as used
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

