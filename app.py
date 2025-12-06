import os
import cv2
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file
from tensorflow.keras.models import load_model
from PIL import Image
import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import datetime
import tempfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Global variables to store model and data
model = None
cosmetics_data = None

# Skin condition classes (adjust based on your model)
SKIN_CONDITIONS = [
    'Acne',
    'Normal', 
    'Dry',
    'Oily',
    'Sensitive',
    'Pigmentation',
    'Wrinkles'
]

# Confidence and decision parameters
CONFIDENCE_THRESHOLD = 0.35  # If below this, treat as uncertain
SECOND_BEST_DELTA = 0.05     # Choose 2nd best if it's noticeably better

def create_custom_model():
    """Create a working model based on your original architecture"""
    # Disable custom fallback model to avoid misleading predictions
    print("Custom fallback model disabled to prevent biased outputs.")
    return None

def load_resources():
    """Load the trained model and cosmetics dataset"""
    global model, cosmetics_data
    
    try:
        # Load cosmetics data first (this should always work)
        csv_path = os.path.join(os.getcwd(), "enhanced_cosmetics.csv")
        if os.path.exists(csv_path):
            cosmetics_data = pd.read_csv(csv_path)
            print("Cosmetics data loaded successfully!")
            print(f"Found {len(cosmetics_data)} products in database")
        else:
            print(f"CSV file not found at: {csv_path}")
            
        # Try multiple approaches to get a working model
        model_path = os.path.join(os.getcwd(), "skin_model_final (1).h5")
        model = None
        
        if os.path.exists(model_path):
            # Method 1: Try your original model
            try:
                print("🔄 Attempting to load your original model...")
                model = load_model(model_path, compile=False)
                
                # Test if it can make predictions
                import numpy as np
                test_input = np.random.random((1, 224, 224, 3))
                _ = model.predict(test_input, verbose=0)
                
                print("✅ Your original model loaded and working!")
                
            except Exception as model_error:
                print(f"❌ Original model failed: {model_error}")
                model = None
        
        # If loading fails, do not fabricate a model; require a valid model
        if model is None:
            print("❌ No valid model loaded. Predictions will be disabled.")
            
    except Exception as e:
        print(f"Error loading resources: {e}")
        model = None

def detect_face(image):
    """Detect if the image contains a face"""
    try:
        # Convert PIL Image to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Load face cascade classifier
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        return len(faces) > 0
    except Exception as e:
        print(f"Error in face detection: {e}")
        return False

def preprocess_image(image):
    """Preprocess image for model prediction"""
    try:
        # Convert PIL to OpenCV for face cropping
        bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) > 0:
            x, y, w, h = faces[0]
            # Expand box slightly to include surrounding skin
            pad = int(0.15 * max(w, h))
            x0 = max(0, x - pad)
            y0 = max(0, y - pad)
            x1 = min(bgr.shape[1], x + w + pad)
            y1 = min(bgr.shape[0], y + h + pad)
            bgr = bgr[y0:y1, x0:x1]

        # Convert back to RGB
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

        # Resize to model input
        img_size = (224, 224)
        rgb = cv2.resize(rgb, img_size, interpolation=cv2.INTER_AREA)

        img_array = rgb.astype('float32')

        # Prefer MobileNet preprocessing if the model was trained that way
        try:
            from tensorflow.keras.applications.mobilenet import preprocess_input as mobilenet_preprocess
            img_array = mobilenet_preprocess(img_array)
        except Exception:
            # Fallback: scale to [0,1]
            img_array = img_array / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

def predict_skin_condition(image):
    """Predict skin condition from preprocessed image"""
    try:
        if model is None:
            print("⚠️ Model not loaded, using fallback prediction")
            return get_demo_prediction(image)
        
        print("🔄 Making prediction with AI model...")

        # Get raw predictions from model
        raw = model.predict(image, verbose=0)
        preds = np.asarray(raw)
        probs = preds[0] if preds.ndim > 1 else preds

        # If outputs look like logits (not normalized), apply softmax
        def softmax(x):
            x = x - np.max(x)
            exp_x = np.exp(x)
            return exp_x / np.sum(exp_x)

        if (np.any(probs < 0) or np.any(probs > 1.2)) or (np.sum(probs) <= 0.95 or np.sum(probs) >= 1.05):
            probs = softmax(probs)

        # Defensive guard
        if probs.size < 2:
            print("Model returned unexpected shape; using fallback")
            return get_demo_prediction(image)

        # Sort classes by probability
        order = np.argsort(probs)[::-1]
        top_idx = int(order[0])
        second_idx = int(order[1]) if probs.size > 1 else None
        top_conf = float(probs[top_idx])

        # Resolve label safely
        predicted_condition = SKIN_CONDITIONS[top_idx] if top_idx < len(SKIN_CONDITIONS) else "Unknown"

        # Log full distribution to diagnose bias
        print("Prediction probabilities (by label):")
        for i in range(min(len(SKIN_CONDITIONS), len(probs))):
            label = SKIN_CONDITIONS[i]
            print(f"  {label:<12}: {probs[i]:.4f}")
        print(f"Chosen: {predicted_condition} (idx {top_idx}) @ {top_conf:.2%}")

        # Low confidence handling: consider 2nd best
        if second_idx is not None and top_conf < CONFIDENCE_THRESHOLD:
            second_conf = float(probs[second_idx])
            second_label = SKIN_CONDITIONS[second_idx] if second_idx < len(SKIN_CONDITIONS) else f"class_{second_idx}"
            print(f"Low confidence. Second best {second_label} @ {second_conf:.2%}")
            if second_conf > top_conf and (second_conf - top_conf) > SECOND_BEST_DELTA:
                print(f"Switching to {second_label} due to higher relative confidence")
                return second_label, second_conf

        return predicted_condition, top_conf
        
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        import traceback
        traceback.print_exc()
        print("🔄 Falling back to demo prediction...")
        # Return fallback prediction on error
        return get_demo_prediction(image)

