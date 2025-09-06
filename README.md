# Medical Appointment Scheduling AI Agent

## Overview

This is a comprehensive medical appointment scheduling system built with Python that uses AI agents to automate the entire patient booking workflow. The system handles patient intake, appointment scheduling, insurance collection, confirmations, and automated reminders through a conversational interface. It features synthetic data generation for testing, multi-channel notifications (email and SMS), and comprehensive appointment management.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit Web Interface**: Form-based UI for patient appointment booking with dropdowns and validation
- **Session State Management**: Maintains patient data and booking state throughout the process
- **Component Caching**: Uses Streamlit's caching system to optimize performance for frequently accessed components
- **Navigation System**: Separate screens for booking appointments and viewing all appointments with filtering

### Agent-Based Architecture
- **Scheduling Agent**: Handles patient information parsing using NLP rules, appointment slot allocation, and doctor availability management
- **Notification Agent**: Manages all communication workflows including email confirmations, SMS reminders, and PDF form distribution
- **Multi-Agent Coordination**: Agents work together to complete the full appointment booking workflow

### Data Management Layer
- **CSV-Based Patient Database**: Uses pandas to manage patient records in `patients.csv` with fields for demographics, insurance, and visit history
- **Excel-Based Scheduling**: Doctor availability and appointment tracking managed through Excel files using openpyxl
- **Synthetic Data Generation**: Faker library creates realistic test data for 50 patients and doctor schedules

### Business Logic Components
- **Patient Manager**: Handles patient lookup, name normalization, and duplicate detection using fuzzy matching
- **Excel Manager**: Manages appointment booking, schedule updates, and admin reporting
- **Smart Scheduling Logic**: Allocates 60-minute slots for new patients and 30-minute slots for returning patients
- **Time Slot Selection**: Interactive dropdown showing available appointment times for selected doctors
- **Indian Phone Format**: Supports +91 - xxxxx xxxxx format for SMS notifications

### Document Generation
- **Professional PDF Forms**: Uses custom MediCare Allergy & Wellness Center intake forms
- **Form Pre-filling**: Automatically fills patient information from booking data
- **Form Distribution**: Automatically sends professional intake forms to new patients via email

### Communication Services
- **Email Service**: Gmail SMTP integration for real email delivery with automatic credential detection
- **SMS Service**: Twilio integration optimized for Indian phone numbers (+91 format)
- **Multi-Channel Notifications**: Coordinated email and SMS campaigns for appointment confirmations and reminders
- **Production Limitations**: Reminder system requires cloud hosting and job scheduling for 24/7 operation

### File Structure Design
- **Modular Architecture**: Separate utility modules for each major function (data generation, patient management, notifications)
- **Agent Pattern**: Dedicated agent classes handle specific workflow responsibilities
- **Configuration Management**: Environment variables control email/SMS credentials and service modes

## External Dependencies

### Core Framework Dependencies
- **Streamlit**: Web interface and session management
- **Pandas**: Data manipulation and CSV operations
- **OpenPyXL**: Excel file operations for schedules and appointments

### AI and NLP Libraries
- **LangGraph + LangChain**: Multi-agent orchestration framework (referenced in requirements but not yet implemented)
- **Faker**: Synthetic data generation for testing

### Communication Services
- **SMTP**: Email delivery service (configurable with Gmail or other providers)
- **Twilio**: SMS messaging service for patient reminders

### Document Processing
- **ReportLab**: PDF generation for intake forms and documents

### Development Tools
- **Python Standard Library**: datetime, os, json, re for core functionality
- **Threading**: Background task execution for reminder systems

### Data Storage
- **CSV Files**: Patient database storage
- **Excel Files**: Doctor schedules and appointment tracking
- **Local File System**: PDF storage and data persistence

### Configuration Requirements
- **Gmail Integration**: EMAIL_ADDRESS and EMAIL_PASSWORD (app password) for real email sending
- **Twilio API**: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER (verified Twilio number required)
- **Phone Format**: Indian format (+91) with automatic formatting and validation
- **Professional Forms**: Custom MediCare intake forms for patient onboarding

## Production Deployment Notes
- **Reminder System**: Requires cloud hosting with always-on capability and job scheduling (Celery, APScheduler)
- **Database**: For production, migrate from CSV/Excel to PostgreSQL or similar database
- **Cloud Hosting**: Deploy on Replit Deployments, Heroku, or AWS for 24/7 operation
- **HIPAA Compliance**: Additional security measures needed for medical data in production
