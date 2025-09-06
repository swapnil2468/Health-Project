import os
from datetime import datetime
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
except ImportError:
    print("ReportLab not available. Using simple text-based PDF generation.")

class PDFGenerator:
    """Service for generating PDF documents"""
    
    def __init__(self):
        self.output_dir = "generated_pdfs"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_intake_form(self, patient_data):
        """Use the professional MediCare intake form"""
        try:
            # Use the professional PDF form provided by the user
            professional_form_paths = [
                "intake_forms/MediCare_Patient_Intake_Form.pdf",
                "attached_assets/New Patient Intake Form_1757083008873.pdf"
            ]
            
            # Find the professional form
            professional_form = None
            for path in professional_form_paths:
                if os.path.exists(path):
                    professional_form = path
                    break
            
            if professional_form:
                print(f"Using professional intake form: {professional_form}")
                return professional_form
            else:
                # Fallback to generating a custom form with their clinic info
                return self._generate_medicare_style_form(patient_data)
                
        except Exception as e:
            print(f"Error with intake form: {e}")
            return self._generate_medicare_style_form(patient_data)
    
    def _generate_medicare_style_form(self, patient_data):
        """Generate intake form matching the MediCare style"""
        try:
            filename = f"MediCare_Intake_Form_{patient_data['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            content = f"""
MediCare Allergy & Wellness Center
456 Healthcare Boulevard, Suite 300 | Phone: (555) 123-4567

New Patient Intake Form
Please complete this form and bring it to your appointment or submit online 24 hours before your visit.

================================================================================
PATIENT INFORMATION (Pre-filled from your booking)

Last Name: {patient_data['name'].split()[-1] if ' ' in patient_data['name'] else patient_data['name']}
First Name: {patient_data['name'].split()[0] if ' ' in patient_data['name'] else patient_data['name']}
Date of Birth: {patient_data['dob']}
Cell Phone: {patient_data.get('phone', '')}
Email Address: {patient_data.get('email', '')}

Appointment Details:
Date: {patient_data['appointment']['date']}
Time: {patient_data['appointment']['time']}
Doctor: {patient_data['doctor']}

Insurance Information:
Insurance Company: {patient_data.get('carrier', '')}
Member ID: {patient_data.get('member_id', '')}
Group Number: {patient_data.get('group_number', '')}

================================================================================
PLEASE COMPLETE THE FOLLOWING SECTIONS:

EMERGENCY CONTACT
Emergency Contact Name: _________________________________
Relationship: _________________________________
Phone Number: _________________________________

CHIEF COMPLAINT & SYMPTOMS
What is the primary reason for your visit today?
____________________________________________________________
____________________________________________________________

How long have you been experiencing these symptoms?
☐ Less than 1 week  ☐ 1-4 weeks  ☐ 1-6 months  ☐ More than 6 months

Please check all symptoms you are currently experiencing:
☐ Sneezing  ☐ Runny nose  ☐ Stuffy nose  ☐ Itchy eyes  ☐ Watery eyes  ☐ Skin rash/hives
☐ Wheezing  ☐ Shortness of breath  ☐ Coughing  ☐ Chest tightness  ☐ Sinus pressure  ☐ Headaches

ALLERGY HISTORY
Do you have any known allergies?
☐ Yes  ☐ No  ☐ Not sure

If yes, please list all known allergies and reactions:
____________________________________________________________
____________________________________________________________

Have you ever had allergy testing before?
☐ Yes - When: ___________  ☐ No

Have you ever used an EpiPen or had a severe allergic reaction?
☐ Yes  ☐ No

CURRENT MEDICATIONS
Please list ALL current medications, vitamins, and supplements:
____________________________________________________________
____________________________________________________________
____________________________________________________________

Are you currently taking any of these allergy medications?
☐ Claritin (loratadine)  ☐ Zyrtec (cetirizine)  ☐ Allegra (fexofenadine)  ☐ Benadryl (diphenhydramine)
☐ Flonase/Nasacort (nasal sprays)  ☐ Other: ________________

MEDICAL HISTORY
Please check any conditions you have or have had:
☐ Asthma  ☐ Eczema  ☐ Sinus infections  ☐ Pneumonia  ☐ Bronchitis  ☐ High blood pressure
☐ Heart disease  ☐ Diabetes  ☐ Other: ________________