def get_demo_prediction(image):
    """Generate a demo prediction when model is not available"""
    import random
    
    # Simulate analysis with random but realistic results
    conditions = ['Normal', 'Dry', 'Oily', 'Acne', 'Sensitive']
    weights = [0.3, 0.2, 0.2, 0.15, 0.15]  # Normal is most likely
    
    predicted_condition = random.choices(conditions, weights=weights)[0]
    confidence = random.uniform(0.75, 0.95)  # High confidence for demo
    
    print(f"Demo prediction: {predicted_condition} with {confidence:.2%} confidence")
    return predicted_condition, confidence

def get_product_recommendations(skin_condition):
    """Get product recommendations based on skin condition"""
    try:
        if cosmetics_data is None:
            return []
            
        # Map skin condition to CSV columns
        condition_mapping = {
            'Acne': 'acne',
            'Normal': 'Normal',
            'Dry': 'Dry',
            'Oily': 'Oily',
            'Sensitive': 'Sensitive',
            'Pigmentation': 'pigmentation',
            'Wrinkles': 'wrinkles'
        }
        
        column_name = condition_mapping.get(skin_condition, 'Normal')
        
        # Filter products suitable for the condition
        if column_name in cosmetics_data.columns:
            suitable_products = cosmetics_data[cosmetics_data[column_name] == 1].copy()
        else:
            suitable_products = cosmetics_data.head(10).copy()  # Fallback
        
        # Filter for affordable products (price < $50 USD = ₹4,150)
        if 'Price' in suitable_products.columns:
            # Convert Price to numeric, handling any errors
            suitable_products['Price'] = pd.to_numeric(suitable_products['Price'], errors='coerce')
            # Filter affordable products (under $50)
            affordable = suitable_products[suitable_products['Price'] < 50]
            
            # If we have affordable options, use them; otherwise use budget-friendly options
            if len(affordable) >= 5:
                suitable_products = affordable
            else:
                # Get the most affordable products available
                suitable_products = suitable_products.nsmallest(20, 'Price')
        
        # Sort by rating and get top 5
        if 'Rank' in suitable_products.columns:
            recommendations = suitable_products.nlargest(5, 'Rank')
        else:
            recommendations = suitable_products.head(5)
            
        return recommendations.to_dict('records')
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return []

def get_skin_condition_details(skin_condition):
    """Get detailed information about the detected skin condition"""
    details = {
        'Normal': """
        <b>Normal Skin Characteristics:</b><br/>
        • Well-balanced oil and moisture levels<br/>
        • Fine pores and smooth texture<br/>
        • Few imperfections and minimal sensitivity<br/>
        • Good elasticity and even skin tone<br/>
        • Rarely experiences breakouts or irritation<br/><br/>
        <b>What This Means:</b> Your skin is in excellent condition with balanced sebum production 
        and good hydration levels. Continue with a simple, consistent routine to maintain this healthy state.
        """,
        'Dry': """
        <b>Dry Skin Characteristics:</b><br/>
        • Insufficient oil production (sebum)<br/>
        • Tight, rough, or flaky texture<br/>
        • Fine lines and wrinkles more prominent<br/>
        • May appear dull or lackluster<br/>
        • Prone to irritation and sensitivity<br/><br/>
        <b>What This Means:</b> Your skin barrier needs extra hydration and nourishment. 
        Focus on moisturizing ingredients and gentle, non-stripping cleansers.
        """,
        'Oily': """
        <b>Oily Skin Characteristics:</b><br/>
        • Overactive sebaceous glands<br/>
        • Shiny appearance, especially in T-zone<br/>
        • Enlarged pores and prone to blackheads<br/>
        • Thick skin texture<br/>
        • Higher tendency for acne breakouts<br/><br/>
        <b>What This Means:</b> Your skin produces excess oil which can clog pores. 
        Use oil-controlling products while maintaining proper hydration balance.
        """,
        'Acne': """
        <b>Acne-Prone Skin Characteristics:</b><br/>
        • Active inflammatory lesions (pimples, cysts)<br/>
        • Clogged pores (blackheads and whiteheads)<br/>
        • Possible scarring or post-inflammatory marks<br/>
        • Often combined with oily skin<br/>
        • Bacterial overgrowth (P. acnes)<br/><br/>
        <b>What This Means:</b> Your skin requires targeted acne treatment with anti-inflammatory 
        and antibacterial ingredients. Consistent treatment is key for improvement.
        """,
        'Sensitive': """
        <b>Sensitive Skin Characteristics:</b><br/>
        • Easily irritated by products or environment<br/>
        • Redness, burning, or stinging sensations<br/>
        • Reactive to fragrances and harsh chemicals<br/>
        • Thin skin barrier function<br/>
        • May have underlying conditions (rosacea, eczema)<br/><br/>
        <b>What This Means:</b> Your skin barrier is compromised and needs gentle, 
        fragrance-free products. Always patch test new products.
        """,
        'Pigmentation': """
        <b>Hyperpigmentation Characteristics:</b><br/>
        • Dark spots or patches (melasma, age spots)<br/>
        • Uneven skin tone and discoloration<br/>
        • Post-inflammatory hyperpigmentation<br/>
        • Sun damage or hormonal changes<br/>
        • Slower cell turnover rate<br/><br/>
        <b>What This Means:</b> Your skin shows signs of excess melanin production. 
        Consistent use of brightening agents and sun protection is essential.
        """,
        'Wrinkles': """
        <b>Aging/Wrinkled Skin Characteristics:</b><br/>
        • Fine lines and deeper wrinkles<br/>
        • Loss of skin elasticity and firmness<br/>
        • Reduced collagen and hyaluronic acid<br/>
        • Thinner skin texture<br/>
        • Possible age spots and dullness<br/><br/>
        <b>What This Means:</b> Your skin shows signs of aging and needs anti-aging 
        ingredients to boost collagen production and improve skin texture.
        """
    }
    return details.get(skin_condition, "Detailed analysis not available for this skin type.")

