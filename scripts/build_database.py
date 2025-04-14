import os
import sys
import pandas as pd
from tqdm import tqdm
# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database import FeatureDatabase
from backend.model_utils import FashionModel
from backend.config import Config

def process_gender(df, gender, model, db):
    if gender == "male":
        image_dir = os.path.join(Config.MALE_IMAGE_DIR)
    else:
        image_dir = os.path.join(Config.FEMALE_IMAGE_DIR)
    for _, row in tqdm(df.iterrows(), total=len(df), desc=gender):
        try:
            img_path = os.path.join(image_dir, row['img_name'])
            if not os.path.exists(img_path):
                print(f"Image not found: {img_path}")
                continue
                
            features = model.extract_features(img_path, row['caption'])
            if features is not None:
                db.add_item(row['img_name'], gender, features, row['caption'])
        except Exception as e:
            print(f"Failed on {row['img_name']}: {str(e)}")

if __name__ == '__main__':
    try:
        print("Initializing...")
        model = FashionModel()
        db = FeatureDatabase()
        
        print("Processing male items...")
        male_df = pd.read_csv(Config.MALE_CSV)
        process_gender(male_df, 'male', model, db)
        
        print("Processing female items...")
        female_df = pd.read_csv(Config.FEMALE_CSV)
        process_gender(female_df, 'female', model, db)
        
        print("Database build complete!")
    except Exception as e:
        print(f"Fatal error: {str(e)}")