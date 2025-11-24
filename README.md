# ML Smart Scheduling - Automated Retraining

Automated machine learning model retraining system for dental appointment smart scheduling.

## Features

- 🤖 **Automated Weekly Retraining** - Runs every Sunday via GitHub Actions
- 📊 **Continuous Learning** - Learns from real appointment data
- 🔄 **Custom Procedure Support** - Automatically learns new procedures
- 📈 **Model Versioning** - Tracks model updates in git
- 🔍 **Monitoring** - Logs all retraining events to Firebase

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Firebase

1. Get your Firebase service account key from Firebase Console
2. Add it to GitHub Secrets as `FIREBASE_SERVICE_ACCOUNT_KEY`

### 3. Test Locally

```bash
python auto_retrain_model.py
```

### 4. Deploy to GitHub

Push this repository to GitHub and the workflow will run automatically.

## How It Works

1. **Data Collection**: Actual appointment durations are saved to Firebase `mlTrainingData` collection
2. **Weekly Export**: GitHub Actions exports new training data
3. **Model Retraining**: Combines new data with original CSV and retrains Random Forest model
4. **Model Update**: Updates `smart_scheduler.pkl` with improved model
5. **Version Control**: Commits updated model to git

## Files

- `auto_retrain_model.py` - Main retraining script
- `ml_prediction_service.py` - ML prediction API service
- `requirements.txt` - Python dependencies
- `.github/workflows/retrain-model.yml` - GitHub Actions workflow

## Monitoring

- **GitHub Actions**: View retraining runs in Actions tab
- **Firebase**: Check `mlRetrainingLogs` collection for detailed logs
- **Admin Dashboard**: View status at `/admin/ml-status`

## Requirements

- Python 3.9+
- Firebase project with Firestore enabled
- GitHub account (free tier works)

## License

Part of the Dental Appointment App capstone project.