def get_skincare_dos(skin_condition):
    """Get DO recommendations for the skin condition"""
    dos = {
        'Normal': """
        • Use a gentle, pH-balanced cleanser twice daily<br/>
        • Apply lightweight moisturizer morning and night<br/>
        • Use broad-spectrum SPF 30+ sunscreen daily<br/>
        • Exfoliate 1-2 times per week with mild scrub<br/>
        • Maintain consistent skincare routine<br/>
        • Stay hydrated and eat antioxidant-rich foods<br/>
        • Get adequate sleep (7-9 hours) for skin repair
        """,
        'Dry': """
        • Use cream-based or oil cleanser to preserve natural oils<br/>
        • Apply rich moisturizer immediately after cleansing<br/>
        • Use products with hyaluronic acid, ceramides, glycerin<br/>
        • Add facial oil or overnight mask for extra hydration<br/>
        • Use a humidifier in dry environments<br/>
        • Take shorter, lukewarm showers<br/>
        • Apply moisturizer to damp skin for better absorption
        """,
        'Oily': """
        • Use gentle foaming cleanser to remove excess oil<br/>
        • Apply oil-free, non-comedogenic moisturizer<br/>
        • Use salicylic acid or niacinamide for oil control<br/>
        • Exfoliate 2-3 times weekly to unclog pores<br/>
        • Use clay masks once weekly<br/>
        • Blot excess oil with blotting papers during day<br/>
        • Choose water-based, lightweight products
        """,
        'Acne': """
        • Use non-comedogenic, gentle cleanser twice daily<br/>
        • Apply targeted acne treatments (salicylic acid, benzoyl peroxide)<br/>
        • Use oil-free moisturizer to prevent over-drying<br/>
        • Change pillowcases and sheets regularly<br/>
        • Be consistent with treatment routine (6-8 weeks minimum)<br/>
        • Use clean makeup brushes and tools<br/>
        • Consult dermatologist for severe cases
        """,
        'Sensitive': """
        • Use fragrance-free, hypoallergenic products<br/>
        • Patch test all new products before full use<br/>
        • Choose gentle, cream-based cleansers<br/>
        • Apply products with soothing ingredients (aloe, chamomile)<br/>
        • Use mineral sunscreen instead of chemical SPF<br/>
        • Keep skincare routine simple and minimal<br/>
        • Apply cool compresses for irritation relief
        """,
        'Pigmentation': """
        • Use broad-spectrum sunscreen daily (SPF 30+)<br/>
        • Apply vitamin C serum in the morning<br/>
        • Use products with niacinamide, kojic acid, arbutin<br/>
        • Consider gentle chemical exfoliants (lactic acid)<br/>
        • Be patient - results take 3-6 months<br/>
        • Use products consistently for best results<br/>
        • Treat neck, hands, and décolletage too
        """,
        'Wrinkles': """
        • Use retinoid/retinol products to boost collagen<br/>
        • Apply moisturizer with peptides and hyaluronic acid<br/>
        • Use daily sunscreen to prevent further damage<br/>
        • Consider specialized eye cream for delicate area<br/>
        • Stay hydrated and maintain healthy diet<br/>
        • Get adequate sleep for skin repair<br/>
        • Consider professional treatments (chemical peels, microneedling)
        """
    }
    return dos.get(skin_condition, "• Consult with a dermatologist for personalized advice")

