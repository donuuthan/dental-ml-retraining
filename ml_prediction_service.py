"""
ML Prediction Service for Smart Scheduling
Loads the trained Random Forest model (smart_scheduler.pkl) and provides duration predictions via HTTP API.
"""

import pickle
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for Flutter app

# Load the trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'smart_scheduler.pkl')
model = None
label_encoders = None

def load_model():
    """Load the trained model and label encoders from PKL file."""
    global model, label_encoders
    try:
        with open(MODEL_PATH, 'rb') as f:
            data = pickle.load(f)
            # PKL file might contain model directly or a dict with model and encoders
            if isinstance(data, dict):
                model = data.get('model')
                label_encoders = data.get('encoders', {})
            else:
                model = data
                label_encoders = {}
        print(f"Model loaded successfully from {MODEL_PATH}")
        return True
    except FileNotFoundError:
        print(f"Error: Model file not found at {MODEL_PATH}")
        return False
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

# Load model on startup
if not load_model():
    print("Warning: Model not loaded. Predictions will use fallback values.")

def encode_feature(value, feature_name, default=0):
    """Encode a categorical feature using label encoder or simple mapping."""
    if feature_name in label_encoders:
        try:
            return label_encoders[feature_name].transform([value])[0]
        except:
            return default
    
    # Fallback encoding if no encoder available
    encoding_maps = {
        'patient_type': {'Adult': 0, 'Child': 1, 'adult': 0, 'child': 1},
        'day_of_week': {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6,
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        },
        'time_period': {
            'Morning': 0, 'Afternoon': 1, 'Evening': 2,
            'morning': 0, 'afternoon': 1, 'evening': 2,
            'AM': 0, 'PM': 1
        }
    }
    
    if feature_name in encoding_maps:
        return encoding_maps[feature_name].get(value, default)
    
    return default

def get_time_period(time_str):
    """Extract time period (Morning/Afternoon/Evening) from time string."""
    try:
        # Parse time string (e.g., "2:00 PM" or "14:30")
        if 'AM' in time_str.upper() or 'PM' in time_str.upper():
            time_part = time_str.split()[0]
            period = time_str.split()[1].upper() if len(time_str.split()) > 1 else 'AM'
            hour = int(time_part.split(':')[0])
            if period == 'PM' and hour != 12:
                hour += 12
            elif period == 'AM' and hour == 12:
                hour = 0
        else:
            hour = int(time_str.split(':')[0])
        
        if 5 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 17:
            return 'Afternoon'
        else:
            return 'Evening'
    except:
        return 'Afternoon'  # Default

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None
    })

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict appointment duration using the ML model.
    
    Request body:
    {
        "procedure_type": "extraction",
        "patient_type": "Adult",  // or "Child"
        "appointment_date": "2024-01-15",  // ISO format
        "appointment_time": "2:00 PM"  // or "14:00"
    }
    
    Response:
    {
        "predicted_duration_minutes": 28.5,
        "confidence": "high",  // or "medium", "low"
        "model_used": true
    }
    """
    try:
        data = request.json
        
        # Validate input
        required_fields = ['procedure_type', 'patient_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        procedure_type = data.get('procedure_type', '').lower()
        patient_type = data.get('patient_type', 'Adult')
        appointment_date = data.get('appointment_date')
        appointment_time = data.get('appointment_time', '12:00 PM')
        
        # If model not loaded, return fallback
        if model is None:
            # Fallback durations (simple averages)
            fallback_durations = {
                'extraction': 25,
                'cleaning': 35,
                'filling': 30,
                'root canal': 60,
                'crown': 45,
                'checkup': 20,
            }
            
            duration = 60  # Default
            for key, value in fallback_durations.items():
                if key in procedure_type:
                    duration = value
                    break
            
            return jsonify({
                'predicted_duration_minutes': float(duration),
                'confidence': 'low',
                'model_used': False,
                'fallback': True
            })
        
        # Extract features
        day_of_week = 'Monday'  # Default
        if appointment_date:
            try:
                date_obj = datetime.fromisoformat(appointment_date.replace('Z', '+00:00'))
                day_of_week = date_obj.strftime('%A')
            except:
                pass
        
        time_period = get_time_period(appointment_time)
        
        # Encode features (adjust based on your model's expected features)
        # Note: You may need to adjust feature names based on your actual model
        features = []
        
        # Feature 1: Procedure type (encoded)
        # For now, use a simple hash-based encoding
        procedure_encoded = hash(procedure_type) % 1000
        features.append(procedure_encoded)
        
        # Feature 2: Patient type
        features.append(encode_feature(patient_type, 'patient_type'))
        
        # Feature 3: Day of week
        features.append(encode_feature(day_of_week, 'day_of_week'))
        
        # Feature 4: Time period
        features.append(encode_feature(time_period, 'time_period'))
        
        # Make prediction
        features_array = np.array([features])
        prediction = model.predict(features_array)[0]
        
        # Ensure prediction is positive and reasonable
        predicted_duration = max(10, min(180, float(prediction)))  # Clamp between 10-180 minutes
        
        # Determine confidence (simplified - you can improve this)
        confidence = 'high' if model is not None else 'low'
        
        return jsonify({
            'predicted_duration_minutes': round(predicted_duration, 1),
            'confidence': confidence,
            'model_used': True,
            'features': {
                'procedure_type': procedure_type,
                'patient_type': patient_type,
                'day_of_week': day_of_week,
                'time_period': time_period
            }
        })
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        return jsonify({
            'error': str(e),
            'predicted_duration_minutes': 60.0,  # Fallback
            'confidence': 'low',
            'model_used': False
        }), 500

if __name__ == '__main__':
    # Run on all interfaces, port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)

