import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.build_database import process_gender

if __name__ == '__main__':
    try:
        print("Initializing...")
        from backend.model_utils import FashionModel
        from backend.database import FeatureDatabase
        from backend.config import Config
        
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