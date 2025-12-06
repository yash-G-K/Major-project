"""
Model Repair Script for AI Skin Analysis App

This script attempts to fix common model loading issues by:
1. Loading the model with different compatibility modes
2. Rebuilding the model if necessary
3. Creating a simplified fallback model structure
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.applications import MobileNet

def analyze_model_structure():
    """Analyze the current model structure to understand the issue"""
    print("Analyzing model structure...")
    
    model_path = "skin_model_final (1).h5"
    
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        return None
    
    try:
        # Try loading with different methods
        print("Attempting to load model...")
        
        # Method 1: Load without compilation
        print("  - Loading without compilation...")
        model = load_model(model_path, compile=False)
        print("  ✅ Loaded successfully without compilation")
        
        # Print model summary
        print("\nModel Summary:")
        model.summary()
        
        return model
        
    except Exception as e:
        print(f"  ❌ Failed to load: {e}")
        return None

def create_fallback_model():
    """Create a simple fallback model with correct architecture"""
    print("\nCreating fallback model...")
    
    try:
        # Create a simple MobileNet-based model
        base_model = MobileNet(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )
        
        # Freeze base model
        base_model.trainable = False
        
        # Add custom top layers
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dropout(0.2)(x)
        predictions = Dense(7, activation='softmax', name='predictions')(x)  # 7 skin conditions
        
        model = Model(inputs=base_model.input, outputs=predictions)
        
        # Compile the model
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print("✅ Fallback model created successfully")
        print("\nFallback Model Summary:")
        model.summary()
        
        # Save the fallback model
        fallback_path = "fallback_skin_model.h5"
        model.save(fallback_path)
        print(f"✅ Fallback model saved as: {fallback_path}")
        
        return model
        
    except Exception as e:
        print(f"❌ Failed to create fallback model: {e}")
        return None

def test_prediction(model, model_name="model"):
    """Test the model with a dummy prediction"""
    print(f"\nTesting {model_name} prediction...")
    
    try:
        # Create dummy input
        dummy_input = np.random.random((1, 224, 224, 3))
        
        # Make prediction
        prediction = model.predict(dummy_input, verbose=0)
        
        print(f"✅ {model_name} prediction successful!")
        print(f"   Output shape: {prediction.shape}")
        print(f"   Predicted class: {np.argmax(prediction[0])}")
        print(f"   Confidence: {np.max(prediction[0]):.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ {model_name} prediction failed: {e}")
        return False

def main():
    print("🔧 AI Skin Analysis Model Repair Tool")
    print("=" * 50)
    
    # Step 1: Analyze current model
    current_model = analyze_model_structure()
    
    if current_model is not None:
        # Test the current model
        if test_prediction(current_model, "current model"):
            print("\n✅ Current model is working! No repair needed.")
            return
        else:
            print("\n⚠️  Current model loads but can't make predictions.")
    else:
        print("\n❌ Current model cannot be loaded.")
    
    # Step 2: Create fallback model
    fallback_model = create_fallback_model()
    
    if fallback_model is not None:
        test_prediction(fallback_model, "fallback model")
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print("- If current model works: Use skin_model_final (1).h5")
    print("- If current model fails: Use fallback_skin_model.h5")
    print("- Update app.py to use the working model")
    
    # Create instructions file
    with open("model_repair_instructions.txt", "w") as f:
        f.write("Model Repair Instructions\n")
        f.write("========================\n\n")
        f.write("1. If your original model has issues, use the fallback model:\n")
        f.write("   - Rename 'fallback_skin_model.h5' to 'skin_model_working.h5'\n")
        f.write("   - Update app.py to load 'skin_model_working.h5' instead\n\n")
        f.write("2. The fallback model uses MobileNet + custom layers\n")
        f.write("3. You may need to retrain with your specific dataset\n\n")
        f.write("4. For demo purposes, the app can also work without a model\n")
        f.write("   using random predictions from the fallback function\n")
    
    print("📄 Instructions saved to: model_repair_instructions.txt")

if __name__ == "__main__":
    main()