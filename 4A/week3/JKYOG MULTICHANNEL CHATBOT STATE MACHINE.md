# JKYOG MULTICHANNEL CHATBOT STATE MACHINE
 
**Ananth Vangala**
 
---
 
## Overview
 
The diagram illustrates the state machine architecture of the JKYog multi-channel chatbot. The flow begins when a user sends a message through a supported channel such as **WhatsApp, web chat, or a voice interface**.
 
The system first **initializes a session** and performs **language detection** to determine the user’s preferred language. Once the language is identified, the chatbot applies **intent detection using NLP and rule-based processing** to understand the user’s request.  
 
The system also maintains **conversation context** by storing session information such as language, detected intent, and conversation state.
 
---
 
## Intent Processing
 
After detecting the intent, the chatbot routes the request to the appropriate workflow. The primary supported intents include:
 
- **Events Information**
- **Donations**
- **Directions to temples or centers**
- **FAQ or Volunteer inquiries**
 
Each intent triggers a **dedicated processing path** where the system retrieves relevant data, such as:
 
- Upcoming events
- Donation links
- Temple locations
- Knowledge base responses
 
If the user wishes to **register for an event or make a donation**, the chatbot generates the required links and confirms the transaction.
 
---
 
## Error Handling and Recovery
 
The system includes several **error recovery mechanisms** to ensure reliability:
 
- If an **API call fails**, the system retries the request before escalating the issue to **human support**.
- If the chatbot **cannot confidently determine the user’s intent**, it asks the user for clarification and reprocesses the input.
- If the user becomes inactive, the system sends a **reminder message** and eventually **closes the session** if no response is received.
 
---
 
## Logging and Analytics
 
Finally, the system logs interaction metadata including:
 
- Detected intent  
- Session duration  
- Communication channel  
- Success or failure status  
 
This data is used for **analytics and continuous system improvement**.
 
Once logging is completed, the **chatbot session is terminated**.
