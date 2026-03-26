# test-format-spec.md

## Overview
30 test scenarios for JKYog WhatsApp Bot:
- 10 Happy Paths  
- 10 Edge Cases  
- 10 Error Scenarios  

---

# HAPPY PATHS (10)

### 1. Greeting
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=Hi&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: Hello! How can I help you today?

---

### 2. Start Donation
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=Donate&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: Please choose an amount or enter a custom donation.

---

### 3. Select Amount
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=25&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: Would you like to make this a monthly donation?

---

### 4. Confirm Monthly
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=Yes&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: Great! Redirecting you to payment now.

---

### 5. Create Payment
POST /create-payment  
Content-Type: application/json  
Expected: 200 OK  
Reply: Payment link generated successfully.

---

### 6. Get Events
GET /calendar  
Expected: 200 OK  
Reply: Here are our upcoming events.

---

### 7. Get Location
GET /maps  
Expected: 200 OK  
Reply: Here is the temple location and directions.

---

### 8. Continue Flow
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=Yes&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: Please confirm your details.

---

### 9. Returning User
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=Hi again&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: Welcome back! How can I assist you?

---

### 10. Health Check
GET /health  
Expected: 200 OK  
Reply: Service is running.

---

# EDGE CASES (10)

### 11. Empty Input
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: Sorry, I didn’t catch that. Can you try again?

---

### 12. Invalid Amount
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=-10&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: Please enter a valid donation amount.

---

### 13. Large Amount
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=1000000&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: That is a large amount. Please confirm your donation.

---

### 14. Non-numeric Input
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=abc&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: Invalid input. Please enter a number.

---

### 15. Yes Without Context
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=Yes&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: Could you clarify what you're responding to?

---

### 16. Session Expired
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=Continue&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: Your session has expired. Please start again.

---

### 17. Duplicate Request
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=Donate&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: You are already in a donation flow.

---

### 18. Unknown Intent
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=asdfgh&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: I didn’t understand that. Can you rephrase?

---

### 19. Partial Input
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=don&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: Did you mean “donate”?

---

### 20. Rapid Messages
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=Donate→25→Yes&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: Processing your previous request. Please wait.

---

# ERROR SCENARIOS (10)

### 21. Invalid Signature
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: invalid-signature  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=Hi&ProfileName=<WhatsApp_Profile_Name>  
Expected: 401 Unauthorized  
Reply: Unauthorized request.

---

### 22. Missing Signature
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=Hi&ProfileName=<WhatsApp_Profile_Name>  
Expected: 401 Unauthorized  
Reply: Missing authentication signature.

---

### 23. Stripe Failure
POST /create-payment  
Content-Type: application/json  
Expected: 500 Internal Server Error  
Reply: Payment service is currently unavailable.

---

### 24. Twilio Send Failure
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=Test send fails&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: Message received but delivery failed.

---

### 25. Database Logging Failure
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=Test DB failure&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: Message received but not saved.

---

### 26. Intent Classifier Failure
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=Hi&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: Let me help you with that.

---

### 27. Session Update Failure
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=Continue&ProfileName=<WhatsApp_Profile_Name>  
Expected: 200 OK  
Reply: Request processed, but session not saved.

---

### 28. Maps API Failure
GET /maps  
Expected: 502 Bad Gateway  
Reply: Unable to fetch location at the moment.

---

### 29. Calendar API Failure
GET /calendar  
Expected: 502 Bad Gateway  
Reply: Unable to retrieve events right now.

---

### 30. Timeout / Server Error
POST /webhook/whatsapp  
Content-Type: application/x-www-form-urlencoded  
X-Twilio-Signature: <Twilio_Signature>  
Body:  
MessageSid=<Auto_Generated>&From=<Sender_Number>&Body=Unexpected failure&ProfileName=<WhatsApp_Profile_Name>  
Expected: 500/504 Error  
Reply: Something went wrong. Please try again later.

---

## Coverage

- Conversation flow  
- API integrations  
- Error handling  
- Multi-turn flows  
