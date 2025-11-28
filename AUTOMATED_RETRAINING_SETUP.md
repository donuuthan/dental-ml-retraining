# Automated ML Model Retraining Setup Guide

## Current Status

Your model **can** automatically retrain from Firebase every week, but you need to choose and configure one of these options:

## Option 1: GitHub Actions (Recommended - Already Configured! ✅)

**Status**: Already set up in `.github/workflows/retrain-model.yml`

**How it works**:
- Runs every Sunday at 2 AM UTC
- Pulls new training data from Firebase
- Trains the model
- Commits the updated model back to your repo

**To activate**:
1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Add secret: `FIREBASE_SERVICE_ACCOUNT_KEY` (paste your Firebase service account JSON)
4. The workflow will run automatically every Sunday

**Manual trigger**: You can also trigger it manually from GitHub Actions tab → "Auto-Retrain ML Model" → "Run workflow"

**Pros**:
- ✅ Already configured
- ✅ Free for public repos
- ✅ Automatic commits of updated model
- ✅ Full Python environment available

**Cons**:
- Requires GitHub repository
- Model file is committed to repo (can be large)

---

## Option 2: Firebase Cloud Function + Cloud Scheduler

**Status**: Function exists but needs configuration

**How it works**:
- Cloud Function checks for new training data weekly
- Logs to Firestore (`mlRetrainingLogs` collection)
- You can trigger manual retraining via HTTP

**To activate**:
1. Deploy the function:
   ```bash
   firebase deploy --only functions:retrainMLModelWeekly
   ```

2. (Optional) Set GitHub token to trigger GitHub Actions:
   ```bash
   firebase functions:secrets:set GITHUB_TOKEN
   firebase functions:secrets:set GITHUB_REPO
   ```

**Current behavior**:
- Checks for new training data in Firebase
- Logs recommendations to `mlRetrainingLogs`
- Can trigger GitHub Actions if configured

**Pros**:
- Integrated with Firebase
- Can check Firebase data directly
- Logs to Firestore for tracking

**Cons**:
- Can't run Python directly (needs external service)
- Currently just logs recommendations

---

## Option 3: Cloud Run Jobs (Best for Production)

**Status**: Configuration file exists (`cloud_run_job.yaml`)

**How it works**:
- Cloud Run Job runs your Python script in a container
- Can be scheduled via Cloud Scheduler
- Full Python environment with all dependencies

**To activate**:
1. Build and deploy the container:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT/ml-retraining
   gcloud run jobs create ml-retraining \
     --image gcr.io/YOUR_PROJECT/ml-retraining \
     --region us-central1
   ```

2. Schedule it:
   ```bash
   gcloud scheduler jobs create http ml-retraining-weekly \
     --schedule="0 2 * * 0" \
     --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/YOUR_PROJECT/jobs/ml-retraining:run" \
     --http-method=POST \
     --oauth-service-account-email=YOUR_PROJECT@appspot.gserviceaccount.com
   ```

**Pros**:
- ✅ Full Python environment
- ✅ Can run directly in GCP
- ✅ Scalable and reliable
- ✅ No GitHub dependency

**Cons**:
- More complex setup
- Requires GCP billing (but very cheap)
- Need to manage container

---

## Option 4: Manual Script (Current Working Method)

**Status**: ✅ Working now!

**How it works**:
- Run the script manually when needed
- Loads from CSV files (or Firebase if configured)

**To use**:
```bash
python "smart scheduling/auto_retrain_model.py"
```

**Pros**:
- ✅ Simple and works immediately
- ✅ Full control
- ✅ Good for testing

**Cons**:
- Not automated
- Requires manual execution

---

## Recommended Setup

**For Development/Testing**: Use **Option 4** (Manual) - it's working now!

**For Production**: Use **Option 1** (GitHub Actions) - it's already configured, just needs the Firebase secret added.

**For Enterprise**: Use **Option 3** (Cloud Run Jobs) - most reliable and scalable.

---

## Checking Retraining Status

All methods log to Firestore `mlRetrainingLogs` collection. You can check:

```javascript
// In Firebase Console → Firestore
// Collection: mlRetrainingLogs
// View recent entries to see retraining history
```

Or query in code:
```javascript
const logs = await db.collection('mlRetrainingLogs')
  .orderBy('timestamp', 'desc')
  .limit(10)
  .get();
```

---

## Next Steps

1. **Immediate**: Your script works manually - keep using it for now
2. **This Week**: Set up GitHub Actions by adding the Firebase secret
3. **Later**: Consider Cloud Run Jobs for production scalability

---

## Troubleshooting

**"No Firebase data exported"**:
- Check that `FIREBASE_SERVICE_ACCOUNT_KEY` is set correctly
- Verify the service account has Firestore read permissions
- Check that `mlTrainingData` collection has documents with `usedForTraining: false`

**"GitHub Actions not running"**:
- Check repository secrets are set
- Verify workflow file is in `.github/workflows/`
- Check Actions tab for error messages

**"Cloud Function not triggering"**:
- Verify function is deployed: `firebase functions:list`
- Check Cloud Scheduler in GCP Console
- Review function logs: `firebase functions:log`

