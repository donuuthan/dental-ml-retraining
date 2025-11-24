# GitHub Setup for ML Model Retraining

This guide will help you set up a GitHub repository for automated ML model retraining.

## Option 1: Create Standalone Repository (Recommended)

Create a separate repository just for the ML retraining system. This keeps it clean and focused.

### Step 1: Create New GitHub Repository

1. Go to https://github.com/new
2. Repository name: `dental-ml-retraining` (or any name you prefer)
3. Description: "Automated ML model retraining for dental appointment smart scheduling"
4. Make it **Public** (for free GitHub Actions) OR use GitHub Education Pack for private repos
5. **Don't** initialize with README, .gitignore, or license (we'll add our own)
6. Click "Create repository"

### Step 2: Initialize Local Repository

Open terminal in the `smart scheduling` folder:

```bash
cd "smart scheduling"

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: ML retraining system"
```

### Step 3: Connect to GitHub

```bash
# Replace YOUR_USERNAME and REPO_NAME with your actual values
git remote add origin https://github.com/YOUR_USERNAME/dental-ml-retraining.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 4: Add Firebase Service Account Key

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `FIREBASE_SERVICE_ACCOUNT_KEY`
5. Value: Paste the entire content of your Firebase service account JSON file
6. Click **Add secret**

### Step 5: Verify GitHub Actions

1. Go to **Actions** tab in your repository
2. You should see "Auto-Retrain ML Model" workflow
3. Click on it and click **Run workflow** to test

---

## Option 2: Add to Existing Repository

If you already have a GitHub repository for your dental app:

### Step 1: Add Files to Existing Repo

```bash
# Navigate to your main project directory
cd C:\Users\User\mobident\dental_appointment_app

# Add the smart scheduling folder
git add "smart scheduling/"
git add ".github/workflows/retrain-model.yml"

# Commit
git commit -m "Add automated ML retraining system"

# Push
git push
```

### Step 2: Add Firebase Secret

Same as Step 4 above - add `FIREBASE_SERVICE_ACCOUNT_KEY` to your repository secrets.

---

## Option 3: Minimal Standalone Repo (Just Retraining)

If you want a minimal repo with only what's needed for retraining:

### Create these files in a new folder:

```
ml-retraining/
├── auto_retrain_model.py
├── requirements.txt
├── .github/
│   └── workflows/
│       └── retrain-model.yml
├── README.md
└── .gitignore
```

Then follow the same steps as Option 1.

---

## Getting Your Firebase Service Account Key

1. Go to Firebase Console: https://console.firebase.google.com
2. Select your project
3. Click **Project Settings** (gear icon)
4. Go to **Service Accounts** tab
5. Click **Generate New Private Key**
6. Download the JSON file
7. Copy the entire content for the GitHub secret

---

## Testing the Setup

### Manual Test

1. Go to GitHub repository
2. Click **Actions** tab
3. Click **Auto-Retrain ML Model** workflow
4. Click **Run workflow** button
5. Select branch: `main`
6. Click **Run workflow**

### Check Results

- Watch the workflow run in real-time
- Check logs for any errors
- Verify model file is updated (if you have enough training data)

---

## Troubleshooting

### "Workflow not showing up"
- Make sure `.github/workflows/retrain-model.yml` exists
- Check file is committed and pushed
- Refresh GitHub page

### "Secret not found"
- Verify secret name is exactly: `FIREBASE_SERVICE_ACCOUNT_KEY`
- Check it's added to repository secrets (not environment secrets)

### "Permission denied"
- Make sure Firebase service account has Firestore read/write permissions
- Check service account key is valid

### "Not enough training data"
- Need at least 50 samples to retrain
- This is normal if you just started collecting data
- Model will use existing version until enough data is collected

---

## Schedule

The workflow runs automatically:
- **Every Sunday at 2 AM UTC**
- Can be triggered manually anytime
- Adjust schedule in `.github/workflows/retrain-model.yml` if needed

---

## Next Steps

1. ✅ Create GitHub repository
2. ✅ Push code
3. ✅ Add Firebase secret
4. ✅ Test manual run
5. ✅ Wait for first automatic run (or trigger manually)
6. ✅ Monitor in Actions tab

Your ML model will now retrain automatically every week! 🚀

