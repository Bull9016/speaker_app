import os
from models import Base, engine, SessionLocal, User, Speaker, Session, Document, QRCode, ChangeRequest
from utils import generate_password_hash

def init_db():
    print("Initializing database...")
    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
    # Ensure uploads directory exists for storing uploaded files
    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    try:
        os.makedirs(uploads_dir, exist_ok=True)
        print(f"Uploads directory ensured at: {uploads_dir}")
    except Exception as e:
        print(f"Warning: Could not create uploads directory: {e}")

    # Create test users if they don't exist
    db = SessionLocal()

    try:
        # Check if speaker user exists
        speaker_user = db.query(User).filter(User.email == "speaker@test.com").first()
        if not speaker_user:
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
            print("Speaker user created.")
        else:
            print("Speaker user already exists.")

        # Check if manager user exists
        manager_user = db.query(User).filter(User.email == "manager@test.com").first()
        if not manager_user:
            # Create event manager user
            manager_user = User(
                email="manager@test.com",
                password_hash=generate_password_hash("test123"),
                role="event_manager",
                is_active=True
            )
            db.add(manager_user)
            print("Manager user created.")
        else:
            print("Manager user already exists.")

        # Commit user changes
        db.commit()

        # Create default settings if they don't exist
        try:
            from models import Setting
            settings_keys = ["agenda_enabled", "documents_enabled", "certificates_published"]
            for key in settings_keys:
                if not db.query(Setting).filter(Setting.key == key).first():
                    db.add(Setting(key=key, value="false"))
            db.commit()
            print("Default settings ensured.")
        except Exception as e:
            db.rollback()
            print(f"Warning: Could not create default settings: {e}")

        # Create default email templates if they don't exist
        try:
            from models import Setting
            templates = [
                ("template_approval", "Hello {name},\n\nYour session '{session}' has been approved.\n\nThanks,\nEvent Team"),
                ("template_rejection", "Hello {name},\n\nWe're sorry to inform you that your session '{session}' was not accepted.\n\nRegards,\nEvent Team"),
                ("template_reminder", "Hello {name},\n\nThis is a reminder to upload your presentation and confirm availability for '{session}'.\n\nThanks,\nEvent Team"),
                ("template_submission", "Hello {name},\n\nThank you for submitting your session '{session}'. We will review it and notify you soon.\n\nRegards,\nEvent Team")
            ]
            for key, value in templates:
                if not db.query(Setting).filter(Setting.key == key).first():
                    db.add(Setting(key=key, value=value))
            db.commit()
            print("Default email templates ensured.")
        except Exception as e:
            db.rollback()
            print(f"Warning: Could not create default email templates: {e}")

        # Add agenda and feedback default flags if they don't exist
        try:
            from models import Setting
            extras = [
                ("agenda_published", "false"),
                ("feedback_enabled", "true"),
                ("certificate_template", "")
            ]
            for key, value in extras:
                if not db.query(Setting).filter(Setting.key == key).first():
                    db.add(Setting(key=key, value=value))
            db.commit()
            print("Extra settings ensured.")
        except Exception as e:
            db.rollback()
            print(f"Warning: Could not create extra settings: {e}")

        print("Database initialization complete!")
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