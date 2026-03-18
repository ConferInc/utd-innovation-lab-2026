# JKYog Chatbot Conversation Flowcharts
Author: Ananth Vangala

These state machine diagrams represent the chatbot conversation flows for the JKYog temple visitor support system.

---

# Visitor Inquiry Flow — State Machine Diagram

This diagram represents the chatbot state machine for handling visitor inquiries for the JKYog temple.  
The flow includes session initialization, visitor options, responses, and error handling.

```mermaid
stateDiagram-v2

[*] --> Session_Initialization

Session_Initialization --> Greeting

Greeting --> Inquiry_Options

Inquiry_Options --> Temple_Timings : Visitor selects Temple Timings
Inquiry_Options --> Upcoming_Events : Visitor selects Events
Inquiry_Options --> Visitor_Guidelines : Visitor selects Guidelines

Temple_Timings --> Provide_Timings
Provide_Timings --> End_Session

Upcoming_Events --> Provide_Event_Info
Provide_Event_Info --> End_Session

Visitor_Guidelines --> Provide_Guidelines
Provide_Guidelines --> End_Session

Inquiry_Options --> Error_State : Invalid input
Error_State --> Inquiry_Options : Ask visitor to select again

End_Session --> [*]
```

---

# Temple Directions Flow — State Machine Diagram

This diagram models how the chatbot assists visitors in getting directions to the temple.  
It handles location input, route generation, and error handling.

```mermaid
stateDiagram-v2

[*] --> Session_Initialization

Session_Initialization --> Greeting

Greeting --> Direction_Request

Direction_Request --> Ask_Starting_Location

Ask_Starting_Location --> GPS_Location : Visitor shares GPS
Ask_Starting_Location --> Manual_Address : Visitor types address
Ask_Starting_Location --> Invalid_Location : Unclear input

GPS_Location --> Generate_Route
Manual_Address --> Generate_Route

Generate_Route --> Provide_Directions

Invalid_Location --> Ask_Starting_Location : Retry

Provide_Directions --> Ask_More_Help

Ask_More_Help --> Direction_Request : Yes
Ask_More_Help --> End_Session : No

End_Session --> [*]
```

---

# Donation Request Flow — State Machine Diagram

This diagram represents how the chatbot assists users in making donations.  
It includes donation options, payment processing, confirmation, and error handling.

```mermaid
stateDiagram-v2

[*] --> Session_Initialization

Session_Initialization --> Greeting

Greeting --> Donation_Intent

Donation_Intent --> Provide_Donation_Options

Provide_Donation_Options --> Online_Donation : Donate Online
Provide_Donation_Options --> Temple_Donation : Donate at Temple
Provide_Donation_Options --> Invalid_Selection : Unclear input

Online_Donation --> Payment_Gateway

Payment_Gateway --> Payment_Success : Payment Approved
Payment_Gateway --> Payment_Failure : Payment Failed

Payment_Failure --> Retry_Payment : Retry
Retry_Payment --> Payment_Gateway

Temple_Donation --> Provide_Temple_Details

Invalid_Selection --> Provide_Donation_Options : Retry

Payment_Success --> Confirmation_Message
Provide_Temple_Details --> Confirmation_Message

Confirmation_Message --> Ask_More_Help

Ask_More_Help --> Donation_Intent : Yes
Ask_More_Help --> End_Session : No
