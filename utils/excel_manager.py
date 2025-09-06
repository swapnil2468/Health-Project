import pandas as pd
import os
from datetime import datetime, timedelta
import uuid

class ExcelManager:
    """Manage Excel operations for appointments and schedules"""
    
    def __init__(self):
        self.appointments_file = 'appointments.xlsx'
        self.schedule_file = 'doctor_schedule.xlsx'
        self.admin_report_file = 'admin_report.xlsx'
    
    def create_appointments_file(self):
        """Create appointments.xlsx with proper structure"""
        try:
            columns = [
                'Appointment_ID', 'Patient_Name', 'DOB', 'Phone', 'Email',
                'Doctor', 'Date', 'Time', 'Duration_Minutes', 'Status',
                'Insurance_Carrier', 'Member_ID', 'Group_Number',
                'Patient_Type', 'Created_Date', 'Notes'
            ]
            
            df = pd.DataFrame(columns=columns)
            df.to_excel(self.appointments_file, index=False, engine='openpyxl')
            print(f"Created {self.appointments_file}")
            
        except Exception as e:
            print(f"Error creating appointments file: {e}")
    
    def create_admin_report_file(self):
        """Create admin_report.xlsx with proper structure"""
        try:
            columns = [
                'Report_Date', 'Appointment_ID', 'Patient_Name', 'Doctor',
                'Appointment_Date', 'Appointment_Time', 'Patient_Type',
                'Insurance_Carrier', 'Status', 'Notes'
            ]
            
            df = pd.DataFrame(columns=columns)
            df.to_excel(self.admin_report_file, index=False, engine='openpyxl')
            print(f"Created {self.admin_report_file}")
            
        except Exception as e:
            print(f"Error creating admin report file: {e}")
    
    def book_appointment(self, patient_data):
        """Book an appointment and update all relevant files"""
        try:
            # Generate unique appointment ID
            appointment_id = f"APT{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
            
            # Create appointment record
            appointment_record = {
                'Appointment_ID': appointment_id,
                'Patient_Name': patient_data['name'],
                'DOB': patient_data['dob'],
                'Phone': patient_data.get('phone', ''),
                'Email': patient_data.get('email', ''),
                'Doctor': patient_data['doctor'],
                'Date': patient_data['appointment']['date'],
                'Time': patient_data['appointment']['time'],
                'Duration_Minutes': patient_data['appointment']['duration'],
                'Status': 'Confirmed',
                'Insurance_Carrier': patient_data.get('carrier', ''),
                'Member_ID': patient_data.get('member_id', ''),
                'Group_Number': patient_data.get('group_number', ''),
                'Patient_Type': 'Returning' if patient_data.get('is_returning') else 'New',
                'Created_Date': datetime.now().strftime('%m/%d/%Y %H:%M'),
                'Notes': ''
            }
            
            # Add to appointments file
            if os.path.exists(self.appointments_file):
                df = pd.read_excel(self.appointments_file)
            else:
                self.create_appointments_file()
                df = pd.read_excel(self.appointments_file)
            
            df = pd.concat([df, pd.DataFrame([appointment_record])], ignore_index=True)
            df.to_excel(self.appointments_file, index=False, engine='openpyxl')
            
            # Update doctor schedule
            self.update_doctor_schedule(patient_data)
            
            # Add new patient to CSV if needed
            if not patient_data.get('is_returning'):
                from utils.data_generator import DataGenerator
                data_gen = DataGenerator()
                data_gen.update_patient_csv_with_new_patient(patient_data)
            
            print(f"Appointment booked successfully: {appointment_id}")
            return appointment_id
            
        except Exception as e:
            print(f"Error booking appointment: {e}")
            return None
    
    def update_doctor_schedule(self, patient_data):
        """Update doctor schedule to mark slot as booked"""
        try:
            if not os.path.exists(self.schedule_file):
                print("Doctor schedule file not found")
                return False
            
            df = pd.read_excel(self.schedule_file)
            
            # Find the slot to update
            slot_id = patient_data['appointment'].get('slot_id')
            if slot_id:
                # Update by slot ID
                mask = df['Slot_ID'] == slot_id
            else:
                # Update by doctor, date, and time
                appointment_date = pd.to_datetime(patient_data['appointment']['date']).date()
                mask = (
                    (df['Doctor'] == patient_data['doctor']) &
                    (pd.to_datetime(df['Date']).dt.date == appointment_date) &
                    (df['Time'] == patient_data['appointment']['time']) &
                    (df['Available'] == True)
                )
            
            if mask.any():
                df.loc[mask, 'Available'] = False
                df.loc[mask, 'Patient_Name'] = patient_data['name']
                df.loc[mask, 'Notes'] = 'Booked via AI Agent'
                
                df.to_excel(self.schedule_file, index=False, engine='openpyxl')
                print("Doctor schedule updated successfully")
                return True
            else:
                print("Could not find matching slot in schedule")
                return False
                
        except Exception as e:
            print(f"Error updating doctor schedule: {e}")
            return False
    
    def get_available_slots(self, doctor=None, date=None):
        """Get available appointment slots"""
        try:
            if not os.path.exists(self.schedule_file):
                return []
            
            df = pd.read_excel(self.schedule_file)
            
            # Filter by available slots
            available_df = df[df['Available'] == True]
            
            # Filter by doctor if specified
            if doctor:
                available_df = available_df[available_df['Doctor'] == doctor]
            
            # Filter by date if specified
            if date:
                if isinstance(date, str):
                    date = pd.to_datetime(date).date()
                available_df = available_df[pd.to_datetime(available_df['Date']).dt.date == date]
            
            # Convert to list of dictionaries
            slots = []
            for _, row in available_df.iterrows():
                slots.append({
                    'slot_id': row['Slot_ID'],
                    'doctor': row['Doctor'],
                    'date': row['Date'],
                    'time': row['Time'],
                    'duration': row['Duration_Minutes']
                })
            
            return slots
            
        except Exception as e:
            print(f"Error getting available slots: {e}")
            return []
    
    def generate_daily_report(self, report_date=None):
        """Generate daily admin report"""
        try:
            if report_date is None:
                report_date = datetime.now().date()
            
            if not os.path.exists(self.appointments_file):
                print("No appointments file found")
                return False
            
            appointments_df = pd.read_excel(self.appointments_file)
            
            # Filter appointments for the specified date
            if not appointments_df.empty:
                appointments_df['Date_Parsed'] = pd.to_datetime(appointments_df['Date'], errors='coerce')
                daily_appointments = appointments_df[
                    appointments_df['Date_Parsed'].dt.date == report_date
                ]
            else:
                daily_appointments = appointments_df
            
            # Create report records
            report_records = []
            for _, appointment in daily_appointments.iterrows():
                report_record = {
                    'Report_Date': report_date.strftime('%m/%d/%Y'),
                    'Appointment_ID': appointment['Appointment_ID'],
                    'Patient_Name': appointment['Patient_Name'],
                    'Doctor': appointment['Doctor'],
                    'Appointment_Date': appointment['Date'],
                    'Appointment_Time': appointment['Time'],
                    'Patient_Type': appointment['Patient_Type'],
                    'Insurance_Carrier': appointment['Insurance_Carrier'],
                    'Status': appointment['Status'],
                    'Notes': appointment.get('Notes', '')
                }
                report_records.append(report_record)
            
            # Load existing report or create new one
            if os.path.exists(self.admin_report_file):
                report_df = pd.read_excel(self.admin_report_file)
                # Remove existing entries for this date
                report_df = report_df[
                    pd.to_datetime(report_df['Report_Date'], errors='coerce').dt.date != report_date
                ]
            else:
                self.create_admin_report_file()
                report_df = pd.read_excel(self.admin_report_file)
            
            # Add new report records
            if report_records:
                new_records_df = pd.DataFrame(report_records)
                report_df = pd.concat([report_df, new_records_df], ignore_index=True)
            
            # Save updated report
            report_df.to_excel(self.admin_report_file, index=False, engine='openpyxl')
            
            print(f"Daily report generated for {report_date} - {len(report_records)} appointments")
            return True
            
        except Exception as e:
            print(f"Error generating daily report: {e}")
            return False
    
    def get_appointment_stats(self):
        """Get appointment statistics"""
        try:
            if not os.path.exists(self.appointments_file):
                return {}
            
            df = pd.read_excel(self.appointments_file)
            
            if df.empty:
                return {
                    'total_appointments': 0,
                    'new_patients': 0,
                    'returning_patients': 0,
                    'confirmed_appointments': 0,
                    'by_doctor': {},
                    'by_insurance': {}
                }
            
            stats = {
                'total_appointments': len(df),
                'new_patients': len(df[df['Patient_Type'] == 'New']),
                'returning_patients': len(df[df['Patient_Type'] == 'Returning']),
                'confirmed_appointments': len(df[df['Status'] == 'Confirmed']),
                'by_doctor': df['Doctor'].value_counts().to_dict(),
                'by_insurance': df['Insurance_Carrier'].value_counts().to_dict()
            }
            
            return stats
            
        except Exception as e:
            print(f"Error getting appointment stats: {e}")
            return {}
