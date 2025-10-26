from flask import Flask, request, send_from_directory
from twilio.rest import Client
from threading import Timer
import logging
import os

# ===== Disable terminal spam =====
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# ===== Twilio credentials from Environment Variables =====
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ===== Public URL prefix for ngrok =====
PUBLIC_URL_PREFIX = "https://whatsapp-chat-bot-owhs.onrender.com/images"

# ===== Sample CV images served via Flask =====
SAMPLE_CV_IMAGES = [
    f"{PUBLIC_URL_PREFIX}/cv_1.png",
    f"{PUBLIC_URL_PREFIX}/cv_2.png",
    f"{PUBLIC_URL_PREFIX}/cv_3.png",
    f"{PUBLIC_URL_PREFIX}/cv_4.png",
    f"{PUBLIC_URL_PREFIX}/cv_5.png"
]


# ===== In-memory conversation states =====
user_states = {}

# ===== Serve local images =====
@app.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory("images", filename)

# ===== Function to send CV review after delay =====
def send_review_message(user_number):
    import time
    
    # Step 1: Send review message
    msg = (
        "We have gone through your CV.\n"
        "Your experience is good but your CV format is not ATS compatible and also content in job role is weak.\n"
        "We can work on your CV to make it ATS compatible and professional CV.\n\n"
        "Just sharing a sample of how we can improve your CV"
    )
    client.messages.create(from_=TWILIO_WHATSAPP_NUMBER, to=user_number, body=msg)
    time.sleep(2)  # Wait 2 seconds before sending images
    
    # Step 2: Send sample CV images one by one with delays
    for img_url in SAMPLE_CV_IMAGES:
        client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=user_number,
            media_url=[img_url]
        )
        time.sleep(3)  # Wait 3 seconds between each image
    
    # Step 3: Wait before sending final message (after all images are sent)
    time.sleep(2)
    
    # Step 4: Follow-up message asking if they want the process (sent AFTER all images)
    followup = (
        "We are a paid service. Please let us know if you want to know our process to get your CV prepared"
    )
    client.messages.create(from_=TWILIO_WHATSAPP_NUMBER, to=user_number, body=followup)
    user_states[user_number] = "review_done"

# ===== Webhook =====
@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip().lower()
    sender = request.values.get("From", "")

    # Stage 1: Initial greeting
    if "hi" in incoming_msg and sender not in user_states:
        welcome_msg = (
            "Hi! Thank you for contacting Your Global Resume.\n"
            "We provide ATS-compatible CVs for candidates targeting jobs in the Middle East. "
            "Our CVs are created by recruiters who work in the region.\n"
            "Currently, we offer CVs compatible for the following countries:\n"
            "1. UAE\n"
            "2. Saudi Arabia\n"
            "3. Oman\n"
            "4. Bahrain\n"
            "5. Qatar\n"
            "6. Kuwait\n\n"
            "Candidates who used our CVs have seen up to 3X increase in interview calls or HR responses.\n\n"
            "Could you please share your current CV so we can review it and see how we can make it ATS compatible for the Middle East format?"
        )
        client.messages.create(from_=TWILIO_WHATSAPP_NUMBER, to=sender, body=welcome_msg)
        user_states[sender] = "awaiting_cv"
        return "OK", 200

    # Stage 2: Handle "Sure" response - ask for CV
    if user_states.get(sender) == "awaiting_cv":
        num_media = int(request.values.get("NumMedia", 0))
        
        # Check if CV/document is actually shared
        if num_media > 0:
            client.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER,
                to=sender,
                body="Thank you!\nPlease allow us a few minutes to go through your CV."
            )
            user_states[sender] = "cv_received"
            # Schedule 5-minute review (300 seconds)
            Timer(300, send_review_message, args=[sender]).start()
            return "OK", 200
        else:
            # Customer just said "sure" without sending CV
            client.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER,
                to=sender,
                body="Please send your CV document or PDF so we can review it."
            )
            return "OK", 200

    # Stage 3: User messages before 5 minutes (while CV is being reviewed)
    if user_states.get(sender) == "cv_received":
        client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=sender,
            body="We are going through your CV. Please give us more minutes to review it thoroughly."
        )
        return "OK", 200

    # Stage 4: After review done - handle yes/no
    if user_states.get(sender) == "review_done":
        if "yes" in incoming_msg:
            # Send message asking for call
            client.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER,
                to=sender,
                body="Can we speak over a call to explain our offerings?"
            )
            # Hand off to human (silent - don't inform customer)
            user_states[sender] = "handoff_to_human"
            # Here you can trigger CRM/Slack webhook or notification
            # For now, just log it
            print(f"[HANDOFF] User {sender} wants to proceed - passing to human agent")
        elif "no" in incoming_msg:
            # Customer said no
            client.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER,
                to=sender,
                body="Thank you have a nice day ahead"
            )
            user_states[sender] = "no_response"
            print(f"[NO RESPONSE] User {sender} declined")
        else:
            # Customer ghosted or sent something else
            user_states[sender] = "no_response"
            print(f"[NO RESPONSE] User {sender} did not respond clearly")
        return "OK", 200

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
