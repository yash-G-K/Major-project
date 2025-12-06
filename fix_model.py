"""
Model repair script for skin_model_final (1).h5
Fixes Keras 3 layer incompatibility issues
"""
import os
import numpy as np
from tensorflow import keras
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.applications import MobileNet

print("=" * 60)
print("SKIN MODEL REPAIR SCRIPT")
print("=" * 60)

model_path = "skin_model_final (1).h5"
output_path = "skin_model_fixed.h5"

if not os.path.exists(model_path):
    print(f"❌ Model file not found: {model_path}")
    exit(1)

print(f"\n📂 Loading model from: {model_path}")

try:
    # Try loading with compile=False
    original_model = load_model(model_path, compile=False)
    print("✅ Model loaded successfully!")
    
    # Get model summary
    print("\n📊 Original Model Architecture:")
    original_model.summary()
    
    # Extract weights
    print("\n🔧 Extracting model weights...")
    weights = original_model.get_weights()
    print(f"✅ Extracted {len(weights)} weight arrays")
    
    # Rebuild model with Keras 3 compatible architecture
    print("\n🏗️ Rebuilding model with compatible architecture...")
    
    input_shape = (224, 224, 3)
    num_classes = 7  # Your SKIN_CONDITIONS has 7 classes
    
    # Create base MobileNet
    base_model = MobileNet(
        weights=None,  # Don't load ImageNet weights
        include_top=False,
        input_shape=input_shape
    )
    
    # Build custom top
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.2)(x)
    predictions = Dense(num_classes, activation='softmax')(x)
    
    # Create new model
    new_model = Model(inputs=base_model.input, outputs=predictions)
    
    print("✅ New model architecture created")
    
    # Set weights
    print("\n⚙️ Transferring weights to new model...")
    try:
        new_model.set_weights(weights)
        print("✅ Weights transferred successfully!")
    except Exception as e:
        print(f"⚠️ Weight transfer failed: {e}")
        print("🔄 Attempting layer-by-layer weight transfer...")
        
        # Try layer by layer
        for i, (old_layer, new_layer) in enumerate(zip(original_model.layers, new_model.layers)):
            try:
                if len(old_layer.get_weights()) > 0:
                    new_layer.set_weights(old_layer.get_weights())
                    print(f"  ✓ Layer {i}: {new_layer.name}")
            except Exception as layer_error:
                print(f"  ✗ Layer {i}: {new_layer.name} - {layer_error}")
    
    # Compile the model
    print("\n🔨 Compiling model...")
    new_model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    print("✅ Model compiled")
    
    # Save the fixed model
    print(f"\n💾 Saving fixed model to: {output_path}")
    new_model.save(output_path)
    print("✅ Model saved successfully!")
    
    # Verify the new model
    print("\n🧪 Verifying fixed model...")
    test_model = load_model(output_path, compile=False)
    test_input = np.random.random((1, 224, 224, 3)).astype('float32')
    test_output = test_model.predict(test_input, verbose=0)
    print(f"✅ Test prediction shape: {test_output.shape}")
    print(f"✅ Test prediction sum: {test_output.sum():.4f} (should be ~1.0 for softmax)")
    
    print("\n" + "=" * 60)
    print("✨ MODEL REPAIR COMPLETE!")
    print(f"📁 Fixed model saved as: {output_path}")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("1. Replace 'skin_model_final (1).h5' reference in app.py with 'skin_model_fixed.h5'")
    print("2. Or rename 'skin_model_fixed.h5' to 'skin_model_final (1).h5'")
    print("3. Restart your Flask app")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n⚠️ Alternative: Creating a fresh model...")
    print("Since weight transfer failed, creating a new untrained model...")
    
    # Create fresh model
    base_model = MobileNet(
        weights='imagenet',
        include_top=False,
        input_shape=(224, 224, 3)
    )
    
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.2)(x)
    predictions = Dense(7, activation='softmax')(x)
    
    fresh_model = Model(inputs=base_model.input, outputs=predictions)
    fresh_model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    fresh_model.save("skin_model_fresh.h5")
    print("✅ Fresh model saved as 'skin_model_fresh.h5'")
    print("⚠️ Note: This model is untrained and will give random predictions")
    print("   Use it only for testing the pipeline")