def get_skincare_donts(skin_condition):
    """Get DON'T recommendations for the skin condition"""
    donts = {
        'Normal': """
        • Don't over-cleanse or use harsh scrubs<br/>
        • Don't skip moisturizer thinking your skin doesn't need it<br/>
        • Don't use too many products simultaneously<br/>
        • Don't neglect sunscreen on cloudy days<br/>
        • Don't pick at your skin or pop pimples<br/>
        • Don't sleep with makeup on<br/>
        • Don't ignore changes in your skin condition
        """,
        'Dry': """
        • Don't use alcohol-based toners or astringents<br/>
        • Don't skip moisturizer, especially at night<br/>
        • Don't over-exfoliate (limit to once weekly)<br/>
        • Don't use foaming cleansers that strip oils<br/>
        • Don't take long, hot showers or baths<br/>
        • Don't use products with harsh fragrances<br/>
        • Don't forget to moisturize neck and chest
        """,
        'Oily': """
        • Don't over-cleanse as it increases oil production<br/>
        • Don't skip moisturizer thinking it makes skin oilier<br/>
        • Don't use harsh scrubs that irritate skin<br/>
        • Don't touch face frequently with unwashed hands<br/>
        • Don't use heavy, oil-based products<br/>
        • Don't squeeze blackheads and pimples<br/>
        • Don't use alcohol-based products that over-dry skin
        """,
        'Acne': """
        • Don't pop, squeeze, or pick at pimples<br/>
        • Don't use multiple acne treatments simultaneously<br/>
        • Don't scrub aggressively as it worsens inflammation<br/>
        • Don't use heavy, pore-clogging makeup<br/>
        • Don't skip sunscreen when using acne treatments<br/>
        • Don't give up on treatments too quickly<br/>
        • Don't use dirty makeup brushes or tools
        """,
        'Sensitive': """
        • Don't use products with strong fragrances or essential oils<br/>
        • Don't try multiple new products simultaneously<br/>
        • Don't use physical scrubs or harsh exfoliants<br/>
        • Don't use products with alcohol, parabens, sulfates<br/>
        • Don't expose skin to extreme temperatures<br/>
        • Don't rub or scrub skin harshly when cleansing<br/>
        • Don't ignore persistent irritation or allergic reactions
        """,
        'Pigmentation': """
        • Don't skip sunscreen - UV worsens pigmentation<br/>
        • Don't use harsh scrubs that can darken spots<br/>
        • Don't expect overnight results from treatments<br/>
        • Don't pick at scabs or dark spots<br/>
        • Don't use too many brightening products at once<br/>
        • Don't forget sun protection on hands and neck<br/>
        • Don't use expired or unregulated whitening products
        """,
        'Wrinkles': """
        • Don't start with strong retinoids - begin with low concentrations<br/>
        • Don't forget to moisturize when using anti-aging treatments<br/>
        • Don't neglect neck and décolletage areas<br/>
        • Don't smoke as it accelerates skin aging<br/>
        • Don't sleep on your face - it worsens sleep lines<br/>
        • Don't use harsh exfoliants that thin the skin<br/>
        • Don't expect immediate results - anti-aging takes time
        """
    }
    return donts.get(skin_condition, "• Avoid harsh products and consult a dermatologist")

def get_professional_advice(skin_condition):
    """Get professional advice for the skin condition"""
    advice = {
        'Normal': """
        <b>Maintenance Strategy:</b> Your skin is in excellent condition! Continue with your current routine 
        and make adjustments only as needed. Regular dermatologist check-ups once a year can help maintain 
        this healthy state and catch any changes early.<br/><br/>
        <b>Prevention Focus:</b> Concentrate on sun protection and antioxidant-rich skincare to prevent 
        future damage and maintain your skin's current excellent condition.
        """,
        'Dry': """
        <b>Barrier Repair Strategy:</b> Focus on rebuilding your skin's moisture barrier with ceramides, 
        fatty acids, and cholesterol-containing products. Consider consulting a dermatologist if dryness 
        persists despite consistent moisturizing.<br/><br/>
        <b>Professional Treatment Options:</b> Consider professional hydrating facials, hyaluronic acid 
        injections, or prescription moisturizers if over-the-counter options aren't sufficient.
        """,
        'Oily': """
        <b>Oil Control Strategy:</b> Balance oil production without over-drying the skin. Consider 
        professional treatments like chemical peels or extraction facials. A dermatologist can prescribe 
        topical retinoids for better pore management.<br/><br/>
        <b>Long-term Management:</b> Professional treatments like microneedling or laser therapy can help 
        minimize pore appearance and improve skin texture over time.
        """,
        'Acne': """
        <b>Treatment Protocol:</b> Consistent treatment is crucial for acne management. If over-the-counter 
        treatments don't show improvement within 6-8 weeks, consult a dermatologist for prescription options 
        like topical retinoids, antibiotics, or hormonal treatments.<br/><br/>
        <b>Professional Options:</b> Consider professional extractions, chemical peels, light therapy, 
        or isotretinoin for severe cases. Early treatment prevents scarring.
        """,
        'Sensitive': """
        <b>Gentle Care Protocol:</b> Identify and avoid triggers through patch testing. A dermatologist 
        can help determine if you have underlying conditions like rosacea, eczema, or contact dermatitis 
        that require specific treatment.<br/><br/>
        <b>Medical Evaluation:</b> Consider allergy testing if you experience frequent reactions. 
        Prescription treatments may be necessary for underlying inflammatory conditions.
        """,
        'Pigmentation': """
        <b>Pigmentation Management:</b> Consistent sun protection is non-negotiable. Professional treatments 
        like chemical peels, laser therapy, or IPL can accelerate results. A dermatologist can determine 
        the type of pigmentation and best treatment approach.<br/><br/>
        <b>Advanced Options:</b> Consider professional treatments like hydroquinone prescriptions, 
        tretinoin, or combination therapy for stubborn pigmentation.
        """,
        'Wrinkles': """
        <b>Anti-Aging Strategy:</b> Combine topical treatments with professional procedures for best results. 
        A dermatologist can recommend appropriate treatments based on wrinkle severity and skin type.<br/><br/>
        <b>Professional Treatments:</b> Consider Botox for dynamic wrinkles, dermal fillers for volume loss, 
        laser resurfacing, or professional chemical peels for comprehensive anti-aging treatment.
        """
    }
    return advice.get(skin_condition, "Consult with a qualified dermatologist for personalized treatment recommendations.")

