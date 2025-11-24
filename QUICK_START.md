# 🚀 Quick Start - GitHub Setup (5 Minutes)

## Step-by-Step Instructions

### 1️⃣ Create GitHub Repository (1 minute)

1. Go to: **https://github.com/new**
2. Repository name: `dental-ml-retraining`
3. Description: "Automated ML retraining for dental appointments"
4. Make it **Public** (for free Actions) OR use GitHub Education Pack
5. **Don't check any boxes** (no README, no .gitignore)
6. Click **"Create repository"**

### 2️⃣ Copy Repository URL

After creating, you'll see a page with setup instructions. Copy the repository URL:
```
https://github.com/YOUR_USERNAME/dental-ml-retraining.git
```
(Replace YOUR_USERNAME with your actual GitHub username)

### 3️⃣ Open PowerShell in Smart Scheduling Folder

1. Press `Windows Key + R`
2. Type: `powershell`
3. Press Enter
4. Type these commands:

```powershell
# Navigate to smart scheduling folder
cd "C:\Users\User\mobident\dental_appointment_app\smart scheduling"

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: ML retraining system"

# Add your GitHub repository (REPLACE WITH YOUR URL!)
git remote add origin https://github.com/YOUR_USERNAME/dental-ml-retraining.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Note:** If it asks for GitHub username/password, you may need to use a Personal Access Token instead of password.

### 4️⃣ Get Firebase Service Account Key (2 minutes)

1. Go to: **https://console.firebase.google.com**
2. Select your project
3. Click **⚙️ Settings** → **Project Settings**
4. Go to **Service Accounts** tab
5. Click **"Generate New Private Key"**
6. Click **"Generate Key"** in the popup
7. A JSON file will download - **open it** and copy ALL the content

### 5️⃣ Add Secret to GitHub (1 minute)

1. Go to your repository: `https://github.com/YOUR_USERNAME/dental-ml-retraining`
2. Click **Settings** (top menu)
3. Click **Secrets and variables** → **Actions**
4. Click **"New repository secret"**
5. Name: `FIREBASE_SERVICE_ACCOUNT_KEY`
6. Value: Paste the entire JSON content you copied
7. Click **"Add secret"**

### 6️⃣ Test It! (1 minute)

1. Go to **Actions** tab in your repository
2. You'll see **"Auto-Retrain ML Model"** workflow
3. Click on it
4. Click **"Run workflow"** button (top right)
5. Select branch: `main`
6. Click green **"Run workflow"** button
7. Watch it run! 🎉

---

## ✅ Done!

Your ML model will now:
- ✅ Retrain automatically every Sunday at 2 AM
- ✅ Learn from real appointment data
- ✅ Improve predictions over time
- ✅ Work completely automatically

---

## 🔍 Check It's Working

### View Runs:
- Go to **Actions** tab → See all runs (green = success)

### View Logs:
- Click on any run → See detailed logs

### Check Firebase:
- Go to Firestore → `mlRetrainingLogs` collection
- See retraining history

---

## 🆘 Troubleshooting

### "Can't push to GitHub"
- Make sure you're logged into GitHub
- Try using GitHub Desktop app instead
- Or use: `gh auth login` (GitHub CLI)

### "Secret not found"
- Make sure secret name is exactly: `FIREBASE_SERVICE_ACCOUNT_KEY`
- Copy entire JSON file (including { and })

### "Workflow not showing"
- Make sure `.github/workflows/retrain-model.yml` exists
- Refresh GitHub page
- Check you're on `main` branch

### "Not enough training data"
- This is normal! Need 50+ appointments
- System uses existing model until enough data

---

## 📞 Need Help?

Check these files:
- `README_GITHUB_SETUP.md` - Detailed guide
- `SETUP_GITHUB.md` - Alternative instructions
- `README.md` - General information

---

**You're all set!** 🎓🚀

