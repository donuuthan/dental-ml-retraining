# How to Get Your Firebase Service Account Key

## Step-by-Step Instructions

### 1. Go to Firebase Console
- Visit: https://console.firebase.google.com
- Select your project (dental-appointment-app-e1b28)

### 2. Open Project Settings
- Click the **⚙️ gear icon** (top left)
- Click **"Project Settings"**

### 3. Go to Service Accounts Tab
- Click **"Service Accounts"** tab
- You'll see "Firebase Admin SDK"

### 4. Generate New Private Key
- Click **"Generate New Private Key"** button
- A warning popup will appear
- Click **"Generate Key"** in the popup

### 5. Download JSON File
- A JSON file will automatically download
- File name looks like: `dental-appointment-app-e1b28-firebase-adminsdk-xxxxx.json`
- **Save this file somewhere safe!**

### 6. Copy Content for GitHub Secret
- Open the downloaded JSON file in Notepad
- Select ALL content (Ctrl+A)
- Copy it (Ctrl+C)
- This is what you'll paste into GitHub Secrets

### 7. Add to GitHub
- Go to your GitHub repository
- Settings → Secrets and variables → Actions
- New repository secret
- Name: `FIREBASE_SERVICE_ACCOUNT_KEY`
- Value: Paste the entire JSON content
- Add secret

## ⚠️ Security Note

- **Never commit this file to git!** (It's already in .gitignore)
- **Never share this key publicly!**
- **Only add it to GitHub Secrets** (it's encrypted there)

## File Location

The downloaded file will be in your Downloads folder:
```
C:\Users\User\Downloads\dental-appointment-app-e1b28-firebase-adminsdk-xxxxx.json
```

## What the JSON Looks Like

```json
{
  "type": "service_account",
  "project_id": "dental-appointment-app-e1b28",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "...",
  "token_uri": "...",
  ...
}
```

Copy the ENTIRE file content (including the curly braces).