Family history of allergies or asthma:
____________________________________________________________
____________________________________________________________

IMPORTANT PRE-VISIT INSTRUCTIONS

CRITICAL: If allergy testing is planned, you MUST stop the following medications 7 days before your appointment:
• All antihistamines (Claritin, Zyrtec, Allegra, Benadryl)
• Cold medications containing antihistamines  
• Sleep aids like Tylenol PM

You MAY continue: Nasal sprays (Flonase, Nasacort), asthma inhalers, and prescription medications

I understand the pre-visit medication instructions:
☐ Yes, I understand and will follow instructions
☐ I have questions about these instructions

PATIENT ACKNOWLEDGMENT
I certify that the information provided is accurate and complete to the best of my knowledge. 
I understand that providing false information may affect my treatment and care.

Patient Signature: _________________________________ Date: __________

================================================================================
For Office Use Only
Date Received: _________ | Staff Initial: _________ | Chart #: _________

MediCare Allergy & Wellness Center | 456 Healthcare Boulevard, Suite 300 | (555) 123-4567
Please submit this form 24 hours before your appointment or arrive 15 minutes early if completing at the office.
"""
            
            # Write as text file since we can't generate actual PDF
            txt_filepath = filepath.replace('.pdf', '.txt')
            with open(txt_filepath, 'w') as f:
                f.write(content)
            
            print(f"MediCare-style intake form generated: {txt_filepath}")
            return txt_filepath
            
        except Exception as e:
            print(f"Error generating MediCare-style intake form: {e}")
            return None
    
    def _generate_intake_form_reportlab(self, patient_data, filepath):
        """Generate intake form using ReportLab"""
        try:
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title = Paragraph("<b>NEW PATIENT INTAKE FORM</b>", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Medical Center Info
            center_info = Paragraph("""
            <b>Medical Center</b><br/>
            123 Healthcare Drive<br/>
            Medical City, MC 12345<br/>
            Phone: (555) 123-4567<br/>
            Fax: (555) 123-4568<br/>
            """, styles['Normal'])
            story.append(center_info)
            story.append(Spacer(1, 20))
            
            # Patient Information (pre-filled from booking)
            patient_info = Paragraph(f"""
            <b>PATIENT INFORMATION</b><br/>
            <b>Name:</b> {patient_data['name']}<br/>
            <b>Date of Birth:</b> {patient_data['dob']}<br/>
            <b>Phone:</b> {patient_data.get('phone', '')}<br/>
            <b>Email:</b> {patient_data.get('email', '')}<br/>
            <b>Appointment Date:</b> {patient_data['appointment']['date']}<br/>
            <b>Appointment Time:</b> {patient_data['appointment']['time']}<br/>
            <b>Doctor:</b> {patient_data['doctor']}<br/>
            """, styles['Normal'])
            story.append(patient_info)
            story.append(Spacer(1, 20))
            
            # Insurance Information (pre-filled)
            insurance_info = Paragraph(f"""
            <b>INSURANCE INFORMATION</b><br/>
            <b>Primary Insurance:</b> {patient_data.get('carrier', '')}<br/>
            <b>Member ID:</b> {patient_data.get('member_id', '')}<br/>
            <b>Group Number:</b> {patient_data.get('group_number', '')}<br/>
            """, styles['Normal'])
            story.append(insurance_info)
            story.append(Spacer(1, 20))
            
            # Medical History Section (to be filled by patient)
            medical_history = Paragraph("""
            <b>MEDICAL HISTORY</b> (Please complete the following sections)<br/><br/>
            
            <b>Current Medications:</b><br/>
            _______________________________________________________________<br/>
            _______________________________________________________________<br/>
            _______________________________________________________________<br/><br/>
            
            <b>Allergies:</b><br/>
            _______________________________________________________________<br/>
            _______________________________________________________________<br/><br/>
            
            <b>Previous Surgeries:</b><br/>
            _______________________________________________________________<br/>
            _______________________________________________________________<br/><br/>
            
            <b>Family Medical History:</b><br/>
            _______________________________________________________________<br/>
            _______________________________________________________________<br/>
            _______________________________________________________________<br/><br/>
            
            <b>Current Symptoms/Reason for Visit:</b><br/>
            _______________________________________________________________<br/>
            _______________________________________________________________<br/>
            _______________________________________________________________<br/><br/>
            
            <b>Emergency Contact:</b><br/>
            Name: ___________________________________ Phone: _______________<br/>
            Relationship: _____________________________<br/><br/>
            
            <b>CONSENT</b><br/>
            I consent to treatment and authorize the release of medical information for insurance purposes.<br/><br/>
            
            Patient Signature: _________________________________ Date: __________<br/>
            """, styles['Normal'])
            story.append(medical_history)
            
            # Build PDF
            doc.build(story)
            
            print(f"Intake form generated: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error with ReportLab PDF generation: {e}")
            return self._generate_intake_form_simple(patient_data, filepath)
    
    def _generate_intake_form_simple(self, patient_data, filepath):
        """Generate simple text-based intake form"""
        try:
            content = f"""
