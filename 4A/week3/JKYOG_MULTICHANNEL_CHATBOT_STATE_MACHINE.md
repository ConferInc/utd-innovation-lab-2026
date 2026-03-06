# JKYog Multichannel Chatbot State Machine
**Author:** Ananth Vangala
 
---
 
# Overview
 
The JKYog Multichannel Chatbot State Machine represents the workflow of a chatbot designed to support multiple communication channels such as WhatsApp, Website Chat, and Voice Bot interfaces. The system manages user conversations by detecting language, identifying user intent, routing requests to appropriate workflows, and handling errors gracefully.
 
The purpose of this state machine is to ensure that the chatbot can process user requests efficiently while maintaining context across conversation turns and providing appropriate recovery mechanisms when errors occur.
 
---
 
# Conversation Initialization
 
The chatbot interaction begins when a user sends a message through one of the supported communication channels.
 
**Entry Channels**
- WhatsApp
- Website Chat
- Voice Bot
 
Once a message is received, the system initializes a new session. During this process, the chatbot loads important session attributes including:
 
- `session_id`
- `user_id`
- user language preference
- previous conversation state
 
This session initialization allows the chatbot to maintain continuity and ensures that returning users can resume previous interactions.
 
---
 
# Language Detection
 
After session initialization, the chatbot performs language detection to determine the user's preferred language.
 
Supported languages include:
 
- English
- Hindi
- Gujarati
 
If the system cannot automatically detect the language, the chatbot prompts the user to manually select their preferred language before continuing the conversation. This step ensures that responses are delivered in the correct language and improves the accessibility of the chatbot for multilingual users.
 
---
 
# Intent Detection
 
Once the language has been determined, the chatbot analyzes the user's message using Natural Language Processing (NLP). The NLP engine evaluates the message and attempts to classify the user's intent.
 
Examples of intents include:
 
- Event information
- Donations
- Temple directions
- Volunteer inquiries
- Frequently asked questions
 
If the chatbot cannot confidently identify the user’s intent, a fallback menu is displayed. This menu allows users to select one of the available options:
 
- Events
- Donations
- Temple Directions
- Volunteer / FAQ
- Human Support
 
This fallback mechanism helps guide users toward valid requests and prevents conversation dead ends.
 
---
 
# Context Maintenance
 
Once the user’s intent has been identified, the chatbot updates and stores the conversation context. Context persistence ensures that the chatbot remembers the current conversation state and maintains continuity throughout the interaction.
 
The system stores key information such as:
 
- detected intent
- current workflow step
- session metadata
- user preferences
 
By maintaining this context, the chatbot can provide consistent responses even across multiple message exchanges.
 
---
 
# Intent Routing and Workflow Execution
 
After identifying the intent, the chatbot routes the request to the appropriate intent handler. Each handler corresponds to a specific workflow designed to address the user's request.
 
---
 
# Event Information Workflow
 
If the user requests information about upcoming events, the chatbot performs the following steps:
 
1. Fetch upcoming events from the system database or API.
2. Display the available event options to the user.
3. Allow the user to select a specific event.
4. Register the user for the selected event if required.
5. Send a confirmation message containing the event details.
 
---
 
# Donation Workflow
 
If the user wants to make a donation, the chatbot follows these steps:
 
1. Ask the user for the desired donation amount.
2. Generate a secure payment link.
3. Send the payment link to the user.
4. Confirm the donation completion once the payment is successful.
 
This workflow integrates with external payment systems to ensure secure transactions.
 
---
 
# Temple Directions Workflow
 
If the user asks for directions to a temple or center, the chatbot retrieves the location data and generates a navigation link.
 
Steps include:
 
1. Retrieve temple location information.
2. Generate a Google Maps link.
3. Send navigation directions and location details to the user.
 
This allows users to easily find the nearest temple or event location.
 
---
 
# FAQ and Knowledge Base Workflow
 
For general questions or volunteer-related inquiries, the chatbot searches a knowledge base to retrieve relevant answers.
 
Steps include:
 
1. Search the knowledge base for relevant information.
2. Retrieve the best matching response.
3. Return the answer to the user.
 
If the system determines that the response confidence is low, the request is escalated to human support to ensure accurate assistance.
 
---
 
# Error Handling and Recovery
 
The chatbot includes several recovery mechanisms to handle errors and unexpected user behavior.
 
---
 
## Invalid User Input
 
If the user enters a message that cannot be processed:
 
1. The chatbot asks the user to clarify the request.
2. The message is reprocessed through the intent detection system.
 
---
 
## API Failure Handling
 
If the chatbot encounters an external API failure:
 
1. The system retries the request up to two times.
2. If the request still fails, the issue is escalated to human support.
 
This ensures that system failures do not interrupt the conversation.
 
---
 
## User Inactivity
 
If the user becomes inactive during the conversation:
 
1. The chatbot sends a reminder message.
2. If no response is received, the system closes the session automatically.
 
This prevents unused sessions from remaining open indefinitely.
 
---
 
# Interaction Logging and Analytics
 
Throughout the interaction, the chatbot logs important metadata for monitoring and analytics purposes.
 
Logged data includes:
 
- detected intent
- communication channel
- success or failure of the interaction
- session duration
 
Additionally, the system emits analytics events when recovery paths are triggered. These events record information such as:
 
- error type
- recovery method
- timestamp
- session ID
- communication channel
 
These analytics logs help developers monitor chatbot performance and identify areas for improvement.
 
---
 
# Session Termination
 
Once the chatbot successfully completes the requested workflow or the user session times out, the conversation ends.
 
Before closing the session, the system records the final interaction metadata and logs the session outcome.
 
This ensures that all conversation data is preserved for future analysis and performance monitoring.
 
---
 
# Conclusion
 
The JKYog Multichannel Chatbot State Machine provides a structured framework for managing chatbot interactions across multiple communication channels. By combining language detection, intent recognition, context management, workflow routing, and robust error recovery mechanisms, the system ensures reliable and efficient chatbot performance.
 
The inclusion of analytics logging and human escalation paths further improves the chatbot's reliability and allows continuous improvement based on real interaction data.
