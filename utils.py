import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os
import hashlib
import requests
import json
from datetime import datetime
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.fernet import Fernet

def generate_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def generate_qr_code(data: str) -> bytes:
    """Generate QR code and return as bytes"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

def create_certificate(name: str, event_name: str = "SAP Vibeathon 2025") -> bytes:
    """Create a certificate with the given name"""
    # Create a new image with a white background
    width, height = 1200, 800
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a nice font, fall back to default if not available
    try:
        title_font = ImageFont.truetype("arial.ttf", 60)
        name_font = ImageFont.truetype("arial.ttf", 40)
        body_font = ImageFont.truetype("arial.ttf", 30)
    except:
        title_font = ImageFont.load_default()
        name_font = title_font
        body_font = title_font

    # Draw the certificate content
    draw.text((width/2, 150), "Certificate of Participation", 
              font=title_font, fill='black', anchor="mm")
    draw.text((width/2, 300), f"This is to certify that", 
              font=body_font, fill='black', anchor="mm")
    draw.text((width/2, 400), name, 
              font=name_font, fill='black', anchor="mm")
    draw.text((width/2, 500), f"participated in {event_name}", 
              font=body_font, fill='black', anchor="mm")
    draw.text((width/2, 600), datetime.now().strftime("%B %d, %Y"), 
              font=body_font, fill='black', anchor="mm")

    # Convert to bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

def create_certificate_from_template(name: str, template_path: str) -> bytes:
    """Overlay speaker name onto an uploaded certificate template image."""
    try:
        base = Image.open(template_path).convert('RGBA')
        draw = ImageDraw.Draw(base)
        try:
            name_font = ImageFont.truetype("arial.ttf", 48)
        except:
            name_font = ImageFont.load_default()
        w, h = base.size
        draw.text((w/2, h/2), name, font=name_font, fill='black', anchor='mm')
        out = io.BytesIO()
        base.save(out, format='PNG')
        return out.getvalue()
    except Exception as e:
        print(f"Certificate template generation failed: {e}")
        return create_certificate(name)

def save_certificate_template(file_path: str) -> bool:
    # In this simple implementation, we just verify the file exists
    return os.path.exists(file_path)

def load_lottie_url(url: str):
    """Load lottie animation from URL"""
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def get_base64_download_link(img_bytes: bytes, filename: str, text: str) -> str:
    """Create a download link for binary data"""
    b64 = base64.b64encode(img_bytes).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{text}</a>'

# Add AI chatbot response function (simplified version)
def get_chatbot_response(query: str) -> str:
    """Simple chatbot response system"""
    # Basic FAQ responses
    faq = {
        "registration": "To register, please fill out the registration form with your details including name, email, and preferred track.",
        "session": "You can submit a session proposal through the 'Submit Session' section after registering.",
        "certificate": "Certificates will be available for download after the event through your speaker dashboard.",
        "schedule": "The event schedule will be published one week before the event date.",
        "contact": "For urgent queries, please contact the event team at vibeathon@example.com"
    }
    
    # Simple keyword matching
    query = query.lower()
    for key, response in faq.items():
        if key in query:
            return response
            
    return "I'm sorry, I couldn't understand your question. Please try asking about registration, sessions, certificates, schedule, or contact information."

def send_email(to_address: str, subject: str, body: str) -> bool:
    """Send email using SMTP. Reads SMTP config from environment variables.

    Environment variables supported:
      SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM, SMTP_USE_TLS
    """
    import smtplib
    from email.message import EmailMessage

    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = int(os.environ.get('SMTP_PORT', '0')) if os.environ.get('SMTP_PORT') else None
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')
    smtp_from = os.environ.get('SMTP_FROM') or smtp_user
    smtp_use_tls = os.environ.get('SMTP_USE_TLS', 'true').lower() in ('1', 'true', 'yes')

    if not smtp_host or not smtp_port:
        # SMTP not configured
        print("SMTP not configured - email not sent")
        print(f"Would send to {to_address}: {subject}\n{body}")
        return False

    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = smtp_from
        msg['To'] = to_address
        msg.set_content(body)

        if smtp_use_tls:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            server.starttls()
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)

        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)

        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP send failed: {e}")
        return False

def get_setting(db, key: str, default: str = "false") -> str:
    from models import Setting
    s = db.query(Setting).filter(Setting.key == key).first()
    return s.value if s else default

def send_templated_email(db, to_address: str, template_key: str, context: dict, subject: str | None = None) -> bool:
    """Render a template stored in Setting (key=template_xxx) and send it via SMTP."""
    from models import Setting
    t = db.query(Setting).filter(Setting.key == template_key).first()
    body = None
    if t and t.value:
        try:
            body = t.value.format(**context)
        except Exception:
            body = t.value
    else:
        # fallback simple body
        body = context.get('body') or ''

    subj = subject or context.get('subject') or (template_key.replace('template_', '').replace('_', ' ').title())
    return send_email(to_address, subj, body)

def get_fernet_key() -> bytes:
    """Get Fernet key from env or generate one for session (not persisted). For production, set ENCRYPTION_KEY env var."""
    key = os.environ.get('ENCRYPTION_KEY')
    if key:
        return key.encode()
    # generate a key for this process
    return Fernet.generate_key()

def encrypt_string(plain: str) -> str:
    f = Fernet(get_fernet_key())
    token = f.encrypt(plain.encode())
    return token.decode()

def decrypt_string(token_str: str) -> str:
    try:
        f = Fernet(get_fernet_key())
        return f.decrypt(token_str.encode()).decode()
    except Exception:
        return token_str

def audit_log(db, actor: str, action: str, details: str):
    from models import AuditLog
    try:
        entry = AuditLog(actor=actor, action=action, details=details)
        db.add(entry)
        db.commit()
    except Exception:
        db.rollback()

def create_notification(db, user_id: int | None, message: str):
    from models import Notification
    try:
        n = Notification(user_id=user_id, message=message)
        db.add(n)
        db.commit()
    except Exception:
        db.rollback()