# Quick Deployment Cheat Sheet

## 🖥️ Desktop App (5 Minutes)

### Build:
```powershell
.\BUILD_DESKTOP_APP.ps1
```

### Launch:
Double-click: `dist\SkinAnalysisApp\SkinAnalysisApp.exe`

---

## ☁️ Cloud Deploy (10 Minutes)

### Render.com (FREE):
1. Push to GitHub
2. Go to render.com → New Web Service
3. Connect repo → Auto-deploy
4. Get URL: `yourapp.onrender.com`

### Railway.app:
1. Push to GitHub  
2. Go to railway.app → New Project
3. Select repo → Deploy
4. Get URL from dashboard

---

## 🚀 One-Click Local Launch

**Method 1:** Double-click `LAUNCH_APP.bat`

**Method 2:** Run in PowerShell
```powershell
.\LAUNCH_APP.ps1
```

**Method 3:** Manual
```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

Open: http://localhost:5000

---

## 🔄 Update Process

### Desktop App:
```powershell
# Make changes to code
.\BUILD_DESKTOP_APP.ps1  # Rebuild
```

### Cloud:
```powershell
git add .
git commit -m "Update"
git push  # Auto-deploys!
```

---

## ⚠️ Important Notes

1. **Model file** is 100+ MB → Use Git LFS for GitHub
2. **Free tier** cloud apps sleep after 15 min inactivity
3. **Desktop app** works offline, cloud needs internet
4. **Port 5000** must be available locally

---

## 📦 File Sizes

- Desktop .exe: ~500MB (includes everything)
- Cloud deployment: Builds on server
- Model file: Upload separately if >100MB

---

## 🎯 Best Use Cases

| Scenario | Recommendation |
|----------|----------------|
| Personal use | Desktop App |
| Share with friends | Cloud (Render) |
| Professional demo | Desktop App |
| Remote access | Cloud (Railway) |
| Offline use | Desktop App |
| Mobile access | Cloud |

