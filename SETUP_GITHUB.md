# Quick GitHub Setup Guide

## 🚀 Fastest Way to Set Up GitHub Actions

### Step 1: Create New Repository (2 minutes)

1. Go to: https://github.com/new
2. Repository name: `dental-ml-retraining`
3. Make it **Public** (free Actions) OR use GitHub Education Pack
4. **Don't** check any boxes (no README, no .gitignore)
5. Click **Create repository**

### Step 2: Copy Repository URL

After creating, GitHub will show you commands. Copy the repository URL (looks like):
```
https://github.com/YOUR_USERNAME/dental-ml-retraining.git
```

### Step 3: Run These Commands

Open PowerShell or Command Prompt in the `smart scheduling` folder:

```powershell
# Navigate to smart scheduling folder
cd "C:\Users\User\mobident\dental_appointment_app\smart scheduling"

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: ML retraining system"

# Add GitHub remote (REPLACE WITH YOUR URL)
git remote add origin https://github.com/YOUR_USERNAME/dental-ml-retraining.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 4: Add Firebase Secret (3 minutes)

1. Go to your repository: `https://github.com/YOUR_USERNAME/dental-ml-retraining`
2. Click **Settings** (top menu)
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Name: `FIREBASE_SERVICE_ACCOUNT_KEY`
6. Value: Open your Firebase service account JSON file, copy ALL content, paste here
7. Click **Add secret**

### Step 5: Test It! (1 minute)

1. Go to **Actions** tab in your repository
2. You'll see "Auto-Retrain ML Model" workflow
3. Click on it
4. Click **Run workflow** button (top right)
5. Select branch: `main`
6. Click green **Run workflow** button
7. Watch it run! 🎉

---

## ✅ That's It!

Your ML model will now:
- ✅ Retrain automatically every Sunday at 2 AM
- ✅ Learn from real appointment data
- ✅ Improve predictions over time
- ✅ Work completely automatically

---

## 🔍 How to Check It's Working

### Check GitHub Actions:
- Go to **Actions** tab
- See workflow runs (green = success, red = error)

### Check Firebase:
- Go to Firestore → `mlRetrainingLogs` collection
- See retraining history

### Check Model:
- After retraining, `smart_scheduler.pkl` will be updated
- Committed to git automatically

---

## 🆘 Troubleshooting

**"Can't push to GitHub"**
- Make sure you're logged into GitHub
- Check repository URL is correct
- Try: `git remote -v` to see your remotes

**"Secret not working"**
- Make sure secret name is exactly: `FIREBASE_SERVICE_ACCOUNT_KEY`
- Copy entire JSON file content (including { and })

**"Workflow not showing"**
- Make sure `.github/workflows/retrain-model.yml` exists
- Refresh GitHub page
- Check you're on the `main` branch

**"Not enough data"**
- This is normal! Need 50+ appointments to retrain
- System will use existing model until enough data

---

## 📝 Next Steps

1. ✅ Repository created
2. ✅ Code pushed
3. ✅ Secret added
4. ✅ Tested manually
5. ⏰ Wait for Sunday 2 AM (or trigger manually anytime)

**You're all set!** 🎓

