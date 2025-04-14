import os

class Config:
    # Path configurations
    MALE_CSV = os.path.join('data', 'df_male.csv')
    FEMALE_CSV = os.path.join('data', 'female_front.csv')
    MALE_IMAGE_DIR = os.path.join('data', 'male_fashion')
    FEMALE_IMAGE_DIR = os.path.join('data', 'female_fashion')
    MODEL_PATH = 'fashion_model.pth'
    DATABASE_PATH = 'features.db'