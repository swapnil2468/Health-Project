import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker
import os

class DataGenerator:
    """Generate synthetic data for patients and doctor schedules"""
    
    def __init__(self):
        self.fake = Faker()
        self.doctors = ["Dr. Smith", "Dr. Johnson", "Dr. Williams"]
        self.insurance_providers = [
            "Blue Cross Blue Shield", "Aetna", "Cigna", "Humana", 
            "United Healthcare", "Kaiser Permanente", "Medicare", "Medicaid"
        ]
    
    def generate_patients_csv(self, num_patients=50):
        """Generate synthetic patient data and save to CSV"""
        patients = []
        
        for i in range(num_patients):
            # Generate visit history
            num_visits = random.randint(0, 10)
            visit_dates = []
            for _ in range(num_visits):
                visit_date = self.fake.date_between(start_date='-2y', end_date='today')
                visit_dates.append(visit_date.strftime('%m/%d/%Y'))
            
            visit_history = '; '.join(visit_dates) if visit_dates else 'New Patient'
            
            patient = {
                'patient_id': f"PAT{1000 + i}",
                'name': self.fake.name(),
                'DOB': self.fake.date_of_birth(minimum_age=18, maximum_age=85).strftime('%m/%d/%Y'),
                'phone': self.fake.phone_number(),
                'email': self.fake.email(),
                'insurance_provider': random.choice(self.insurance_providers),
                'member_id': self.generate_member_id(),
                'group_number': self.generate_group_number(),
                'visit_history': visit_history
            }
            
            patients.append(patient)
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(patients)
        df.to_csv('patients.csv', index=False)
        print(f"Generated {num_patients} synthetic patients in patients.csv")
        
        return df
    
    def generate_member_id(self):
        """Generate realistic member ID"""
        prefixes = ['ABC', 'DEF', 'GHI', 'JKL', 'MNO', 'PQR', 'STU', 'VWX', 'YZ1', 'BC2']
        prefix = random.choice(prefixes)
        numbers = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return f"{prefix}{numbers}"
    
    def generate_group_number(self):
        """Generate realistic group number"""
        if random.random() < 0.2:  # 20% chance of no group number
            return 'N/A'
        
        formats = [
            lambda: f"{random.randint(100000, 999999)}",
            lambda: f"GRP{random.randint(1000, 9999)}",
            lambda: f"{random.choice(['A', 'B', 'C'])}{random.randint(10000, 99999)}",
        ]
        
        return random.choice(formats)()
    
    def generate_doctor_schedule(self):
        """Generate doctor schedule for 5 working days"""
        schedule_data = []
        
        # Generate for next 5 working days
        start_date = datetime.now().date()
        working_days = []
        
        current_date = start_date
        while len(working_days) < 5:
            if current_date.weekday() < 5:  # Monday to Friday
                working_days.append(current_date)
            current_date += timedelta(days=1)
        
        slot_id = 1000
        
        for doctor in self.doctors:
            for date in working_days:
                # Each doctor works 9 AM to 5 PM with 30-minute slots
                for hour in range(9, 17):
                    for minute in [0, 30]:
                        time_str = f"{hour:02d}:{minute:02d}"
                        
                        # Randomly make some slots unavailable (booked)
                        is_available = random.random() > 0.3  # 70% availability
                        
                        schedule_entry = {
                            'Slot_ID': f"SLOT_{slot_id}",
                            'Doctor': doctor,
                            'Date': date,
                            'Time': time_str,
                            'Available': is_available,
                            'Duration_Minutes': 30,
                            'Patient_Name': '' if is_available else self.fake.name(),
                            'Notes': '' if is_available else 'Booked'
                        }
                        
                        schedule_data.append(schedule_entry)
                        slot_id += 1
        
        # Create DataFrame and save to Excel
        df = pd.DataFrame(schedule_data)
        df.to_excel('doctor_schedule.xlsx', index=False, engine='openpyxl')
        print(f"Generated doctor schedule in doctor_schedule.xlsx")
        
        return df
    
    def update_patient_csv_with_new_patient(self, patient_data):
        """Add new patient to the CSV file"""
        try:
            # Load existing patients
            if os.path.exists('patients.csv'):
                df = pd.read_csv('patients.csv')
            else:
                df = pd.DataFrame()
            
            # Generate new patient ID
            if len(df) > 0:
                last_id = int(df['patient_id'].str.replace('PAT', '').max())
                new_id = f"PAT{last_id + 1}"
            else:
                new_id = "PAT1000"
            
            # Create new patient record
            new_patient = {
                'patient_id': new_id,
                'name': patient_data['name'],
                'DOB': patient_data['dob'],
                'phone': patient_data.get('phone', ''),
                'email': patient_data.get('email', ''),
                'insurance_provider': patient_data.get('carrier', ''),
                'member_id': patient_data.get('member_id', ''),
                'group_number': patient_data.get('group_number', ''),
                'visit_history': 'New Patient'
            }
            
            # Add new patient and save
            df = pd.concat([df, pd.DataFrame([new_patient])], ignore_index=True)
            df.to_csv('patients.csv', index=False)
            
            return new_id
            
        except Exception as e:
            print(f"Error updating patient CSV: {e}")
            return None
