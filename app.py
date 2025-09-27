import streamlit as st
import pandas as pd
import datetime
from models import (SessionLocal, Speaker, Session, User, QRCode,
                   Document, ChangeRequest)
from utils import (generate_password_hash, verify_password, generate_qr_code,
                  create_certificate, load_lottie_url, get_base64_download_link,
                  get_chatbot_response)
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import json
import os

# Database initialization - always ensure tables and data
from models import Base, engine
Base.metadata.create_all(bind=engine)  # Create tables if they don't exist

from init_db import init_db
init_db()  # Seed data idempotently

# Page config
st.set_page_config(
    page_title="Speaker Persona App",
    page_icon="🎤",
    layout="wide"
)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_db():
    return SessionLocal()

db = get_db()

def login_user(email: str, password: str):
    """Verify user login"""
    if not email or not password:
        return False
        
    db = get_db()
    user = db.query(User).filter(User.email == email).first()
    
    if user and verify_password(password, user.password_hash):
        # Update last login
        user.last_login = datetime.datetime.now()
        db.commit()
        
        st.session_state.user = {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
        return True
    return False

def register_new_user(email: str, password: str, role: str) -> bool:
    """Register a new user in the database"""
    db = get_db()
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return False
    
    new_user = User(
        email=email,
        password_hash=generate_password_hash(password),
        role=role
    )
    try:
        db.add(new_user)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        st.error(f"Error creating user: {str(e)}")
        return False

def show_registration():
    """Display registration form"""
    st.title("Register New Account")
    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    with st.form("registration_form"):
        st.markdown("---")
        # Account fields
        full_name = st.text_input("Full Name (required)")
        email = st.text_input("Email Address (required)")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        mobile = st.text_input("Mobile Number (required)")
        role = st.selectbox("Role", ["speaker", "event_manager"]) 

        # Speaker-specific fields
        track = st.selectbox("Track", ["AI/ML", "Web Development", "Cloud", "Mobile", "Other"])
        session_category = st.selectbox("Session Category", ["Master Class", "Demo Pod", "Talk", "Workshop", "Other"])
        tshirt_size = st.selectbox("T-shirt Size", ["S", "M", "L", "XL", "XXL"])
        food_choice = st.selectbox("Food Choice", ["Vegetarian", "Non-Vegetarian"]) 
        blood_group = st.text_input("Blood Group")
        emergency_name = st.text_input("Emergency Contact Name")
        emergency_number = st.text_input("Emergency Contact Number")
        linkedin = st.text_input("LinkedIn Profile URL")
        sap = st.text_input("SAP Community URL")

        # Co-speaker fields (optional)
        speaker2_name = st.text_input("Speaker 2 Name (optional)")
        speaker2_email = st.text_input("Speaker 2 Email (optional)")
        speaker2_tshirt = st.selectbox("Speaker 2 T-shirt Size", ["None", "S", "M", "L", "XL", "XXL"]) 

        # File uploads
        st.subheader("Optional: Upload Supporting Files (presentations, promos)")
        uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)

        submit = st.form_submit_button("Register")

        if submit:
            # Basic validations
            if not full_name or not email or not password or not mobile:
                st.error("Full name, email, password and mobile number are required.")
                st.stop()
            if password != confirm_password:
                st.error("Passwords do not match!")
                st.stop()

            # Create user and speaker
            if not register_new_user(email, password, role):
                st.error("Email already registered!")
                st.stop()

            # fetch created user
            user = db.query(User).filter(User.email == email).first()
            if not user:
                st.error("Failed to create user account.")
                st.stop()

            from utils import encrypt_string, audit_log
            new_speaker = Speaker(
                user_id=user.id,
                name=encrypt_string(full_name),
                mobile=encrypt_string(mobile),
                track=track,
                session_category=session_category,
                tshirt_size=tshirt_size,
                speaker2_name=encrypt_string(speaker2_name) if speaker2_name else None,
                speaker2_email=encrypt_string(speaker2_email) if speaker2_email else None,
                speaker2_tshirt=(speaker2_tshirt if speaker2_tshirt != "None" else None),
                food_choice=food_choice,
                blood_group=blood_group,
                emergency_contact_name=encrypt_string(emergency_name) if emergency_name else None,
                emergency_contact_number=encrypt_string(emergency_number) if emergency_number else None,
                linkedin_url=linkedin,
                sap_community_url=sap
            )
            try:
                db.add(new_speaker)
                db.commit()
                audit_log(db, user.email, 'register_speaker', f'Speaker profile created for user_id={user.id}')
            except Exception as e:
                db.rollback()
                st.error(f"Error saving speaker profile: {e}")
                st.stop()

            # Save uploaded files to uploads directory and create Document rows
            if uploaded_files:
                for up in uploaded_files:
                    try:
                        save_path = os.path.join(uploads_dir, up.name)
                        with open(save_path, "wb") as f:
                            f.write(up.getbuffer())

                        doc = Document(
                            speaker_id=new_speaker.id,
                            session_id=None,
                            doc_type="uploaded",
                            file_url=save_path
                        )
                        db.add(doc)
                    except Exception as e:
                        st.warning(f"Failed to save file {up.name}: {e}")
                db.commit()

            st.success("Registration complete. You may now login.")
            st.session_state.show_register = False
            st.rerun()

