# 🚀 INSTALLATION GUIDE
# AI Skin Analysis & Cosmetics Recommendation System
# Complete Setup Instructions

## 📋 System Requirements

### **Minimum Requirements**
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher (Recommended: 3.9-3.11)
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space
- **Internet**: Required for initial setup and package installation

### **Recommended Requirements**
- **Python**: 3.9-3.11 (optimal TensorFlow compatibility)
- **RAM**: 8GB or more (for faster AI processing)
- **CPU**: Multi-core processor (Intel i5/AMD Ryzen 5 or better)
- **GPU**: Optional CUDA-compatible GPU for faster inference
- **Browser**: Chrome 80+, Firefox 75+, Safari 13+, or Edge 80+
- **Webcam**: For real-time photo capture feature

---

## 🛠️ Step-by-Step Installation

### **Step 1: Verify Python Installation**

#### Windows (PowerShell):
```powershell
python --version
# Should show Python 3.8+ (e.g., Python 3.9.7)
```

#### macOS/Linux (Terminal):
```bash
python3 --version
# Should show Python 3.8+ (e.g., Python 3.9.7)
```

#### If Python is not installed:
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **macOS**: Use Homebrew: `brew install python3`
- **Linux**: Use package manager: `sudo apt install python3 python3-pip`

---

### **Step 2: Navigate to Project Directory**

```powershell
# Windows PowerShell
cd "c:\Users\ASUS\OneDrive\Desktop\major project\full major project"

# Verify you're in the correct directory
ls
# Should show: app.py, requirements.txt, enhanced_cosmetics.csv, etc.
```

---

### **Step 3: Create Virtual Environment (Recommended)**

#### Option A: Using venv (Built-in)
```powershell
# Create virtual environment
python -m venv skin_analysis_env

# Activate virtual environment
# Windows:
.\skin_analysis_env\Scripts\Activate.ps1
# macOS/Linux:
source skin_analysis_env/bin/activate

# Verify activation (should show environment name)
```

#### Option B: Using conda (If Anaconda/Miniconda installed)
```powershell
# Create conda environment
conda create -n skin_analysis python=3.9

# Activate environment
conda activate skin_analysis
```

---

### **Step 4: Install Dependencies**

#### Method A: Install all requirements at once
```powershell
pip install -r requirements.txt
```

#### Method B: Install packages individually (if requirements.txt has issues)
```powershell
# Core web framework
pip install flask==3.0.0

# AI/ML packages
pip install tensorflow==2.15.0
pip install numpy==1.24.4

# Computer vision
pip install opencv-python==4.8.1.78

# Data processing
pip install pandas==2.1.4

# PDF generation
pip install reportlab==4.0.7

# Image processing
pip install pillow==10.1.0

# Additional utilities
pip install werkzeug==3.0.1
pip install jinja2==3.1.2
pip install click==8.1.7
pip install itsdangerous==2.1.2
pip install markupsafe==2.1.3
```

---

### **Step 5: Verify Installation**

#### Check installed packages:
```powershell
pip list | grep -E "(flask|tensorflow|opencv|pandas|reportlab|pillow)"
```

#### Test Python imports:
```powershell
python -c "import flask, tensorflow, cv2, pandas, reportlab; print('All packages imported successfully!')"
```

---

### **Step 6: Verify Required Files**

#### Check for essential files:
```powershell
# List files to verify presence
ls -la

# Required files checklist:
# ✓ app.py - Main Flask application
# ✓ requirements.txt - Dependencies list
# ✓ enhanced_cosmetics.csv - Product database (1,472 products)
# ✓ skin_model_final (1).h5 - AI model file
# ✓ templates/index.html - Web interface
# ✓ static/css/style.css - Styling
# ✓ static/js/script.js - Frontend functionality
```

#### Verify file sizes:
```powershell
# Model file should be substantial (>10MB)
ls -lh "skin_model_final (1).h5"

# Database should contain product data
head -n 5 enhanced_cosmetics.csv
```

---

### **Step 7: Test Application Startup**

#### Start the Flask development server:
```powershell
python app.py
```

#### Expected output:
```
Loading AI model...
Model loaded successfully!
Loading cosmetics database...
Database loaded: 1472 products available.
 * Running on http://127.0.0.1:5000
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment.
```

---

### **Step 8: Test Web Interface**

#### Open browser and navigate to:
```
http://localhost:5000
```

#### Verify interface loads with:
- ✅ Upload section with camera and file options
- ✅ Modern gradient design
- ✅ Responsive layout
- ✅ No console errors (F12 Developer Tools)

---

