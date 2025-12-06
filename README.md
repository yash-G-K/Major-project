# 🌟 AI Skin Analysis & Cosmetics Recommendation System

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v3.0.0-green.svg)
![TensorFlow](https://img.shields.io/badge/tensorflow-v2.15.0-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A sophisticated web application that uses AI to analyze skin conditions through camera capture or image upload, providing personalized cosmetic product recommendations with Indian Rupee pricing, ingredient analysis, and comprehensive skincare advice.

## ✨ Enhanced Features

### 🎯 Core Functionality
- **📸 Dual Image Input**: Camera capture & file upload options
- **🧠 Advanced AI Analysis**: TensorFlow MobileNet-based classification (7 skin conditions)
- **👤 Face Detection**: OpenCV-powered validation for accurate analysis
- **💄 Product Recommendations**: 1,472+ premium cosmetics from 50+ brands
- **💰 Dual Currency Display**: USD & Indian Rupees (₹) conversion
- **🧪 Ingredient Analysis**: Detailed ingredient benefits and explanations
- **📋 Professional PDF Reports**: Comprehensive analysis with skincare routines
- **💡 Skincare Tips**: Personalized DO's & DON'Ts for each skin type
- **📱 Responsive Design**: Mobile-first, cross-platform compatibility
- **🎨 Modern UI**: Gradient design with smooth animations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam (optional, for camera features)
- Modern web browser

### Installation

1. **Clone or download the project**
   ```bash
   cd "c:\Users\ASUS\OneDrive\Desktop\major project\full major project"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify files are present**
   - `skin_model_final (1).h5` - Your trained model
   - `enhanced_cosmetics.csv` - Product database

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to: `http://localhost:5000`

## 📱 How to Use

### 1. Upload or Capture Image
- **Upload**: Click "Upload Photo" and select an image from your device
- **Camera**: Click "Take Photo" to use your device's camera
- **Drag & Drop**: Simply drag an image file onto the upload area

### 2. Image Requirements
- Must contain a clear face
- Supported formats: JPG, PNG, JPEG
- Maximum file size: 16MB
- Good lighting recommended for best results

### 3. Analysis Process
- Face detection validates the image
- AI model analyzes skin condition
- System matches condition with suitable products
- Results displayed with confidence levels

### 4. View Results
- See detected skin condition and confidence
- Browse recommended products
- View product details, prices, and ratings
- Download PDF report for your records

### 5. Download Report
- Click "Download PDF Report"
- Get comprehensive analysis with:
  - Skin condition results
  - Product recommendations table
  - Analysis timestamp
  - Professional formatting

## 🔧 Technical Details

### Skin Conditions Detected
- **Normal**: Balanced skin with no major concerns
- **Dry**: Lacking moisture, may appear flaky
- **Oily**: Excess sebum production, shiny appearance
- **Acne**: Presence of pimples, blackheads, or blemishes
- **Sensitive**: Reactive skin prone to irritation
- **Pigmentation**: Uneven skin tone, dark spots
- **Wrinkles**: Signs of aging, fine lines

### Model Architecture
- Based on MobileNet for efficient mobile deployment
- Trained on skin condition classification dataset
- Input size: 224x224 RGB images
- Output: 7 skin condition classes with confidence scores

### Product Database
- 1,474+ cosmetic products from major brands
- Detailed ingredient information
- Skin type compatibility mapping
- Price and rating information
- Brand and product name details

## 📂 Project Structure

```
full major project/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── skin_model_final (1).h5    # Trained AI model
├── enhanced_cosmetics.csv     # Product database
├── templates/
│   └── index.html             # Main web interface
├── static/
│   ├── css/
│   │   └── style.css          # Styling and animations
│   ├── js/
│   │   └── script.js          # Interactive functionality
│   └── images/                # Static images (optional)
└── uploads/                   # Temporary file storage
```

## 🛠️ Development Features

### Security & Privacy
- Images processed locally, not stored permanently
- Face detection prevents non-face image processing
- Secure file handling with size and type validation
- No user data collection or tracking

### Performance Optimizations
- Efficient MobileNet architecture
- Client-side image preview and validation
- Optimized CSS and JavaScript loading
- Responsive design for all screen sizes

### Error Handling
- Comprehensive error messages
- Graceful fallbacks for camera issues
- File validation and user feedback
- Network error recovery

## 🎨 Customization

### Adding New Skin Conditions
1. Update `SKIN_CONDITIONS` list in `app.py`
2. Retrain model with new classes
3. Update icon mapping in `script.js`
4. Adjust CSS styling if needed

### Modifying Product Recommendations
1. Update CSV file with new products
2. Modify `get_product_recommendations()` function
3. Adjust product card display in JavaScript
4. Update PDF report generation if needed

### UI Customization
1. Edit CSS variables in `style.css` for colors/fonts
2. Modify HTML structure in `index.html`
3. Update JavaScript for new interactions
4. Add custom animations or effects

## 📊 Model Information

The skin analysis model was trained using:
- **Architecture**: MobileNet (efficient for web deployment)
- **Input**: 224x224 RGB images
- **Output**: 7 skin condition classes
- **Training Platform**: Google Colab
- **Framework**: TensorFlow/Keras

## 🤝 Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## ⚠️ Disclaimer

This application is for educational and informational purposes only. The AI analysis should not replace professional dermatological advice. Always consult with a qualified dermatologist for serious skin concerns or medical conditions.

## 📞 Support

If you encounter any issues:
1. Check the console for error messages
2. Verify all files are in place
3. Ensure Python dependencies are installed
4. Test with different images
5. Check browser compatibility

## 🎯 Future Enhancements

Potential improvements for future versions:
- Multi-language support
- Skin condition severity scoring
- Ingredient analysis and allergen detection
- User accounts and history tracking
- Mobile app development
- Integration with e-commerce platforms
- Advanced analytics and insights

---

**Built with ❤️ using Flask, TensorFlow, and modern web technologies**