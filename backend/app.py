from flask import Flask, request, jsonify 
from model_utils import FashionModel
from database import FeatureDatabase
from config import Config
import traceback
import os

app = Flask(__name__)
model = FashionModel()
# Create a single instance of FeatureDatabase
db = FeatureDatabase()

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
            
        gender = request.form.get('gender')
        if gender not in ['male', 'female']:
            return jsonify({"error": "Invalid gender"}), 400
            
        text_query = request.form.get('query', '')
        image = request.files['image']
        
        # Extract features
        features = model.extract_features(image, text_query)
        if features is None:
            return jsonify({"error": "Feature extraction failed"}), 500
            
        # Get recommendations
        results = db.get_similar(features, gender)
        
        if not results:
            return jsonify({"error": "No similar items found"}), 404
            
        # Format results
        formatted_results = []
        for img_name, caption in results:
            image_path = os.path.join(
                Config.MALE_IMAGE_DIR if gender == 'male' else Config.FEMALE_IMAGE_DIR,
                img_name
            )
            if os.path.exists(image_path):
                formatted_results.append({
                    "image": image_path,
                    "caption": caption
                })
            else:
                print(f"Warning: Image not found: {image_path}")
        
        if not formatted_results:
            return jsonify({"error": "No valid images found"}), 404
            
        return jsonify(formatted_results)
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)