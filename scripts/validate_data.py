# scripts/validate_data.py
import pandas as pd
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import Config

def check_gender_data(csv_path, image_dir):
    df = pd.read_csv(csv_path)
    missing = []
    for img in df['img_name']:
        if not os.path.exists(os.path.join(image_dir, img)):
            missing.append(img)
    return missing

if __name__ == '__main__':
    male_missing = check_gender_data(Config.MALE_CSV, Config.MALE_IMAGE_DIR)
    female_missing = check_gender_data(Config.FEMALE_CSV, Config.FEMALE_IMAGE_DIR)
    
    print(f"Male missing: {len(male_missing)}")
    print(f"Female missing: {len(female_missing)}")