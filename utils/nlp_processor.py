import spacy
import re
from config import Config

class NLPProcessor:
    def __init__(self):
        self.nlp = spacy.load("fr_core_news_sm")
        self.skill_patterns = [
            r'\b(?:python|java|javascript|c\+\+|sql|html|css)\b',
            r'\b(?:machine\slearning|deep\slearning|nlp)\b',
            r'\b(?:aws|azure|google\scloud)\b'
        ]
    
    def extract_entities(self, text):
        doc = self.nlp(text.lower())  # Convert to lowercase for better matching
        entities = {
            "PERSON": [],
            "ORG": [],
            "DATE": [],
            "LOC": [],
            "SKILLS": [],
            "EXPERIENCE": [],
            "EDUCATION": []
        }
        
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)
        
        # Extract skills using regex patterns
        for pattern in self.skill_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                skill = match.group()
                if skill not in entities["SKILLS"]:
                    entities["SKILLS"].append(skill)
        
        return entities
    
    def extract_experience(self, text):
        experience = []
        # Look for common experience patterns
        patterns = [
            r'(\d+)\s+ans\s+d\'expérience',
            r'(\d+)\s+mois\s+d\'expérience',
            r'(\d+)\s+années\s+d\'expérience'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                experience.append(match.group())
        
        return experience
    
    def extract_education(self, text):
        education = []
        # Look for common education patterns
        patterns = [
            r'(?:licence|master|doctorat|bac\s*\+[\d]+)',
            r'(?:école\s+de\s+commerce|hec|essec|emlyon)',
            r'(?:ingénieur|polytechnique)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                education.append(match.group())
        
        return education
    
    def process_resume(self, text):
        entities = self.extract_entities(text)
        entities["EXPERIENCE"] = self.extract_experience(text)
        entities["EDUCATION"] = self.extract_education(text)
        
        # Clean up and deduplicate
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities