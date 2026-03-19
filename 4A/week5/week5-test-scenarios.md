# week5-test-scenarios.md

## Overview
30 test scenarios for JKYog WhatsApp Bot:
- 10 Happy Paths  
- 10 Edge Cases  
- 10 Error Scenarios  

Mapped to Team 4B API endpoints.

---

## API Endpoints

| Endpoint            | Method | Purpose                    |
|---------------------|--------|----------------------------|
| /webhook/whatsapp   | POST   | Main conversation handler  |
| /create-payment     | POST   | Stripe payment             |
| /maps               | GET    | Location lookup            |
| /calendar           | GET    | Events                     |
| /health             | GET    | Health check               |

---

# HAPPY PATHS (10)

### 1. Greeting
**Endpoint:** `POST /webhook/whatsapp`  

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "Hi",
  "ProfileName": "User"
}
```

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "Hello! How can I help?"
}
```


---

### 2. Start Donation

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "Donate"
}
```

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "Please choose an amount or enter a custom amount."
}
```


---

### 3. Select Preset Amount

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "25"
}
```

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "Would you like to make this a monthly donation?"
}
```


---

### 4. Confirm Monthly

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "Yes"
}
```

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "Redirecting you to payment..."
}
```


---

### 5. Create Payment

**Endpoint:** `POST /create-payment`

**Request**

```http
POST /create-payment HTTP/1.1
Host: localhost:8000
Content-Length: 0
```

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "client_secret": "pi_12345_secret_ABCDE"
}
```


---

### 6. Get Events

**Endpoint:** `GET /calendar`

**Request**

```http
GET /calendar HTTP/1.1
Host: localhost:8000
```

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "events": [
    {
      "id": "<string>",
      "summary": "<string>",
      "start": "<ISO datetime>",
      "end": "<ISO datetime>"
    }
  ]
}
```


---

### 7. Get Location

**Endpoint:** `GET /maps`

**Request**

```http
GET /maps HTTP/1.1
Host: localhost:8000
```

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "query": "<string>",
  "results": [
    {
      "formatted_address": "<string>",
      "location": {
        "lat": "<float>",
        "lng": "<float>"
      }
    }
  ]
}
```


---

### 8. Continue Flow

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "Yes"
}
```

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "Please confirm your details."
}
```


---

### 9. Returning User

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "Hi again"
}
```

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "Welcome back! How can I help?"
}
```


---

### 10. Health Check

**Endpoint:** `GET /health`

**Request**

```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "ok"
}
```


---

# EDGE CASES (10)

### 11. Empty Input

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": ""
}
```

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "Sorry, I didn’t catch that."
}
```


---

### 12. Invalid Amount

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "-10"
}
```

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "Please enter a valid amount."
}
```


---

### 13. Large Amount

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "1000000"
}
```

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "Please confirm this large amount."
}
```


---

### 14. Non-numeric Input

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "abc"
}
```

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "Invalid input. Enter a number."
}
```


---

### 15. Yes Without Context

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "Yes"
}
```

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "Can you clarify?"
}
```


---

### 16. Session Expired

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "Continue"
}
```

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "Session expired. Start again."
}
```


---

### 17. Duplicate Request

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "Donate"
}
```

*(Assume the user already started a donation flow.)*

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "You're already in a donation flow."
}
```


---

### 18. Unknown Intent

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "asdfgh"
}
```

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "I didn’t understand that."
}
```


---

### 19. Partial Input

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "don"
}
```

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "Did you mean donate?"
}
```


---

### 20. Rapid Messages

**Endpoint:** `POST /webhook/whatsapp`

**Request (conceptual)**

User sends multiple messages quickly, e.g.:

```json
[
  { "From": "whatsapp:+1234567890", "Body": "Donate" },
  { "From": "whatsapp:+1234567890", "Body": "25" },
  { "From": "whatsapp:+1234567890", "Body": "Yes" }
]
```

*(Each item would be a separate POST /webhook/whatsapp call.)*

**Expected Response (for later overlapping message)**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "Processing your previous request..."
}
```


---

# ERROR SCENARIOS (10)

### 21. Authentication Failure

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
X-Twilio-Signature: invalid-signature
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "Hi"
}
```

**Expected Response**

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json
```

```json
{
  "detail": "Unauthorized request"
}
```


---

### 22. Stripe Failure

**Endpoint:** `POST /create-payment`

**Request**

```http
POST /create-payment HTTP/1.1
Host: localhost:8000
Content-Length: 0
```

**Expected Response**

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json
```

```json
{
  "detail": "Payment failed"
}
```


---

### 23. Twilio Send Failure

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "Test send fails"
}
```

*(Assume the outgoing WhatsApp send fails after the bot builds a reply.)*

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "Processing request"
}
```


---

### 24. Database Logging Failure

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "Test DB log failure"
}
```

*(Assume DB logging fails but the bot still replies.)*

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "Message received but not logged"
}
```


---

### 25. Intent Classifier Failure

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "Hi"
}
```

*(Assume the intent classifier crashes internally.)*

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "Let me help you with that."
}
```


---

### 26. Session Update Failure

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "Continue"
}
```

*(Assume updating the session in storage fails.)*

**Expected Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "status": "success",
  "reply": "Request completed successfully"
}
```


---

### 27. Maps API Failure

**Endpoint:** `GET /maps`

**Request**

```http
GET /maps HTTP/1.1
Host: localhost:8000
```

*(Assume the external maps API is down.)*

**Expected Response**

```http
HTTP/1.1 502 Bad Gateway
Content-Type: application/json
```

```json
{
  "detail": "Location unavailable"
}
```


---

### 28. Calendar API Failure

**Endpoint:** `GET /calendar`

**Request**

```http
GET /calendar HTTP/1.1
Host: localhost:8000
```

*(Assume the external calendar API is down.)*

**Expected Response**

```http
HTTP/1.1 502 Bad Gateway
Content-Type: application/json
```

```json
{
  "detail": "Events unavailable"
}
```


---

### 29. Timeout Error

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "Slow response test"
}
```

*(Assume processing takes too long and times out.)*

**Expected Response**

```http
HTTP/1.1 504 Gateway Timeout
Content-Type: application/json
```

```json
{
  "detail": "Request timed out. Try again."
}
```


---

### 30. Internal Server Error

**Endpoint:** `POST /webhook/whatsapp`

**Request**

```http
POST /webhook/whatsapp HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

```json
{
  "From": "whatsapp:+1234567890",
  "Body": "Unexpected failure"
}
```

*(Assume an unexpected internal error occurs.)*

**Expected Response**

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json
```

```json
{
  "detail": "Internal server error"
}
```


---

## Coverage

- Conversation flow
- API integrations
- Error handling
- Multi-turn and edge cases