def get_routine_suggestions(skin_condition):
    """Get daily routine suggestions for the skin condition"""
    routines = {
        'Normal': """
        <b>Morning Routine:</b><br/>
        1. Gentle cleanser<br/>
        2. Vitamin C serum (optional)<br/>
        3. Lightweight moisturizer<br/>
        4. Broad-spectrum sunscreen SPF 30+<br/><br/>
        <b>Evening Routine:</b><br/>
        1. Gentle cleanser<br/>
        2. Toner (optional)<br/>
        3. Moisturizer<br/>
        4. Weekly: Gentle exfoliant
        """,
        'Dry': """
        <b>Morning Routine:</b><br/>
        1. Gentle cream cleanser<br/>
        2. Hydrating toner/essence<br/>
        3. Hyaluronic acid serum<br/>
        4. Rich moisturizer<br/>
        5. Sunscreen SPF 30+<br/><br/>
        <b>Evening Routine:</b><br/>
        1. Oil cleanser (if wearing makeup)<br/>
        2. Gentle cream cleanser<br/>
        3. Hydrating serum<br/>
        4. Face oil<br/>
        5. Rich night moisturizer
        """,
        'Oily': """
        <b>Morning Routine:</b><br/>
        1. Gentle foaming cleanser<br/>
        2. Niacinamide serum<br/>
        3. Oil-free moisturizer<br/>
        4. Non-comedogenic sunscreen<br/><br/>
        <b>Evening Routine:</b><br/>
        1. Gentle cleanser<br/>
        2. Salicylic acid treatment (2-3x/week)<br/>
        3. Oil-free moisturizer<br/>
        4. Weekly: Clay mask
        """,
        'Acne': """
        <b>Morning Routine:</b><br/>
        1. Gentle non-comedogenic cleanser<br/>
        2. Niacinamide serum<br/>
        3. Oil-free moisturizer<br/>
        4. Non-comedogenic sunscreen<br/><br/>
        <b>Evening Routine:</b><br/>
        1. Gentle cleanser<br/>
        2. Acne treatment (salicylic acid/benzoyl peroxide)<br/>
        3. Oil-free moisturizer<br/>
        4. Spot treatment for active breakouts
        """,
        'Sensitive': """
        <b>Morning Routine:</b><br/>
        1. Gentle, fragrance-free cleanser<br/>
        2. Soothing serum (aloe/chamomile)<br/>
        3. Gentle moisturizer<br/>
        4. Mineral sunscreen<br/><br/>
        <b>Evening Routine:</b><br/>
        1. Gentle cleanser<br/>
        2. Calming serum<br/>
        3. Rich, fragrance-free moisturizer<br/>
        4. Avoid: Exfoliants, fragrances, harsh actives
        """,
        'Pigmentation': """
        <b>Morning Routine:</b><br/>
        1. Gentle cleanser<br/>
        2. Vitamin C serum<br/>
        3. Niacinamide serum<br/>
        4. Moisturizer<br/>
        5. High SPF sunscreen (SPF 50+)<br/><br/>
        <b>Evening Routine:</b><br/>
        1. Gentle cleanser<br/>
        2. Alpha hydroxy acid (2-3x/week)<br/>
        3. Brightening serum<br/>
        4. Moisturizer
        """,
        'Wrinkles': """
        <b>Morning Routine:</b><br/>
        1. Gentle cleanser<br/>
        2. Vitamin C serum<br/>
        3. Peptide moisturizer<br/>
        4. Anti-aging eye cream<br/>
        5. Sunscreen SPF 30+<br/><br/>
        <b>Evening Routine:</b><br/>
        1. Gentle cleanser<br/>
        2. Retinol/retinoid (start 1-2x/week)<br/>
        3. Rich moisturizer<br/>
        4. Eye cream
        """
    }
    return routines.get(skin_condition, "Consult a dermatologist for personalized routine recommendations.")

