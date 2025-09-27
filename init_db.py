import os
from models import Base, engine, SessionLocal, User, Speaker, Session, Document, QRCode, ChangeRequest
from utils import generate_password_hash

def init_db():
    # Remove existing database file if it exists
    db_path = os.path.join(os.path.dirname(__file__), "speaker_app.db")
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Removed existing database: {db_path}")
        except Exception as e:
            print(f"Warning: Could not remove existing database: {e}")

    print("Creating new database...")
    # Create all tables
    Base.metadata.create_all(bind=engine)
    # Ensure uploads directory exists for storing uploaded files
    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    try:
        os.makedirs(uploads_dir, exist_ok=True)
        print(f"Uploads directory ensured at: {uploads_dir}")
    except Exception as e:
        print(f"Warning: Could not create uploads directory: {e}")
    
    # Create test users
    db = SessionLocal()
    
    try:
        # Create speaker user
        speaker_user = User(
            email="speaker@test.com",
            password_hash=generate_password_hash("test123"),
            role="speaker",
            is_active=True
        )
        db.add(speaker_user)
        db.flush()  # Get the ID without committing
        
        # Create speaker profile
        speaker = Speaker(
            user_id=speaker_user.id,
            name="Test Speaker",
            mobile="1234567890",
            speaker2_name=None,
            speaker2_email=None,
            speaker2_tshirt=None,
            track="AI/ML",
            tshirt_size="L",
            food_choice="Veg",
            blood_group="O+",
            emergency_contact_name="Emergency Contact",
            emergency_contact_number="9876543210",
            linkedin_url="https://linkedin.com/test",
            sap_community_url="https://community.sap.com/test"
        )
        db.add(speaker)
        
        # Create event manager user
        manager_user = User(
            email="manager@test.com",
            password_hash=generate_password_hash("test123"),
            role="event_manager",
            is_active=True
        )
        db.add(manager_user)
        
        # Commit all changes
        db.commit()
        # Create default settings
        try:
            from models import Setting
            settings = [
                Setting(key="agenda_enabled", value="false"),
                Setting(key="documents_enabled", value="false"),
                Setting(key="certificates_published", value="false")
            ]
            db.add_all(settings)
            db.commit()
            print("Default settings created.")
        except Exception as e:
            db.rollback()
            print(f"Warning: Could not create default settings: {e}")
        # Create default email templates
        try:
            from models import Setting
            templates = [
                Setting(key="template_approval", value="Hello {name},\n\nYour session '{session}' has been approved.\n\nThanks,\nEvent Team"),
                Setting(key="template_rejection", value="Hello {name},\n\nWe're sorry to inform you that your session '{session}' was not accepted.\n\nRegards,\nEvent Team"),
                Setting(key="template_reminder", value="Hello {name},\n\nThis is a reminder to upload your presentation and confirm availability for '{session}'.\n\nThanks,\nEvent Team")
            ]
            # Submission template
            templates.append(Setting(key="template_submission", value="Hello {name},\n\nThank you for submitting your session '{session}'. We will review it and notify you soon.\n\nRegards,\nEvent Team"))
            db.add_all(templates)
            db.commit()
            print("Default email templates created.")
        except Exception as e:
            db.rollback()
            print(f"Warning: Could not create default email templates: {e}")
        # Add agenda and feedback default flags
        try:
            from models import Setting
            extras = [
                Setting(key="agenda_published", value="false"),
                Setting(key="feedback_enabled", value="true"),
                Setting(key="certificate_template", value="")
            ]
            db.add_all(extras)
            db.commit()
            print("Extra settings created.")
        except Exception as e:
            db.rollback()
            print(f"Warning: Could not create extra settings: {e}")
        print("Test users created successfully!")
        print("\nTest Accounts:")
        print("Speaker - Email: speaker@test.com, Password: test123")
        print("Event Manager - Email: manager@test.com, Password: test123")
        
    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("\nDatabase initialized successfully!")