import pandas as pd
import os
from datetime import datetime
import re

class PatientManager:
    """Manage patient data and lookups"""
    
    def __init__(self):
        self.patients_file = 'patients.csv'
    
    def lookup_patient(self, name, dob):
        """Look up patient by name and date of birth"""
        try:
            if not os.path.exists(self.patients_file):
                return None
            
            df = pd.read_csv(self.patients_file)
            
            if df.empty:
                return None
            
            # Clean and normalize name for comparison
            name_clean = self.normalize_name(name)
            
            # Look for exact matches first
            for _, patient in df.iterrows():
                patient_name_clean = self.normalize_name(patient['name'])
                patient_dob = patient['DOB']
                
                if (patient_name_clean == name_clean and 
                    self.compare_dates(patient_dob, dob)):
                    return patient.to_dict()
            
            # If no exact match, try partial name matching
            for _, patient in df.iterrows():
                patient_name_clean = self.normalize_name(patient['name'])
                patient_dob = patient['DOB']
                
                if (self.partial_name_match(patient_name_clean, name_clean) and 
                    self.compare_dates(patient_dob, dob)):
                    return patient.to_dict()
            
            return None
            
        except Exception as e:
            print(f"Error looking up patient: {e}")
            return None
    
    def normalize_name(self, name):
        """Normalize name for comparison"""
        if not name:
            return ""
        
        # Remove extra spaces, convert to lowercase
        normalized = re.sub(r'\s+', ' ', str(name).strip().lower())
        
        # Remove common prefixes/suffixes
        prefixes = ['mr', 'mrs', 'ms', 'dr', 'prof']
        suffixes = ['jr', 'sr', 'ii', 'iii', 'iv']
        
        words = normalized.split()
        cleaned_words = []
        
        for word in words:
            word_clean = word.replace('.', '').replace(',', '')
            if word_clean not in prefixes and word_clean not in suffixes:
                cleaned_words.append(word_clean)
        
        return ' '.join(cleaned_words)
    
    def partial_name_match(self, name1, name2):
        """Check if names partially match (for fuzzy matching)"""
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        # Check if at least 2 words match (for first/last name)
        common_words = words1.intersection(words2)
        return len(common_words) >= 2
    
    def compare_dates(self, date1, date2):
        """Compare two dates in various formats"""
        try:
            # Parse dates
            parsed_date1 = self.parse_date(date1)
            parsed_date2 = self.parse_date(date2)
            
            if parsed_date1 and parsed_date2:
                return parsed_date1 == parsed_date2
            
            return False
            
        except Exception as e:
            print(f"Error comparing dates: {e}")
            return False
    
    def parse_date(self, date_str):
        """Parse date string in various formats"""
        if not date_str:
            return None
        
        date_formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%m.%d.%Y',
            '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y',
            '%Y/%m/%d', '%Y-%m-%d', '%Y.%m.%d',
            '%m/%d/%y', '%m-%d-%y', '%m.%d.%y',
            '%d/%m/%y', '%d-%m-%y', '%d.%m.%y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str).strip(), fmt).date()
            except ValueError:
                continue
        
        return None
    
    def get_patient_by_id(self, patient_id):
        """Get patient by patient ID"""
        try:
            if not os.path.exists(self.patients_file):
                return None
            
            df = pd.read_csv(self.patients_file)
            
            patient = df[df['patient_id'] == patient_id]
            
            if not patient.empty:
                return patient.iloc[0].to_dict()
            
            return None
            
        except Exception as e:
            print(f"Error getting patient by ID: {e}")
            return None
    
    def search_patients(self, search_term):
        """Search patients by name, phone, or email"""
        try:
            if not os.path.exists(self.patients_file):
                return []
            
            df = pd.read_csv(self.patients_file)
            
            if df.empty:
                return []
            
            search_term_lower = search_term.lower()
            
            # Search in name, phone, and email
            matches = df[
                df['name'].str.lower().str.contains(search_term_lower, na=False) |
                df['phone'].str.contains(search_term, na=False) |
                df['email'].str.lower().str.contains(search_term_lower, na=False)
            ]
            
            return matches.to_dict('records')
            
        except Exception as e:
            print(f"Error searching patients: {e}")
            return []
    
    def update_patient_visit_history(self, patient_id, visit_date):
        """Update patient's visit history"""
        try:
            if not os.path.exists(self.patients_file):
                return False
            
            df = pd.read_csv(self.patients_file)
            
            # Find patient
            patient_mask = df['patient_id'] == patient_id
            
            if not patient_mask.any():
                return False
            
            # Get current visit history
            current_history = df.loc[patient_mask, 'visit_history'].iloc[0]
            
            # Format visit date
            if isinstance(visit_date, str):
                visit_date_str = visit_date
            else:
                visit_date_str = visit_date.strftime('%m/%d/%Y')
            
            # Update visit history
            if pd.isna(current_history) or current_history == 'New Patient':
                new_history = visit_date_str
            else:
                new_history = f"{current_history}; {visit_date_str}"
            
            df.loc[patient_mask, 'visit_history'] = new_history
            
            # Save updated data
            df.to_csv(self.patients_file, index=False)
            
            print(f"Updated visit history for patient {patient_id}")
            return True
            
        except Exception as e:
            print(f"Error updating patient visit history: {e}")
            return False
    
    def get_patient_stats(self):
        """Get patient statistics"""
        try:
            if not os.path.exists(self.patients_file):
                return {}
            
            df = pd.read_csv(self.patients_file)
            
            if df.empty:
                return {
                    'total_patients': 0,
                    'new_patients': 0,
                    'returning_patients': 0,
                    'by_insurance': {}
                }
            
            # Count new vs returning patients
            new_patients = len(df[df['visit_history'] == 'New Patient'])
            returning_patients = len(df[df['visit_history'] != 'New Patient'])
            
            stats = {
                'total_patients': len(df),
                'new_patients': new_patients,
                'returning_patients': returning_patients,
                'by_insurance': df['insurance_provider'].value_counts().to_dict()
            }
            
            return stats
            
        except Exception as e:
            print(f"Error getting patient stats: {e}")
            return {}