def show_login():
    """Display login form"""
    st.title("🎤 Speaker Persona App")
    
    # Load animation
    lottie_url = "https://assets5.lottiefiles.com/packages/lf20_V9t630.json"
    animation = load_lottie_url(lottie_url)
    if animation:
        st_lottie(animation, height=300)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.subheader("Welcome Back! 👋")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if login_user(email, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            st.markdown("---")
        if st.button("New User? Register Here"):
            st.session_state.show_register = True
            st.rerun()

def show_speaker_dashboard():
    """Display speaker dashboard"""
    st.title(f"Welcome, {st.session_state.user['email']} 👋")
    
    # Sidebar menu
    with st.sidebar:
        selected = option_menu(
            "Main Menu",
            ["Profile", "Submit Session", "My Sessions", "Agenda", "Documents", "Availability", "Resources", "Chat Support"],
            icons=['person', 'mic', 'list-task', 'calendar-event', 'file-earmark', 'calendar', 'folder', 'chat-dots'],
            menu_icon="cast",
            default_index=0
        )
    
    if selected == "Profile":
        st.header("My Profile")
        speaker = db.query(Speaker).filter(
            Speaker.user_id == st.session_state.user['id']
        ).first()
        
        if speaker:
            # Show existing profile
            from utils import decrypt_string
            st.write(f"Name: {decrypt_string(speaker.name)}")
            st.write(f"Track: {speaker.track}")
            # ... show other fields
            if st.button("Edit Profile"):
                st.session_state.edit_profile = True
        else:
            # Show profile creation form
            with st.form("profile_form"):
                name = st.text_input("Full Name")
                mobile = st.text_input("Mobile Number")
                track = st.selectbox("Track", ["AI/ML", "Web Development", "Cloud", "Mobile", "Other"])
                t_size = st.selectbox("T-Shirt Size", ["S", "M", "L", "XL", "XXL"])
                food = st.selectbox("Food Preference", ["Vegetarian", "Non-Vegetarian"])
                blood = st.text_input("Blood Group")
                emergency_name = st.text_input("Emergency Contact Name")
                emergency_number = st.text_input("Emergency Contact Number")
                linkedin = st.text_input("LinkedIn Profile URL")
                sap = st.text_input("SAP Community URL")
                
                if st.form_submit_button("Save Profile"):
                    from utils import encrypt_string, audit_log
                    new_speaker = Speaker(
                        user_id=st.session_state.user['id'],
                        name=encrypt_string(name),
                        mobile=encrypt_string(mobile),
                        track=track,
                        tshirt_size=t_size,
                        food_choice=food,
                        blood_group=blood,
                        emergency_contact_name=encrypt_string(emergency_name) if emergency_name else None,
                        emergency_contact_number=encrypt_string(emergency_number) if emergency_number else None,
                        linkedin_url=linkedin,
                        sap_community_url=sap
                    )
                    db.add(new_speaker)
                    db.commit()
                    audit_log(db, st.session_state.user['email'], 'create_profile', f'user_id={st.session_state.user['id']}')
                    st.success("Profile saved successfully!")
                    st.rerun()

    elif selected == "Submit Session":
        st.header("Submit a New Session")
        with st.form("session_form"):
            title = st.text_input("Session Title")
            abstract = st.text_area("Session Abstract")
            category = st.selectbox(
                "Session Category",
                ["Talk", "Master Class", "Demo Pod", "Workshop"]
            )
            track = st.selectbox(
                "Session Track",
                ["AI/ML", "Web Development", "Cloud", "Mobile", "Other"]
            )
            co_speaker = st.text_input("Co-Speaker Email (optional)")
            co_speaker_size = st.selectbox(
                "Co-Speaker T-Shirt Size",
                ["None", "S", "M", "L", "XL", "XXL"]
            )
            
            if st.form_submit_button("Submit Session"):
                speaker = db.query(Speaker).filter(
                    Speaker.user_id == st.session_state.user['id']
                ).first()
                
                if speaker:
                    new_session = Session(
                        speaker_id=speaker.id,
                        title=title,
                        abstract=abstract,
                        category=category,
                        track=track,
                        co_speaker_email=co_speaker if co_speaker else None,
                        co_speaker_tshirt=co_speaker_size if co_speaker_size != "None" else None
                    )
                    db.add(new_session)
                    db.commit()
                    st.success("Session submitted successfully!")
                    # Send notification email using templates
                    try:
                        from utils import send_templated_email
                        send_templated_email(db, speaker.user.email, 'template_submission', { 'name': decrypt_string(speaker.name) if hasattr(speaker, 'name') else speaker.name, 'session': title })
                        try:
                            from utils import create_notification
                            create_notification(db, speaker.user.id, f"Session '{title}' submitted and pending review.")
                        except Exception:
                            pass
                        if new_session.co_speaker_email:
                            send_templated_email(db, new_session.co_speaker_email, 'template_submission', { 'name': new_session.co_speaker_email, 'session': title })
                    except Exception:
                        pass
                else:
                    st.error("Please complete your profile first!")

    elif selected == "My Sessions":
        st.header("My Sessions")
        speaker = db.query(Speaker).filter(
            Speaker.user_id == st.session_state.user['id']
        ).first()

        if speaker:
            sessions = db.query(Session).filter(Session.speaker_id == speaker.id).all()
            if sessions:
                for session in sessions:
                    with st.expander(f"{session.title} ({session.status})"):
                        col1, col2 = st.columns([2,1])

                        with col1:
                            st.write(f"Abstract: {session.abstract}")
                            st.write(f"Category: {session.category}")
                            st.write(f"Track: {session.track}")
                            if session.timeslot:
                                st.write(f"Time Slot: {session.timeslot}")
                            if session.location:
                                st.write(f"Location: {session.location}")

                            # Speaker confirmation
                            if session.status == "approved" and not session.speaker_confirmed:
                                if st.button("Confirm Availability", key=f"confirm_{session.id}"):
                                    session.speaker_confirmed = True
                                    db.commit()
                                    st.success("Availability confirmed!")
                                    st.rerun()

                        with col2:
                            # Change request form
                            if session.status != "approved" or (datetime.datetime.now() - session.created_at).days < 7:
                                with st.form(f"change_request_{session.id}"):
                                    st.subheader("Request Change")
                                    change_type = st.selectbox(
                                        "Change Type",
                                        ["Title", "Abstract", "Speaker"],
                                        key=f"change_type_{session.id}"
                                    )
                                    new_value = st.text_area("New Value", key=f"new_value_{session.id}")

                                    if st.form_submit_button("Submit Request"):
                                        change = ChangeRequest(
                                            session_id=session.id,
                                            request_type=change_type.lower(),
                                            old_value=getattr(session, change_type.lower()),
                                            new_value=new_value
                                        )
                                        db.add(change)
                                        db.commit()
                                        st.success("Change request submitted!")
                            else:
                                st.info("Changes disabled (1 week before event)")

                        # Show QR code if session is approved
                        if session.status == "approved":
                            qr = db.query(QRCode).filter(
                                QRCode.speaker_id == speaker.id
                            ).first()

                            if qr:
                                st.image(generate_qr_code(qr.code))
                                st.download_button(
                                    "Download QR Code",
                                    generate_qr_code(qr.code),
                                    file_name=f"qr_code_{session.id}.png",
                                    mime="image/png"
                                )

                        # Show change request history
                        changes = db.query(ChangeRequest).filter(
                            ChangeRequest.session_id == session.id
                        ).all()

                        if changes:
                            st.subheader("Change Request History")
                            for change in changes:
                                st.write(f"Type: {change.request_type}")
                                st.write(f"Status: {change.status}")
                                st.write(f"Requested: {change.created_at.strftime('%Y-%m-%d %H:%M')}")
                                if change.resolved_at:
                                    st.write(f"Resolved: {change.resolved_at.strftime('%Y-%m-%d %H:%M')}")
            else:
                st.info("No sessions submitted yet.")
        else:
            st.error("Please complete your profile first!")

    elif selected == "Agenda":
        st.header("Event Agenda")
        from utils import get_setting
        if get_setting(db, "agenda_published") == "true":
            approved_sessions = db.query(Session).filter(Session.status == "approved", Session.timeslot != None).order_by(Session.timeslot).all()
            if approved_sessions:
                agenda_data = []
                for session in approved_sessions:
                    speaker = db.query(Speaker).filter(Speaker.id == session.speaker_id).first()
                    from utils import decrypt_string
                    speaker_name = decrypt_string(speaker.name) if speaker.name else "Unknown"
                    agenda_data.append({
                        "Time": session.timeslot,
                        "Title": session.title,
                        "Speaker": speaker_name,
                        "Location": session.location or "TBD"
                    })
                df = pd.DataFrame(agenda_data)
                st.dataframe(df)
            else:
                st.info("No agenda available yet.")
        else:
            st.info("Agenda not published yet.")

    elif selected == "Documents":
        st.header("Document Management")
        speaker = db.query(Speaker).filter(
            Speaker.user_id == st.session_state.user['id']
        ).first()
        
        if speaker:
            # Upload new document
            st.subheader("Upload Document")
            with st.form("document_upload"):
                doc_type = st.selectbox(
                    "Document Type",
                    ["Presentation", "Promotional Material", "Other"]
                )
                session_id = st.selectbox(
                    "Related Session",
                    ["None"] + [s.title for s in speaker.sessions],
                    format_func=lambda x: x if x != "None" else "No specific session"
                )
                file_url = st.text_input("Document URL (Google Drive/OneDrive link)")
                
                if st.form_submit_button("Upload"):
                    doc = Document(
                        speaker_id=speaker.id,
                        session_id=None if session_id == "None" else [s.id for s in speaker.sessions if s.title == session_id][0],
                        doc_type=doc_type,
                        file_url=file_url
                    )
                    db.add(doc)
                    db.commit()
                    st.success("Document uploaded successfully!")
            
            # List uploaded documents
            st.subheader("My Documents")
            docs = db.query(Document).filter(Document.speaker_id == speaker.id).all()
            if docs:
                for doc in docs:
                    with st.expander(f"{doc.doc_type} - {doc.upload_date.strftime('%Y-%m-%d')}"):
                        st.write(f"Status: {doc.status}")
                        st.write(f"URL: {doc.file_url}")
                        if doc.session_id:
                            session = db.query(Session).filter(Session.id == doc.session_id).first()
                            st.write(f"Session: {session.title}")
            else:
                st.info("No documents uploaded yet.")
        else:
            st.error("Please complete your profile first!")

    elif selected == "Availability":
        st.header("Manage Availability")
        speaker = db.query(Speaker).filter(
            Speaker.user_id == st.session_state.user['id']
        ).first()
        
        if speaker:
            st.subheader("Set Your Availability")
            current_availability = speaker.availability or {}
            
            # Date selection
            selected_date = st.date_input("Select Date")
            if selected_date:
                date_str = selected_date.strftime("%Y-%m-%d")
                
                # Time slot selection
                time_slots = [
                    "09:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00",
                    "13:00 - 14:00", "14:00 - 15:00", "15:00 - 16:00"
                ]
                
                selected_slots = []
                for slot in time_slots:
                    is_available = st.checkbox(
                        slot,
                        value=date_str in current_availability and slot in current_availability[date_str]
                    )
                    if is_available:
                        selected_slots.append(slot)
                
                if st.button("Save Availability"):
                    if date_str not in current_availability:
                        current_availability[date_str] = []
                    current_availability[date_str] = selected_slots
                    speaker.availability = current_availability
                    db.commit()
                    st.success("Availability updated!")
            
            # Show current availability
            st.subheader("Current Availability")
            if current_availability:
                for date, slots in current_availability.items():
                    if slots:  # Only show dates with available slots
                        with st.expander(date):
                            for slot in slots:
                                st.write(slot)
            else:
                st.info("No availability set yet.")
        else:
            st.error("Please complete your profile first!")

    elif selected == "Resources":
        st.header("Speaker Resources")
        
        # Templates section
        st.subheader("Templates")
        st.download_button(
            "Download Presentation Template",
            data=b"Presentation template content",  # Replace with actual template
            file_name="presentation_template.pptx"
        )
        st.download_button(
            "Download Promotional Material Template",
            data=b"Promotional template content",  # Replace with actual template
            file_name="promotional_template.pptx"
        )
        
        # Speaker guidelines
        st.subheader("Speaker Guidelines")
        st.markdown("""
        ### Important Deadlines
        - Session submission: 2 weeks before event
        - Presentation upload: 1 week before event
        - Availability confirmation: 3 days after selection
        
        ### Presentation Guidelines
        - 16:9 aspect ratio
        - Include introduction and agenda slides
        - Maximum 30 slides for a 45-minute session
        """)
        
        # Certificates section
        st.subheader("Certificates")
        speaker = db.query(Speaker).filter(
            Speaker.user_id == st.session_state.user['id']
        ).first()
        
        if speaker and speaker.is_verified:
            cert_bytes = create_certificate(speaker.name)
            st.download_button(
                "Download Certificate",
                cert_bytes,
                file_name="certificate.png",
                mime="image/png"
            )
        else:
            st.info("Certificates will be available after the event.")

    elif selected == "Chat Support":
        st.header("Chat Support")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("How can I help you?"):
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Get and display assistant response
            response = get_chatbot_response(prompt)
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

def show_event_manager_dashboard():
    """Display event manager dashboard"""
    st.title("Event Manager Dashboard")
    # Management Settings (agenda/documents/certificates)
    st.subheader("Platform Settings")
    try:
        from utils import get_setting
        from models import Setting
        agenda_val = get_setting(db, "agenda_enabled", "false") == "true"
        docs_val = get_setting(db, "documents_enabled", "false") == "true"
        certs_val = get_setting(db, "certificates_published", "false") == "true"

        col1, col2, col3 = st.columns(3)
        with col1:
            new_agenda = st.checkbox("Agenda Enabled", value=agenda_val)
        with col2:
            new_docs = st.checkbox("Documents Enabled", value=docs_val)
        with col3:
            new_certs = st.checkbox("Certificates Published", value=certs_val)

        if st.button("Save Settings"):
            # Update settings in DB
            def set_kv(k, v):
                s = db.query(Setting).filter(Setting.key == k).first()
                if s:
                    s.value = v
                else:
                    db.add(Setting(key=k, value=v))
            set_kv("agenda_enabled", "true" if new_agenda else "false")
            set_kv("documents_enabled", "true" if new_docs else "false")
            set_kv("certificates_published", "true" if new_certs else "false")
            db.commit()
            st.success("Settings saved")
    except Exception:
        st.warning("Settings unavailable (DB not initialized)")
    
    with st.sidebar:
        selected = option_menu(
            "Management",
            ["Session Review", "Agenda Builder", "Speaker Management", "Feedback", "Change Requests", "Communications"],
            icons=['list-check', 'calendar-event', 'people', 'chat-dots', 'exclamation-triangle', 'envelope'],
            menu_icon="gear",
            default_index=0
        )
    
    if selected == "Session Review":
        st.header("Session Review")
        sessions = db.query(Session).filter(Session.status == "pending").all()
        
        if sessions:
            for session in sessions:
                speaker = db.query(Speaker).filter(Speaker.id == session.speaker_id).first()
                with st.expander(f"{session.title} by {speaker.name}"):
                    st.write(f"Abstract: {session.abstract}")
                    st.write(f"Category: {session.category}")
                    st.write(f"Track: {session.track}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Approve", key=f"approve_{session.id}"):
                            session.status = "approved"
                            db.commit()
                            # create QR code entry for speaker check-in and t-shirt
                            try:
                                import uuid
                                code = str(uuid.uuid4())
                                qr = QRCode(speaker_id=speaker.id, code=code, purpose="checkin")
                                db.add(qr)
                                db.commit()
                            except Exception:
                                db.rollback()
                            st.success("Session approved!")
                            # Send notification emails using templates
                            try:
                                from utils import send_templated_email, get_setting, decrypt_string
                                send_templated_email(db, speaker.user.email, 'template_approval', { 'name': decrypt_string(speaker.name), 'session': session.title })
                                if session.co_speaker_email:
                                    send_templated_email(db, session.co_speaker_email, 'template_approval', { 'name': session.co_speaker_email, 'session': session.title })
                                if get_setting(db, "documents_enabled") == "true":
                                    send_templated_email(db, speaker.user.email, 'template_reminder', { 'name': speaker.name, 'session': session.title })
                                try:
                                    from utils import create_notification
                                    create_notification(db, speaker.user.id, f"Your session '{session.title}' was approved.")
                                except Exception:
                                    pass
                            except Exception:
                                pass
                            st.rerun()
                    with col2:
                        if st.button("Reject", key=f"reject_{session.id}"):
                            session.status = "rejected"
                            db.commit()
                            st.success("Session rejected!")
                            st.rerun()
                    with col3:
                        if st.button("Hold", key=f"hold_{session.id}"):
                            session.status = "hold"
                            db.commit()
                            st.success("Session put on hold!")
                            st.rerun()
        else:
            st.info("No pending sessions to review.")

    elif selected == "Agenda Builder":
        st.header("Agenda Builder")
        approved_sessions = db.query(Session).filter(Session.status == "approved").all()
        
        if approved_sessions:
            st.subheader("Assign Time Slots")
            for session in approved_sessions:
                if not session.timeslot:
                    speaker = db.query(Speaker).filter(Speaker.id == session.speaker_id).first()
                    with st.expander(f"{session.title} by {speaker.name}"):
                        timeslot = st.selectbox(
                            "Select Time Slot",
                            ["9:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00",
                             "13:00 - 14:00", "14:00 - 15:00", "15:00 - 16:00"],
                            key=f"slot_{session.id}"
                        )
                        location = st.selectbox(
                            "Select Location",
                            ["Room A", "Room B", "Room C", "Demo Area"],
                            key=f"loc_{session.id}"
                        )
                        if st.button("Assign", key=f"assign_{session.id}"):
                            session.timeslot = timeslot
                            session.location = location
                            db.commit()
                            st.success("Time slot assigned!")
                            st.rerun()
            
            # Show current agenda
            st.subheader("Current Agenda")
            agenda_data = []
            for session in approved_sessions:
                if session.timeslot:
                    speaker = db.query(Speaker).filter(Speaker.id == session.speaker_id).first()
                    agenda_data.append({
                        "Time": session.timeslot,
                        "Title": session.title,
                        "Speaker": speaker.name,
                        "Location": session.location
                    })
            
            if agenda_data:
                df = pd.DataFrame(agenda_data)
                st.dataframe(df.sort_values("Time"))
                
                # Export agenda
                if st.button("Export Agenda"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download Agenda CSV",
                        csv,
                        file_name="agenda.csv",
                        mime="text/csv"
                    )
                # Publish agenda
                if st.button("Publish Agenda"):
                    from utils import get_setting
                    from models import Setting
                    s = db.query(Setting).filter(Setting.key == "agenda_published").first()
                    if s:
                        s.value = "true"
                    else:
                        db.add(Setting(key="agenda_published", value="true"))
                    db.commit()
                    st.success("Agenda published. Speakers can now view the agenda.")
        else:
            st.info("No approved sessions to schedule.")

    elif selected == "Speaker Management":
        st.header("Speaker Management")
        speakers = db.query(Speaker).join(User).all()
        
        if speakers:
            speaker_data = []
            for speaker in speakers:
                session_count = db.query(Session).filter(
                    Session.speaker_id == speaker.id,
                    Session.status == "approved"
                ).count()
                
                speaker_data.append({
                    "Name": speaker.name,
                    "Email": speaker.user.email,  # Access email through the user relationship
                    "Track": speaker.track,
                    "Sessions": session_count,
                    "T-Shirt": speaker.tshirt_size,
                    "Food": speaker.food_choice
                })
            
            df = pd.DataFrame(speaker_data)
            st.dataframe(df)
            
            # Export speaker data
            if st.button("Export Speaker Data"):
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download Speaker Data CSV",
                    csv,
                    file_name="speakers.csv",
                    mime="text/csv"
                )
        else:
            st.info("No registered speakers yet.")

    # Add QR scan / t-shirt distribution management for event manager
    if selected == "Speaker Management":
        st.subheader("QR Scan (T-shirt / Checkin)")
        code_input = st.text_input("Scan/Enter QR Code to mark used (simulate)")
        if st.button("Mark QR as Used"):
            qr = db.query(QRCode).filter(QRCode.code == code_input).first()
            if qr and not qr.is_used:
                qr.is_used = True
                qr.used_at = datetime.datetime.now()
                db.commit()
                st.success("QR marked as used")
            else:
                st.error("QR not found or already used")

    elif selected == "Feedback":
        st.header("Session Feedback")
        from models import Feedback
        sessions = db.query(Session).filter(Session.status == "approved").all()
        if sessions:
            feedback_data = []
            for session in sessions:
                feedbacks = db.query(Feedback).filter(Feedback.session_id == session.id).all()
                if feedbacks:
                    avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks)
                    speaker = db.query(Speaker).filter(Speaker.id == session.speaker_id).first()
                    from utils import decrypt_string
                    speaker_name = decrypt_string(speaker.name) if speaker.name else "Unknown"
                    feedback_data.append({
                        "Session": session.title,
                        "Speaker": speaker_name,
                        "Average Rating": round(avg_rating, 1),
                        "Feedback Count": len(feedbacks)
                    })
                    with st.expander(f"{session.title} - Avg Rating: {round(avg_rating, 1)} ({len(feedbacks)} feedback(s))"):
                        for fb in feedbacks:
                            st.write(f"Rating: {fb.rating}/5")
                            if fb.comments:
                                st.write(f"Comments: {fb.comments}")
                            st.write(f"Submitted: {fb.created_at.strftime('%Y-%m-%d %H:%M')}")
                            st.markdown("---")
            if feedback_data:
                df = pd.DataFrame(feedback_data)
                st.dataframe(df)
                if st.button("Export Feedback CSV"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download Feedback CSV",
                        csv,
                        file_name="feedback.csv",
                        mime="text/csv"
                    )
            else:
                st.info("No feedback submitted yet.")
        else:
            st.info("No approved sessions yet.")

    elif selected == "Change Requests":
        st.header("Change Requests")
        requests = db.query(ChangeRequest).order_by(ChangeRequest.created_at.desc()).all()
        if requests:
            for req in requests:
                session = db.query(Session).filter(Session.id == req.session_id).first()
                speaker = db.query(Speaker).filter(Speaker.id == session.speaker_id).first()
                with st.expander(f"{req.request_type} for {session.title} by {speaker.name} - {req.status}"):
                    st.write(f"Old value: {req.old_value}")
                    st.write(f"New value: {req.new_value}")
                    st.write(f"Requested: {req.created_at}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Approve Request", key=f"appr_req_{req.id}"):
                            req.status = "approved"
                            db.commit()
                            st.success("Request approved")
                            st.rerun()
                    with col2:
                        if st.button("Reject Request", key=f"rej_req_{req.id}"):
                            req.status = "rejected"
                            db.commit()
                            st.success("Request rejected")
                            st.rerun()
        else:
            st.info("No change requests found.")

    elif selected == "Communications":
        st.header("Communications & Templates")
        from models import Setting
        templates = db.query(Setting).filter(Setting.key.like('template_%')).all()
        for t in templates:
            new_val = st.text_area(f"Template: {t.key}", value=t.value, key=t.key)
            if st.button(f"Save {t.key}", key=f"save_{t.key}"):
                t.value = new_val
                db.commit()
                st.success(f"{t.key} saved")

    # Speaker-facing feedback form (speakers can access under their dashboard)
    if st.session_state.user and st.session_state.user.get('role') == 'speaker':
        st.sidebar.markdown("---")
        st.sidebar.header("Feedback")
        if st.sidebar.button("Give Feedback"):
            st.session_state.show_feedback = True
    if st.session_state.get('show_feedback'):
        st.header("Submit Feedback for a Session")
        speaker = db.query(Speaker).filter(Speaker.user_id == st.session_state.user['id']).first()
        if speaker:
            sessions = db.query(Session).filter(Session.speaker_id == speaker.id, Session.status == 'approved').all()
            if sessions:
                sel = st.selectbox("Select Session", [s.title for s in sessions])
                rating = st.slider("Rating", 1, 5, 4)
                comments = st.text_area("Comments")
                if st.button("Submit Feedback"):
                    s_obj = [s for s in sessions if s.title == sel][0]
                    from models import Feedback
                    fb = Feedback(session_id=s_obj.id, rating=rating, comments=comments)
                    db.add(fb)
                    db.commit()
                    st.success("Feedback submitted. Thank you!")
                    st.session_state.show_feedback = False

# Initialize session state
if 'show_register' not in st.session_state:
    st.session_state.show_register = False

# Main app logic
def main():
    if not st.session_state.user:
        if st.session_state.show_register:
            show_registration()
            if st.button("← Back to Login"):
                st.session_state.show_register = False
                st.rerun()
        else:
            show_login()
    else:
        if st.session_state.user['role'] == 'speaker':
            show_speaker_dashboard()
        elif st.session_state.user['role'] == 'event_manager':
            show_event_manager_dashboard()
        
        # Logout button in sidebar
        with st.sidebar:
            if st.button("Logout"):
                st.session_state.user = None
                st.rerun()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Startup Error: {str(e)}")
        import traceback
        st.write(traceback.format_exc())
