WhatsApp CV Bot

Automatically send your CV to anyone who messages your WhatsApp number. 
Built using Flask and Twilio WhatsApp API.

Overview:
This bot replies instantly on WhatsApp and sends multiple CV images stored in the images folder. 
Helpful for sharing your CV with recruiters or contacts quickly and professionally.

Features:
• Auto-reply on WhatsApp
• Sends multiple CV pages
• Secure Twilio integration
• Works locally or via hosting (Ngrok/Any server)

Tech Used:
• Python
• Flask
• Twilio WhatsApp API

Project Structure:
Chat-Bot/
│
├── app.py                 → Main application
├── requirements.txt       → Library dependencies
└── images/                → CV images folder
    ├── cv_1.png
    ├── cv_2.png
    ├── cv_3.png
    ├── cv_4.png
    └── cv_5.png

How To Run:
1. Clone the repository
   git clone https://github.com/aishwaryaachari/Chat-Bot.git
   cd Chat-Bot_repo

2. Install dependencies
   pip install -r requirements.txt

3. Run server
   python app.py

4. Make Webhook public using Ngrok (if required)

Twilio Setup:
• Go to Twilio WhatsApp Sandbox
• Add your public server URL to
  “When a message comes in”
• Send a WhatsApp message to test 

Developer Info:
Created by: Aishwarya Achari  
Focused on automation and professional communication tools.