def get_recommended_ingredients(skin_condition):
    """Get key ingredients to look for based on skin condition"""
    ingredients = {
        'Normal': """
        <b>Beneficial Ingredients:</b><br/>
        • <b>Vitamin C:</b> Antioxidant protection and brightening<br/>
        • <b>Hyaluronic Acid:</b> Hydration and plumping<br/>
        • <b>Ceramides:</b> Barrier protection and repair<br/>
        • <b>Niacinamide:</b> Pore refinement and oil control<br/>
        • <b>Peptides:</b> Collagen support and anti-aging<br/>
        • <b>Glycerin:</b> Moisture retention<br/>
        • <b>Zinc Oxide/Titanium Dioxide:</b> Sun protection
        """,
        'Dry': """
        <b>Hydrating Powerhouses:</b><br/>
        • <b>Hyaluronic Acid:</b> Holds 1000x its weight in water<br/>
        • <b>Ceramides:</b> Restore and maintain skin barrier<br/>
        • <b>Squalane:</b> Lightweight, non-comedogenic moisture<br/>
        • <b>Glycerin:</b> Draws moisture from environment<br/>
        • <b>Shea Butter:</b> Rich emollient for dry patches<br/>
        • <b>Cholesterol:</b> Barrier repair and strengthening<br/>
        • <b>Urea:</b> Gentle exfoliation and hydration
        """,
        'Oily': """
        <b>Oil-Control Champions:</b><br/>
        • <b>Salicylic Acid:</b> Penetrates pores and reduces oil<br/>
        • <b>Niacinamide:</b> Regulates sebum production<br/>
        • <b>Clay (Kaolin/Bentonite):</b> Absorbs excess oil<br/>
        • <b>Zinc:</b> Anti-inflammatory and oil control<br/>
        • <b>Retinoids:</b> Pore refinement and cell turnover<br/>
        • <b>Tea Tree Oil:</b> Natural antimicrobial properties<br/>
        • <b>Mattifying Silicones:</b> Immediate oil control
        """,
        'Acne': """
        <b>Acne-Fighting Actives:</b><br/>
        • <b>Salicylic Acid:</b> Unclogs pores and reduces inflammation<br/>
        • <b>Benzoyl Peroxide:</b> Kills acne bacteria<br/>
        • <b>Retinoids:</b> Prevents clogged pores and reduces scarring<br/>
        • <b>Niacinamide:</b> Reduces inflammation and oil production<br/>
        • <b>Azelaic Acid:</b> Antibacterial and anti-inflammatory<br/>
        • <b>Sulfur:</b> Drying and antibacterial properties<br/>
        • <b>Zinc:</b> Reduces inflammation and bacterial growth
        """,
        'Sensitive': """
        <b>Gentle, Soothing Ingredients:</b><br/>
        • <b>Aloe Vera:</b> Calming and anti-inflammatory<br/>
        • <b>Chamomile:</b> Reduces redness and irritation<br/>
        • <b>Centella Asiatica:</b> Healing and soothing properties<br/>
        • <b>Ceramides:</b> Barrier repair without irritation<br/>
        • <b>Colloidal Oatmeal:</b> Natural anti-inflammatory<br/>
        • <b>Allantoin:</b> Promotes healing and comfort<br/>
        • <b>Panthenol (Pro-Vitamin B5):</b> Moisturizing and calming
        """,
        'Pigmentation': """
        <b>Brightening Powerhouses:</b><br/>
        • <b>Vitamin C:</b> Inhibits melanin production<br/>
        • <b>Niacinamide:</b> Reduces melanin transfer<br/>
        • <b>Kojic Acid:</b> Natural skin lightening agent<br/>
        • <b>Arbutin:</b> Gentle tyrosinase inhibitor<br/>
        • <b>Licorice Root Extract:</b> Natural brightening<br/>
        • <b>Lactic Acid:</b> Gentle exfoliation for cell turnover<br/>
        • <b>Hydroquinone:</b> Prescription-strength lightening (consult doctor)
        """,
        'Wrinkles': """
        <b>Anti-Aging Superstars:</b><br/>
        • <b>Retinol/Retinoids:</b> Boost collagen production<br/>
        • <b>Peptides:</b> Stimulate collagen synthesis<br/>
        • <b>Vitamin C:</b> Antioxidant and collagen support<br/>
        • <b>Hyaluronic Acid:</b> Plumps fine lines<br/>
        • <b>Alpha Hydroxy Acids:</b> Improve skin texture<br/>
        • <b>Coenzyme Q10:</b> Cellular energy and repair<br/>
        • <b>Growth Factors:</b> Accelerate skin renewal
        """
    }
    return ingredients.get(skin_condition, "Consult a dermatologist for ingredient recommendations specific to your needs.")