NEW PATIENT INTAKE FORM

Medical Center
123 Healthcare Drive
Medical City, MC 12345
Phone: (555) 123-4567
Fax: (555) 123-4568

================================================================================

PATIENT INFORMATION
Name: {patient_data['name']}
Date of Birth: {patient_data['dob']}
Phone: {patient_data.get('phone', '')}
Email: {patient_data.get('email', '')}
Appointment Date: {patient_data['appointment']['date']}
Appointment Time: {patient_data['appointment']['time']}
Doctor: {patient_data['doctor']}

INSURANCE INFORMATION
Primary Insurance: {patient_data.get('carrier', '')}
Member ID: {patient_data.get('member_id', '')}
Group Number: {patient_data.get('group_number', '')}

================================================================================

MEDICAL HISTORY (Please complete the following sections)

Current Medications:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

Allergies:
_________________________________________________________________
_________________________________________________________________

Previous Surgeries:
_________________________________________________________________
_________________________________________________________________

Family Medical History:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

Current Symptoms/Reason for Visit:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

Emergency Contact:
Name: _________________________________ Phone: _______________
Relationship: _____________________________

================================================================================

CONSENT
I consent to treatment and authorize the release of medical information 
for insurance purposes.

Patient Signature: _______________________________ Date: __________

================================================================================

Please complete this form and bring it to your appointment, or submit it 
online through our patient portal.

Thank you for choosing Medical Center!
"""
            
            # Write to text file (since we can't generate actual PDF without reportlab)
            txt_filepath = filepath.replace('.pdf', '.txt')
            with open(txt_filepath, 'w') as f:
                f.write(content)
            
            print(f"Intake form generated (text format): {txt_filepath}")
            return txt_filepath
            
        except Exception as e:
            print(f"Error generating simple intake form: {e}")
            return None
    
    def generate_appointment_summary(self, patient_data):
        """Generate appointment summary PDF"""
        try:
            filename = f"appointment_summary_{patient_data['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            content = f"""
APPOINTMENT CONFIRMATION SUMMARY

Medical Center
123 Healthcare Drive
Medical City, MC 12345
Phone: (555) 123-4567

================================================================================

APPOINTMENT DETAILS

Patient: {patient_data['name']}
Date of Birth: {patient_data['dob']}
Appointment Date: {patient_data['appointment']['date']}
Appointment Time: {patient_data['appointment']['time']}
Doctor: {patient_data['doctor']}
Duration: {patient_data['appointment']['duration']} minutes
Appointment ID: {patient_data.get('appointment_id', 'N/A')}

Contact Information:
Phone: {patient_data.get('phone', '')}
Email: {patient_data.get('email', '')}

Insurance Information:
Carrier: {patient_data.get('carrier', '')}
Member ID: {patient_data.get('member_id', '')}
Group Number: {patient_data.get('group_number', '')}

================================================================================

IMPORTANT REMINDERS

- Please arrive 15 minutes early for check-in
- Bring a valid photo ID and insurance card
- {"Complete your intake form before the appointment" if not patient_data.get('is_returning') else ""}
- If you need to cancel or reschedule, please call at least 24 hours in advance

Thank you for choosing Medical Center!
"""
            
            txt_filepath = filepath.replace('.pdf', '.txt')
            with open(txt_filepath, 'w') as f:
                f.write(content)
            
            print(f"Appointment summary generated: {txt_filepath}")
            return txt_filepath
            
        except Exception as e:
            print(f"Error generating appointment summary: {e}")
            return None
