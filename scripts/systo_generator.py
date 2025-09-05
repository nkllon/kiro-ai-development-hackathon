#!/usr/bin/env python3
"""
Systo Generator - Automated Beast Mode Mascot Creation
Generates all Systo variations using OpenAI DALL-E 3 API
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import base64

class SystoGenerator:
    """Automated Systo mascot generation using OpenAI DALL-E 3"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        
        self.base_url = "https://api.openai.com/v1/images/generations"
        self.output_dir = Path("assets/systo")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Systo prompt templates
        self.prompts = {
            "base": {
                "name": "Systo Base",
                "prompt": """Professional mascot illustration of Systo, a friendly wolf-dog hybrid DevOps engineer. 
                Athletic but approachable build (working dog energy, not intimidating). 
                Wearing practical utility vest with small tech tools in pockets. 
                Smart collar displaying simple metrics/status lights. 
                Confident but friendly expression with slight smirk. 
                Collaborative pose (thumbs up or holding a tool). 
                Clean digital illustration style, suitable for branding. 
                White background. Colors: dark gray fur with blue tech accents. 
                Professional but approachable energy."""
            },
            "sre": {
                "name": "SRE Systo", 
                "prompt": """Systo the wolf-dog DevOps mascot wearing a "This is Fine" t-shirt, 
                calmly working on a laptop while small fire icons float around him (representing incidents). 
                Same friendly character design as base Systo - athletic build, confident smirk, 
                dark gray fur with blue accents. Professional illustration style, white background."""
            },
            "platform": {
                "name": "Platform Engineer Systo",
                "prompt": """Systo the wolf-dog DevOps mascot wearing a hard hat with "Infrastructure as Code" text, 
                holding rolled-up blueprints, with small container ship icons (Docker reference) floating nearby. 
                Same character design - athletic build, confident expression, dark gray fur with blue accents. 
                Professional illustration style, white background."""
            },
            "cloud": {
                "name": "Cloud Native Systo",
                "prompt": """Systo the wolf-dog DevOps mascot with Kubernetes wheel patterns on his utility vest, 
                surrounded by small floating cloud symbols, holding a laptop showing deployment pipelines. 
                Same character design - athletic build, friendly smirk, dark gray fur with blue accents. 
                Professional illustration style, white background."""
            },
            "security": {
                "name": "Security DevOps Systo",
                "prompt": """Systo the wolf-dog DevOps mascot wearing a "Zero Trust" bandana, 
                holding a magnifying glass for vulnerability scanning, with shield icons nearby. 
                Same character design - athletic build, confident expression, dark gray fur with blue accents. 
                Professional illustration style, white background."""
            }
        }
    
    def generate_image(self, prompt: str, variant_name: str) -> Optional[str]:
        """Generate single image using DALL-E 3"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "quality": "standard",
            "response_format": "url"
        }
        
        try:
            print(f"Generating {variant_name}...")
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            image_url = result['data'][0]['url']
            
            # Download and save image
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            
            filename = f"systo_{variant_name.lower().replace(' ', '_')}.png"
            filepath = self.output_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(img_response.content)
            
            print(f"✅ Saved: {filepath}")
            return str(filepath)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error generating {variant_name}: {e}")
            return None
    
    def generate_all_variants(self) -> Dict[str, str]:
        """Generate all Systo variations"""
        
        print("🚀 SYSTO GENERATION: SYSTEMATIC SUPERIORITY ENGAGED")
        print(f"Output directory: {self.output_dir.absolute()}")
        print("-" * 50)
        
        results = {}
        
        for variant_key, variant_data in self.prompts.items():
            name = variant_data["name"]
            prompt = variant_data["prompt"]
            
            filepath = self.generate_image(prompt, name)
            if filepath:
                results[variant_key] = filepath
        
        # Save generation metadata
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "variants": results,
            "prompts_used": self.prompts
        }
        
        metadata_file = self.output_dir / "generation_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("-" * 50)
        print(f"✅ Generated {len(results)} Systo variants")
        print(f"📄 Metadata saved: {metadata_file}")
        print("🎯 BEAST MODE: EVERYONE WINS")
        
        return results
    
    def create_asset_structure(self):
        """Create organized asset directory structure"""
        
        dirs = [
            "source",      # Original AI generations
            "processed",   # Refined versions
            "vectors",     # SVG versions (for non-Confluence use)
            "exports",     # Different formats/sizes
            "brand"        # Logo variations
        ]
        
        for dir_name in dirs:
            (self.output_dir / dir_name).mkdir(exist_ok=True)
        
        print(f"📁 Created asset structure in {self.output_dir}")


def main():
    """Main execution function"""
    
    print("🦾 SYSTO GENERATOR - Beast Mode Mascot Creation")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found!")
        print("Set your API key: export OPENAI_API_KEY='your-key-here'")
        return
    
    try:
        generator = SystoGenerator(api_key)
        generator.create_asset_structure()
        results = generator.generate_all_variants()
        
        print("\n🎉 SYSTEMATIC SUPERIORITY ACHIEVED!")
        print("Next steps:")
        print("1. Review generated Systo variants")
        print("2. Refine favorites in Photoshop with Firefly")
        print("3. Create vector versions in Illustrator")
        print("4. Build brand asset library")
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        print("Check your API key and try again.")


if __name__ == "__main__":
    main()