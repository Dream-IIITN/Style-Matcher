import torch
from PIL import Image
from transformers import ViTModel, ViTImageProcessor
from sentence_transformers import SentenceTransformer
from config import Config
import torch.nn as nn

class SharedFashionModel(nn.Module):
    def __init__(self, shared_dim=768, gender_specific_dim=256):
        super().__init__()
        # Initialize components
        self.shared_image_encoder = ViTModel.from_pretrained('google/vit-base-patch16-224-in21k')
        self.text_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        
        # Projection layers
        self.image_proj = nn.Linear(shared_dim, gender_specific_dim)
        self.text_proj = nn.Linear(384, gender_specific_dim)  # SBERT output dim
        
        # Accessory and style encoders
        self.accessory_encoder = nn.Linear(4, 32)
        self.style_encoder = nn.Linear(2, 32)

    def forward(self, pixel_values, texts, accessories, styles, genders):
        # Image features
        image_features = self.shared_image_encoder(pixel_values=pixel_values).last_hidden_state[:, 0, :]
        image_features = self.image_proj(image_features)
        
        # Text features with batch processing
        text_features = []
        for t in texts:
            if not isinstance(t, str):
                t = str(t)
            text_features.append(torch.tensor(self.text_model.encode(t, show_progress_bar=False)))
        text_features = torch.stack(text_features).to(pixel_values.device)
        text_features = self.text_proj(text_features)
        
        # Accessory and style features
        accessory_features = self.accessory_encoder(accessories)
        style_features = self.style_encoder(styles)
        
        # Combine all features
        combined = torch.cat([
            image_features,
            text_features,
            accessory_features,
            style_features
        ], dim=1)
        
        return combined

class FashionModel:
    def __init__(self, model_path=Config.MODEL_PATH):
        try:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            # Create the model architecture
            self.model = SharedFashionModel()
            # Load the state dictionary
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.to(self.device)
            self.model.eval()
            
            self.image_processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224-in21k')
            self.text_encoder = SentenceTransformer('paraphrase-MiniLM-L6-v2')
            print("Model loaded successfully")
        except Exception as e:
            print(f"Model loading failed: {str(e)}")
            raise

    def extract_features(self, image, text):
        try:
            # Process image
            img = Image.open(image).convert('RGB')
            img_tensor = self.image_processor(img, return_tensors="pt")['pixel_values'].to(self.device)
            
            # Process text
            text_emb = torch.tensor(self.text_encoder.encode(text, show_progress_bar=False)).to(self.device)
            
            # Create dummy tensors for accessories and styles
            batch_size = img_tensor.size(0)
            dummy_accessories = torch.zeros(batch_size, 4).to(self.device)
            dummy_styles = torch.zeros(batch_size, 2).to(self.device)
            dummy_genders = torch.zeros(batch_size).long().to(self.device)
            
            # Get combined features
            with torch.no_grad():
                features = self.model(
                    pixel_values=img_tensor,
                    texts=[text],
                    accessories=dummy_accessories,
                    styles=dummy_styles,
                    genders=dummy_genders
                )
            return features.cpu()
        except Exception as e:
            print(f"Feature extraction failed: {str(e)}")
            return None