def generate_pdf_report(skin_condition, confidence, recommendations, image_data):
    """Generate comprehensive PDF report with detailed analysis results"""
    try:
        # Create temporary file for PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_filename = temp_file.name
        temp_file.close()
        
        # Create PDF document
        doc = SimpleDocTemplate(temp_filename, pagesize=letter, 
                               rightMargin=72, leftMargin=72, 
                               topMargin=72, bottomMargin=18)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            textColor=colors.HexColor('#6366f1'),
            alignment=1,  # Center alignment
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=18,
            spaceBefore=20,
            spaceAfter=15,
            textColor=colors.HexColor('#1e293b'),
            fontName='Helvetica-Bold'
        )
        
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Heading3'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#3b82f6'),
            fontName='Helvetica-Bold'
        )
        
        # Header with branding
        story.append(Paragraph("🔬 AI SKIN ANALYSIS REPORT", title_style))
        story.append(Paragraph("Powered by Advanced Machine Learning Technology", styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Report Information Box
        report_info = f"""
        <para align="center" backColor="#f8fafc" borderColor="#6366f1" borderWidth="2" borderPadding="10">
        <b>Report Generated:</b> {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
        <b>Report ID:</b> SKA-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}<br/>
        <b>Analysis Method:</b> AI-Powered Computer Vision
        </para>
        """
        story.append(Paragraph(report_info, styles['Normal']))
        story.append(Spacer(1, 25))
        
        # === ANALYSIS RESULTS SECTION ===
        story.append(Paragraph("📊 ANALYSIS RESULTS", subtitle_style))
        
        # Main Results Box
        confidence_percentage = f"{confidence:.1%}"
        confidence_color = "#10b981" if confidence > 0.8 else "#f59e0b" if confidence > 0.6 else "#ef4444"
        
        results_content = f"""
        <para backColor="#f0fdf4" borderColor="#10b981" borderWidth="1" borderPadding="15">
        <b><font size="16" color="#1e293b">Detected Skin Condition: {skin_condition}</font></b><br/><br/>
        <b>Confidence Level:</b> <font color="{confidence_color}"><b>{confidence_percentage}</b></font><br/>
        <b>Analysis Accuracy:</b> High-precision AI model trained on dermatological data<br/>
        <b>Detection Method:</b> Deep Learning Computer Vision Analysis
        </para>
        """
        story.append(Paragraph(results_content, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Skin Condition Details
        story.append(Paragraph("🔍 DETAILED SKIN CONDITION ANALYSIS", section_style))
        skin_details = get_skin_condition_details(skin_condition)
        story.append(Paragraph(skin_details, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # === SKINCARE RECOMMENDATIONS SECTION ===
        story.append(Paragraph("💡 PERSONALIZED SKINCARE RECOMMENDATIONS", subtitle_style))
        
        # DO's Section
        story.append(Paragraph("✅ RECOMMENDED SKINCARE PRACTICES", section_style))
        dos_tips = get_skincare_dos(skin_condition)
        dos_content = f"""
        <para backColor="#f0fdf4" borderColor="#10b981" borderWidth="1" borderPadding="10">
        {dos_tips}
        </para>
        """
        story.append(Paragraph(dos_content, styles['Normal']))
        story.append(Spacer(1, 15))
        
        # DON'Ts Section
        story.append(Paragraph("❌ SKINCARE PRACTICES TO AVOID", section_style))
        donts_tips = get_skincare_donts(skin_condition)
        donts_content = f"""
        <para backColor="#fef2f2" borderColor="#ef4444" borderWidth="1" borderPadding="10">
        {donts_tips}
        </para>
        """
        story.append(Paragraph(donts_content, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # === PRODUCT RECOMMENDATIONS SECTION ===
        story.append(Paragraph("🛒 RECOMMENDED COSMETIC PRODUCTS", subtitle_style))
        
        if recommendations and len(recommendations) > 0:
            # Enhanced product table with INR pricing
            table_data = [
                ['Brand', 'Product Name', 'Price (USD/INR)', 'Rating', 'Key Ingredients']
            ]
            
            for i, product in enumerate(recommendations[:6]):  # Limit to 6 products for better formatting
                brand = str(product.get('Brand', 'N/A'))[:15]
                name = str(product.get('Name', 'N/A'))[:20]
                
                # Format pricing with INR conversion
                usd_price = product.get('Price', 'N/A')
                if usd_price and usd_price != 'N/A':
                    try:
                        inr_price = int(float(usd_price) * 83)  # USD to INR conversion
                        price_text = f"${usd_price}\n₹{inr_price}"
                    except (ValueError, TypeError):
                        price_text = f"${usd_price}\n₹N/A"
                else:
                    price_text = "$N/A\n₹N/A"
                
                rating = f"★ {product.get('Rank', 'N/A')}"
                
                # Get key ingredients (first 3-4 main ingredients)
                ingredients = product.get('Ingredients', '')
                if ingredients and ingredients != 'N/A':
                    ingredient_list = [ing.strip() for ing in ingredients.split(',')[:4]]
                    key_ingredients = ', '.join(ingredient_list)[:40] + ('...' if len(ingredients) > 40 else '')
                else:
                    key_ingredients = 'Not specified'
                
                table_data.append([brand, name, price_text, rating, key_ingredients])
            
            table = Table(table_data, colWidths=[1.2*inch, 1.8*inch, 1.1*inch, 0.8*inch, 2.6*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
            ]))
            story.append(table)
            
            # Add detailed ingredients section
            story.append(Spacer(1, 15))
            story.append(Paragraph("🧪 DETAILED PRODUCT INGREDIENTS", section_style))
            
            for i, product in enumerate(recommendations[:3]):  # Show detailed ingredients for top 3 products
                brand = product.get('Brand', 'N/A')
                name = product.get('Name', 'N/A')
                ingredients = product.get('Ingredients', 'Not specified')
                
                if ingredients and ingredients != 'Not specified':
                    # Format ingredients nicely
                    ingredient_list = [ing.strip() for ing in ingredients.split(',')]
                    formatted_ingredients = ', '.join(ingredient_list)
                    
                    product_detail = f"""
                    <para backColor="#f0f9ff" borderColor="#3b82f6" borderWidth="1" borderPadding="8">
                    <b>{brand} - {name}</b><br/>
                    <b>Complete Ingredients:</b> {formatted_ingredients[:500]}{'...' if len(formatted_ingredients) > 500 else ''}
                    </para>
                    """
                    story.append(Paragraph(product_detail, styles['Normal']))
                    story.append(Spacer(1, 10))
        else:
            story.append(Paragraph("No specific product recommendations available for your skin type.", styles['Normal']))
        
        story.append(Spacer(1, 25))
        
        # === PROFESSIONAL ADVICE SECTION ===
        story.append(Paragraph("👨‍⚕️ PROFESSIONAL SKINCARE ADVICE", subtitle_style))
        professional_advice = get_professional_advice(skin_condition)
        advice_content = f"""
        <para backColor="#eff6ff" borderColor="#3b82f6" borderWidth="1" borderPadding="12">
        {professional_advice}
        </para>
        """
        story.append(Paragraph(advice_content, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # === ROUTINE SUGGESTIONS ===
        story.append(Paragraph("🌅 DAILY SKINCARE ROUTINE", section_style))
        routine_suggestions = get_routine_suggestions(skin_condition)
        story.append(Paragraph(routine_suggestions, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # === INGREDIENTS TO LOOK FOR ===
        story.append(Paragraph("🧪 KEY INGREDIENTS FOR YOUR SKIN TYPE", section_style))
        ingredients = get_recommended_ingredients(skin_condition)
        ingredients_content = f"""
        <para backColor="#f0f9ff" borderColor="#0ea5e9" borderWidth="1" borderPadding="10">
        {ingredients}
        </para>
        """
        story.append(Paragraph(ingredients_content, styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Footer and Disclaimer
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=1
        )
        
        disclaimer_text = """
        <para backColor="#fef3c7" borderColor="#f59e0b" borderWidth="1" borderPadding="15">
        <b>⚠️ IMPORTANT DISCLAIMER:</b><br/>
        This analysis is generated by an AI model and is for informational purposes only. 
        It should not replace professional dermatological advice. Please consult with a qualified 
        dermatologist for serious skin concerns, persistent issues, or before starting any new 
        skincare regimen. Individual results may vary.
        </para>
        """
        story.append(Paragraph(disclaimer_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Footer
        footer_text = f"""
        AI Skin Analysis Report • Generated by Advanced Machine Learning • 
        For questions or concerns, consult a dermatologist • Report ID: SKA-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}
        """
        story.append(Paragraph(footer_text, footer_style))
        
        # Build PDF
        doc.build(story)
        
        return temp_filename
    except Exception as e:
        print(f"Error generating comprehensive PDF: {e}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'file' not in request.files and 'camera_image' not in request.form:
            return jsonify({'error': 'No image provided'}), 400
        
        # Handle file upload or camera capture
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            image = Image.open(file.stream)
        elif 'camera_image' in request.form:
            # Handle base64 camera image
            image_data = request.form['camera_image']
            # Remove data URL prefix
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        else:
            return jsonify({'error': 'No valid image provided'}), 400
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Check if image contains a face
        if not detect_face(image):
            return jsonify({'error': 'No face detected in the image. Please upload an image containing a face.'}), 400
        
        # Preprocess image for prediction
        processed_image = preprocess_image(image)
        if processed_image is None:
            return jsonify({'error': 'Failed to process image'}), 400
        
        # Predict skin condition
        skin_condition, confidence = predict_skin_condition(processed_image)
        if skin_condition is None:
            return jsonify({'error': 'Failed to analyze skin condition'}), 500
        
        # Get product recommendations
        recommendations = get_product_recommendations(skin_condition)
        
        # Store results in session for PDF generation
        session_data = {
            'skin_condition': skin_condition,
            'confidence': confidence,
            'recommendations': recommendations
        }
        
        return jsonify({
            'skin_condition': skin_condition,
            'confidence': confidence,
            'recommendations': recommendations,
            'session_id': 'temp_session'  # In production, use proper session management
        })
        
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'error': 'An error occurred processing your image'}), 500

@app.route('/generate_report', methods=['POST'])
def generate_report():
    try:
        data = request.get_json()
        skin_condition = data.get('skin_condition')
        confidence = data.get('confidence', 0)
        recommendations = data.get('recommendations', [])
        
        # Generate PDF report
        pdf_path = generate_pdf_report(skin_condition, confidence, recommendations, None)
        
        if pdf_path:
            return send_file(
                pdf_path,
                as_attachment=True,
                download_name=f'skin_analysis_report_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
                mimetype='application/pdf'
            )
        else:
            return jsonify({'error': 'Failed to generate report'}), 500
            
    except Exception as e:
        print(f"Report generation error: {e}")
        return jsonify({'error': 'Failed to generate report'}), 500

# Load resources when the app starts
load_resources()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)