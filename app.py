import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import json

from agents.scheduling_agent import SchedulingAgent
from agents.notification_agent import NotificationAgent
from utils.data_generator import DataGenerator
from utils.patient_manager import PatientManager
from utils.excel_manager import ExcelManager

# Page configuration
st.set_page_config(
    page_title="Medical Appointment Scheduling AI Agent",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {}
if 'data_initialized' not in st.session_state:
    st.session_state.data_initialized = False
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'appointment_booked' not in st.session_state:
    st.session_state.appointment_booked = False

# Initialize components
@st.cache_resource
def initialize_components():
    """Initialize all components and generate synthetic data if needed"""
    data_gen = DataGenerator()
    patient_mgr = PatientManager()
    excel_mgr = ExcelManager()
    scheduling_agent = SchedulingAgent()
    notification_agent = NotificationAgent()
    
    return data_gen, patient_mgr, excel_mgr, scheduling_agent, notification_agent

def ensure_data_files():
    """Ensure all required data files exist"""
    if not st.session_state.data_initialized:
        data_gen, _, excel_mgr, _, _ = initialize_components()
        
        with st.spinner("Initializing system and generating synthetic data..."):
            # Generate patients.csv if it doesn't exist
            if not os.path.exists('patients.csv'):
                st.info("Generating synthetic patient data...")
                data_gen.generate_patients_csv()
            
            # Generate doctor_schedule.xlsx if it doesn't exist
            if not os.path.exists('doctor_schedule.xlsx'):
                st.info("Generating doctor schedule data...")
                data_gen.generate_doctor_schedule()
            
            # Create appointments.xlsx if it doesn't exist
            if not os.path.exists('appointments.xlsx'):
                excel_mgr.create_appointments_file()
            
            # Create admin_report.xlsx if it doesn't exist
            if not os.path.exists('admin_report.xlsx'):
                excel_mgr.create_admin_report_file()
        
        st.session_state.data_initialized = True
        st.success("System initialized successfully!")

def main():
    st.title("🏥 Medical Appointment Scheduling System")
    st.markdown("---")
    
    # Ensure data files are initialized
    ensure_data_files()
    
    # Get components
    data_gen, patient_mgr, excel_mgr, scheduling_agent, notification_agent = initialize_components()
    
    # Sidebar for admin functions
    with st.sidebar:
        st.header("Admin Panel")
        
        if st.button("Generate Admin Report"):
            with st.spinner("Generating admin report..."):
                excel_mgr.generate_daily_report()
                st.success("Admin report generated!")
        
        pass  # Removed View Appointments from sidebar
        
        if st.button("Reset Form"):
            # Clear patient data
            st.session_state.patient_data = {}
            st.session_state.form_submitted = False
            st.session_state.appointment_booked = False
            st.rerun()
    
    # Navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'book_appointment'
    
    # Navigation buttons
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    
    with col_nav1:
        if st.button("📋 Book Appointment", use_container_width=True):
            st.session_state.current_page = 'book_appointment'
    
    with col_nav2:
        if st.button("📅 View Appointments", use_container_width=True):
            st.session_state.current_page = 'view_appointments'
    
    with col_nav3:
        if st.button("🔄 Reset Form", use_container_width=True):
            st.session_state.patient_data = {}
            st.session_state.form_submitted = False
            st.session_state.appointment_booked = False
            st.session_state.current_page = 'book_appointment'
            st.rerun()
    
    st.markdown("---")
    
    # Show appropriate page based on navigation
    if st.session_state.current_page == 'view_appointments':
        display_appointments_page(excel_mgr)
        return
    elif st.session_state.appointment_booked:
        display_appointment_confirmation()
        return
    
    # Main appointment booking form
    st.header("📋 Book Your Appointment")
    
    # Show welcome message
    st.markdown("""
    Welcome to our Medical Appointment Scheduling System! Please fill out the form below 
    to schedule your appointment. All required fields are marked with an asterisk (*).
    """)
    
    with st.form("appointment_form"):
        # Personal Information Section
        st.subheader("📋 Personal Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input(
                "Full Name *",
                placeholder="Enter your full name (e.g., John Smith)",
                help="Please enter your first and last name as it appears on your ID"
            )
            
            phone = st.text_input(
                "Phone Number *",
                placeholder="+91 - 98765 43210",
                help="Enter your phone number in Indian format for SMS confirmations and reminders"
            )
        
        with col2:
            dob = st.date_input(
                "Date of Birth *",
                min_value=datetime(1920, 1, 1),
                max_value=datetime.now(),
                help="Your date of birth helps us locate your medical records"
            )
            
            email = st.text_input(
                "Email Address *",
                placeholder="john.smith@email.com",
                help="Email address for appointment confirmations and forms"
            )
        
        # Appointment Details Section
        st.subheader("👨‍⚕️ Appointment Details")
        
        col3, col4 = st.columns(2)
        
        with col3:
            preferred_doctor = st.selectbox(
                "Preferred Doctor *",
                options=["Select a doctor..."] + data_gen.doctors,
                help="Choose your preferred doctor from our available physicians"
            )
        
        # Time slot selection (will be populated after doctor selection)
        if preferred_doctor and preferred_doctor != "Select a doctor...":
            with st.spinner(f"Loading available slots for {preferred_doctor}..."):
                available_slots = scheduling_agent.get_available_slots(preferred_doctor)
            
            if available_slots:
                time_slot_options = ["Select a time slot..."] + [slot['display'] for slot in available_slots]
                selected_time_slot = st.selectbox(
                    "Available Time Slots *",
                    options=time_slot_options,
                    help="Choose your preferred appointment time from available slots"
                )
            else:
                st.warning(f"No available slots found for {preferred_doctor}. Please try another doctor.")
                selected_time_slot = "Select a time slot..."
        else:
            st.info("Please select a doctor first to see available time slots.")
            selected_time_slot = "Select a time slot..."
        
        with col4:
            appointment_reason = st.text_area(
                "Reason for Visit (Optional)",
                placeholder="Brief description of your symptoms or reason for the appointment",
                max_chars=200,
                help="Optional: Help us prepare for your visit by describing your symptoms or concerns"
            )
        
        # Insurance Information Section
        st.subheader("🏥 Insurance Information")
        
        col5, col6 = st.columns(2)
        
        with col5:
            insurance_provider = st.selectbox(
                "Insurance Provider *",
                options=["Select your insurance..."] + data_gen.insurance_providers,
                help="Select your insurance provider from the list"
            )
            
            member_id = st.text_input(
                "Member ID *",
                placeholder="ABC12345678",
                help="Your insurance member ID (usually found on your insurance card)"
            )
        
        with col6:
            group_number = st.text_input(
                "Group Number",
                placeholder="GRP1234 (if applicable)",
                help="Group number from your insurance card (leave blank if not applicable)"
            )
        
        # Form submission
        st.markdown("---")
        submit_button = st.form_submit_button(
            "📅 Schedule My Appointment",
            type="primary",
            use_container_width=True
        )
        
        # Form validation and processing
        if submit_button:
            # Validate required fields
            errors = []
            
            if not full_name or len(full_name.strip()) < 2:
                errors.append("Please enter your full name")
            
            if not phone:
                errors.append("Please enter your phone number")
            
            if not email or '@' not in email:
                errors.append("Please enter a valid email address")
            
            if preferred_doctor == "Select a doctor...":
                errors.append("Please select a preferred doctor")
            
            if 'selected_time_slot' in locals() and selected_time_slot == "Select a time slot...":
                errors.append("Please select an appointment time slot")
            
            if insurance_provider == "Select your insurance...":
                errors.append("Please select your insurance provider")
            
            if not member_id:
                errors.append("Please enter your insurance member ID")
            
            # Display errors or process form
            if errors:
                st.error("Please correct the following errors:")
                for error in errors:
                    st.error(f"• {error}")
            else:
                # Get selected slot details
                selected_slot = None
                if 'selected_time_slot' in locals() and selected_time_slot != "Select a time slot...":
                    available_slots = scheduling_agent.get_available_slots(preferred_doctor)
                    for slot in available_slots:
                        if slot['display'] == selected_time_slot:
                            selected_slot = slot
                            break
                
                # Process the appointment booking
                process_appointment_form(
                    full_name, dob, phone, email, preferred_doctor,
                    selected_slot, insurance_provider, member_id, group_number,
                    appointment_reason, patient_mgr, excel_mgr, 
                    scheduling_agent, notification_agent
                )
    
    # Show form tips
    with st.expander("💡 Form Tips"):
        st.markdown("""
        **Required fields are marked with ***
        
        **Tips for filling out the form:**
        - **Full Name**: Use your legal name as it appears on your ID
        - **Phone**: Use your primary phone number for text reminders
        - **Email**: Check your email after booking for confirmation and forms
        - **Doctor**: All our doctors are experienced general practitioners
        - **Insurance**: Make sure to have your insurance card handy for accurate information
        - **Member ID**: Usually a combination of letters and numbers on your insurance card
        - **Group Number**: Not all insurance plans have group numbers - leave blank if not applicable
        """)

def display_appointments_page(excel_mgr):
    """Display all appointments page"""
    st.header("📅 All Appointments")
    
    if os.path.exists('appointments.xlsx'):
        appointments_df = pd.read_excel('appointments.xlsx')
        
        if not appointments_df.empty:
            st.success(f"Found {len(appointments_df)} appointments")
            
            # Filter options
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                date_filter = st.date_input(
                    "Filter by Date (Optional)",
                    value=None,
                    help="Leave empty to see all appointments"
                )
            
            with col_filter2:
                status_filter = st.selectbox(
                    "Filter by Status",
                    options=["All", "Confirmed", "Cancelled", "Completed"],
                    help="Filter appointments by their status"
                )
            
            # Apply filters
            filtered_df = appointments_df.copy()
            
            if date_filter:
                filtered_df['Date_Parsed'] = pd.to_datetime(filtered_df['Date'], errors='coerce')
                filtered_df = filtered_df[filtered_df['Date_Parsed'].dt.date == date_filter]
            
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['Status'] == status_filter]
            
            # Display appointments
            if len(filtered_df) > 0:
                st.markdown(f"### Showing {len(filtered_df)} appointments")
                
                # Customize columns for better display
                display_columns = [
                    'Appointment_ID', 'Patient_Name', 'Doctor', 'Date', 'Time',
                    'Duration_Minutes', 'Patient_Type', 'Insurance_Carrier', 'Status'
                ]
                
                # Show only available columns
                available_columns = [col for col in display_columns if col in filtered_df.columns.tolist()]
                
                st.dataframe(
                    filtered_df[available_columns],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Show statistics
                st.markdown("---")
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                
                with col_stat1:
                    st.metric("Total Appointments", len(filtered_df))
                
                with col_stat2:
                    new_patients = len(filtered_df[filtered_df['Patient_Type'] == 'New'])
                    st.metric("New Patients", new_patients)
                
                with col_stat3:
                    confirmed = len(filtered_df[filtered_df['Status'] == 'Confirmed'])
                    st.metric("Confirmed", confirmed)
                
                with col_stat4:
                    today_appointments = 0
                    if 'Date_Parsed' in filtered_df.columns.tolist():
                        today = datetime.now().date()
                        today_appointments = len(filtered_df[pd.to_datetime(filtered_df['Date_Parsed']).dt.date == today])
                    st.metric("Today's Appointments", today_appointments)
            else:
                st.info("No appointments match the selected filters.")
        else:
            st.info("📅 No appointments have been booked yet.")
    else:
        st.warning("⚠️ Appointments file not found. Please make sure the system is properly initialized.")
    
    # Add refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

def process_appointment_form(full_name, dob, phone, email, preferred_doctor, 
                           selected_slot, insurance_provider, member_id, group_number, 
                           appointment_reason, patient_mgr, excel_mgr, 
                           scheduling_agent, notification_agent):
    """Process the appointment form submission"""
    
    with st.spinner("Processing your appointment request..."):
        try:
            # Prepare patient data
            dob_str = dob.strftime('%m/%d/%Y')
            
            # Look up patient to determine if returning
            patient_record = patient_mgr.lookup_patient(full_name, dob_str)
            is_returning = patient_record is not None
            
            # Prepare patient data dictionary
            st.session_state.patient_data = {
                'name': full_name.strip(),
                'dob': dob_str,
                'phone': phone.strip(),
                'email': email.strip().lower(),
                'doctor': preferred_doctor,
                'carrier': insurance_provider,
                'member_id': member_id.strip(),
                'group_number': group_number.strip() if group_number else '',
                'is_returning': is_returning,
                'appointment_reason': appointment_reason.strip() if appointment_reason else ''
            }
            
            if is_returning:
                st.session_state.patient_data['patient_record'] = patient_record
            
            # Use selected time slot
            duration = 30 if is_returning else 60
            
            if selected_slot:
                appointment_slot = {
                    'date': selected_slot['date'],
                    'time': selected_slot['time'], 
                    'duration': duration,
                    'slot_id': selected_slot['slot_id']
                }
                st.session_state.patient_data['appointment'] = appointment_slot
                
                # Book the appointment
                appointment_id = excel_mgr.book_appointment(st.session_state.patient_data)
                st.session_state.patient_data['appointment_id'] = appointment_id
                
                if appointment_id:
                    # Send confirmations
                    email_sent = notification_agent.send_email_confirmation(st.session_state.patient_data)
                    sms_sent = notification_agent.send_sms_confirmation(st.session_state.patient_data)
                    
                    # Schedule reminders
                    notification_agent.schedule_reminders(st.session_state.patient_data)
                    
                    # Mark as successfully booked
                    st.session_state.appointment_booked = True
                    st.session_state.form_submitted = True
                    
                    st.success("✅ Appointment successfully booked!")
                    st.rerun()
                else:
                    st.error("❌ Error booking appointment. Please try again.")
            else:
                st.error(f"❌ No available slots found for {preferred_doctor}. Please try selecting a different doctor or contact us at (555) 123-4567.")
                
        except Exception as e:
            st.error(f"❌ An error occurred while booking your appointment: {str(e)}")
            print(f"Error in process_appointment_form: {e}")

def display_appointment_confirmation():
    """Display the appointment confirmation page"""
    
    st.success("🎉 Your appointment has been successfully booked!")
    
    # Main confirmation details
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📅 Appointment Details")
        
        appointment_data = st.session_state.patient_data
        
        st.info(f"""
        **Patient:** {appointment_data['name']}  
        **Date:** {appointment_data['appointment']['date']}  
        **Time:** {appointment_data['appointment']['time']}  
        **Doctor:** {appointment_data['doctor']}  
        **Duration:** {appointment_data['appointment']['duration']} minutes  
        **Appointment ID:** {appointment_data.get('appointment_id', 'N/A')}  
        **Patient Type:** {'Returning Patient' if appointment_data.get('is_returning') else 'New Patient'}
        """)
        
        st.markdown("### 📧 Confirmations Sent")
        st.success(f"✅ Email confirmation sent to: {appointment_data.get('email', 'N/A')}")
        st.success(f"✅ SMS confirmation sent to: {appointment_data.get('phone', 'N/A')}")
        
        if not appointment_data.get('is_returning'):
            st.info("📋 As a new patient, you'll receive a New Patient Intake Form via email. Please fill it out before your appointment.")
    
    with col2:
        st.markdown("### 🏥 Location")
        st.markdown("""
        **Medical Center**  
        123 Healthcare Drive  
        Medical City, MC 12345  
        📞 (555) 123-4567
        """)
        
        st.markdown("### ⏰ Reminders")
        st.markdown("""
        **Automated reminders will be sent:**  
        • 24 hours before  
        • 2 hours before  
        • 30 minutes before
        """)
    
    # Important notes
    st.markdown("---")
    st.markdown("### ⚠️ Important Notes")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        **Before Your Appointment:**
        • Arrive 15 minutes early for check-in
        • Bring a valid photo ID
        • Bring your insurance card
        • Complete intake form (new patients)
        """)
    
    with col4:
        st.markdown("""
        **Need to Make Changes?**
        • Call us at (555) 123-4567
        • Cancel/reschedule at least 24 hours in advance
        • Email us at appointments@medicalcenter.com
        """)
    
    # Action buttons
    st.markdown("---")
    col5, col6, col7 = st.columns(3)
    
    with col5:
        if st.button("📄 Download Confirmation", use_container_width=True):
            # Generate and offer download of appointment summary
            from utils.pdf_generator import PDFGenerator
            pdf_gen = PDFGenerator()
            pdf_path = pdf_gen.generate_appointment_summary(st.session_state.patient_data)
            if pdf_path:
                st.success("Confirmation generated! Check the generated_pdfs folder.")
    
    with col6:
        if st.button("📅 Add to Calendar", use_container_width=True):
            # Generate calendar event details
            appointment = st.session_state.patient_data['appointment']
            calendar_text = f"""
            Subject: Medical Appointment - {st.session_state.patient_data['doctor']}
            Location: Medical Center, 123 Healthcare Drive, Medical City, MC 12345
            Date: {appointment['date']}
            Time: {appointment['time']}
            Duration: {appointment['duration']} minutes
            """
            st.text_area("Calendar Event Details (copy and paste into your calendar):", calendar_text, height=150)
    
    with col7:
        if st.button("🔄 Book Another Appointment", use_container_width=True):
            # Reset form for new appointment
            st.session_state.patient_data = {}
            st.session_state.form_submitted = False
            st.session_state.appointment_booked = False
            st.rerun()

if __name__ == "__main__":
    main()