## 🔧 Troubleshooting Common Issues

### **Issue 1: TensorFlow Installation Problems**

#### Error: "No module named 'tensorflow'"
```powershell
# Try specific TensorFlow version
pip uninstall tensorflow
pip install tensorflow==2.15.0

# For Apple Silicon Macs:
pip install tensorflow-macos==2.15.0
```

#### Error: "Could not load dynamic library 'cudart64_110.dll'"
```powershell
# This is normal for CPU-only installations
# Add this to app.py if needed:
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
```

---

### **Issue 2: OpenCV Installation Problems**

#### Error: "No module named 'cv2'"
```powershell
pip uninstall opencv-python
pip install opencv-python-headless==4.8.1.78
```

#### Error: "ImportError: libGL.so.1"
```bash
# Linux only
sudo apt-get install libgl1-mesa-glx
```

---

### **Issue 3: Model Loading Errors**

#### Error: "Cannot load model file"
```powershell
# Verify file exists and is not corrupted
python -c "
import tensorflow as tf
try:
    model = tf.keras.models.load_model('skin_model_final (1).h5')
    print('Model loaded successfully!')
except Exception as e:
    print(f'Model loading failed: {e}')
"
```

#### Fallback: If model file is corrupted
- The application includes an automatic fallback that creates a MobileNet-based model
- Check console output for "Creating fallback model..." message

---

### **Issue 4: Port Already in Use**

#### Error: "Address already in use"
```powershell
# Find and kill process using port 5000
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# Or use different port
python -c "
import app
app.app.run(port=5001)
"
```

---

### **Issue 5: Camera Access Problems**

#### Browser doesn't request camera permission:
- Use HTTPS (required by modern browsers)
- Try different browser (Chrome recommended)
- Check browser camera permissions in settings

#### Alternative: Use file upload instead of camera

---

### **Issue 6: Memory Issues**

#### Error: "OOM when allocating tensor"
```powershell
# Reduce TensorFlow memory usage
export TF_FORCE_GPU_ALLOW_GROWTH=true  # Linux/Mac
$env:TF_FORCE_GPU_ALLOW_GROWTH="true"  # Windows PowerShell

# Or add to app.py:
import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    tf.config.experimental.set_memory_growth(gpus[0], True)
```

---

## 🚀 Performance Optimization

### **Speed up startup time:**
```python
# Add to top of app.py
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce TensorFlow logging
```

### **Reduce memory usage:**
```python
# Optimize TensorFlow for CPU
import tensorflow as tf
tf.config.threading.set_inter_op_parallelism_threads(1)
tf.config.threading.set_intra_op_parallelism_threads(1)
```

---

## 📱 Browser Configuration

### **Recommended Browser Settings:**
- **Chrome**: Enable camera/microphone permissions
- **Firefox**: Set `media.navigator.permission.disabled = false`
- **Safari**: Enable camera access in system preferences
- **Edge**: Allow camera access for localhost

### **HTTPS Setup (Optional, for camera features):**
```powershell
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Run with HTTPS
python -c "
import ssl
import app
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain('cert.pem', 'key.pem')
app.app.run(host='0.0.0.0', port=5000, ssl_context=context)
"
```

---

## 🔄 Update Instructions

### **Update dependencies:**
```powershell
pip install -r requirements.txt --upgrade
```

### **Update specific packages:**
```powershell
pip install --upgrade tensorflow opencv-python flask pandas reportlab
```

---

## 🎉 Success Checklist

After completing installation, verify:
- ✅ Python 3.8+ installed and accessible
- ✅ All dependencies installed without errors
- ✅ Flask application starts successfully  
- ✅ Web interface loads at http://localhost:5000
- ✅ Camera permission works (or file upload as alternative)
- ✅ AI model loads without errors
- ✅ Database file (enhanced_cosmetics.csv) accessible
- ✅ Sample image analysis works end-to-end

---

## 🆘 Getting Help

### **If you encounter issues:**
1. **Check error messages** in terminal/console
2. **Verify Python version** compatibility
3. **Update pip**: `python -m pip install --upgrade pip`
4. **Clear pip cache**: `pip cache purge`
5. **Try clean installation** in new virtual environment
6. **Check system resources** (RAM, disk space)

### **Contact Information:**
- Check PROJECT_DOCUMENTATION.md for detailed technical info
- Review TECHNICAL_SPECIFICATIONS.md for module details
- Create GitHub issue for bugs or feature requests

---

**🎯 You're ready to start analyzing skin conditions with AI!**

**Next Step**: Open http://localhost:5000 and upload your first image!