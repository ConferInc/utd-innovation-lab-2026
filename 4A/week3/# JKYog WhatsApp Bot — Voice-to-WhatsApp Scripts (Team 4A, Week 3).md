\# JKYog WhatsApp Bot — Voice-to-WhatsApp Scripts (Team 4A, Week 3\)  
Owner: Chanakya Alluri    
Due: March 6, 2026 (11:59 PM CST)

\#\# 0\) Purpose  
These scripts handle:  
1\) Transition from a \*\*voice call\*\* (IVR/voice bot) into \*\*WhatsApp chat\*\* with the JKYog bot    
2\) Five \*\*error/fallback scenarios\*\* (user-safe messaging \+ recovery prompts)

Tone: respectful, calm, devotional-friendly, minimal friction.

\---

\#\# 1\) Variables & Conventions

\#\#\# Variables (placeholders)  
\- \`{TEMPLE\_NAME}\` \= JKYog Temple (or specific temple name if multiple)  
\- \`{CITY}\` \= (City Name)  
\- \`{WHATSAPP\_NUMBER}\` \= WhatsApp enabled business number (E.164)  
\- \`{WA\_LINK}\` \= \`https://wa.me/{WHATSAPP\_NUMBER}?text={ENCODED\_START\_TEXT}\`  
\- \`{START\_TEXT}\` \= “Hi” OR “JKYog” OR “Start”  
\- \`{SHORT\_CODE}\` \= 4–6 digit code (optional)  
\- \`{CASE\_ID}\` \= unique conversation/session id  
\- \`{HOURS}\` \= support hours for human escalation  
\- \`{SUPPORT\_LINE}\` \= human support phone (if available)

\#\#\# WhatsApp message style  
\- Keep messages under \~3 short paragraphs  
\- Use numbered options / quick reply buttons where supported  
\- Always provide a way to return “Menu” / “Start Over”

\---

\#\# 2\) Voice-to-WhatsApp Handoff — Core Flows

\#\#\# Flow A: Standard Handoff (User agrees \+ has WhatsApp)  
\*\*Goal:\*\* Send user a WhatsApp link and confirm next steps.

\*\*VOICE SCRIPT (Agent)\*\*  
1\) Greeting \+ capability    
\> “Namaste\! I can help with temple timings, directions, and donations. For faster support and links, I can continue on WhatsApp.”

2\) Consent check    
\> “Would you like me to send you a WhatsApp message now? Please say \*\*Yes\*\* or \*\*No\*\*.”

\*\*If YES\*\*  
3\) Confirm number (optional if caller ID available)    
\> “Great. I will send the message to the number you’re calling from. Is that okay?”

\- If user says “No”:    
\> “Please tell me the 10-digit mobile number you want to use for WhatsApp.”

4\) Set expectation    
\> “Perfect. You’ll receive a WhatsApp message in a few seconds. Please open it and reply \*\*Hi\*\* to begin.”

5\) Closure    
\> “I’ll stay on the line for 10 seconds—if you don’t receive it, I can resend.”

\*\*WHATSAPP MESSAGE (System / Bot)\*\*    
\> “Namaste 🙏 Welcome to {TEMPLE\_NAME}.    
Reply \*\*Hi\*\* to start.    
You can ask about:    
1\) Temple timings & events    
2\) Directions & parking    
3\) Donations & receipts”

\*\*Recovery button (if supported)\*\*  
\- Quick Replies: \`Hi\` | \`Menu\` | \`Talk to a volunteer\`

\---

\#\#\# Flow B: Handoff via “User-initiated WhatsApp” (No outbound message allowed)  
\*\*When:\*\* Policies/stack cannot send proactive WhatsApp message; user must start chat.

\*\*VOICE SCRIPT\*\*    
\> “To continue on WhatsApp, please message us first.    
Open WhatsApp and send \*\*Hi\*\* to this number: \*\*{WHATSAPP\_NUMBER}\*\*.    
You can also use this link: \*\*{WA\_LINK}\*\*.”

\> “Once you send \*\*Hi\*\*, our WhatsApp bot will guide you.”

\*\*WHATSAPP FIRST MESSAGE (User \-\> Bot):\*\* “Hi”

\*\*BOT REPLY\*\*    
\> “Namaste 🙏 You’re connected to {TEMPLE\_NAME}.    
How can I help today?    
1\) Visitor info (timings, events)    
2\) Directions (parking, transit)    
3\) Donations (receipt, recurring)”

\---

\#\#\# Flow C: Link \+ Short Code Verification (Optional, for continuity)  
\*\*When:\*\* You want to connect voice session \`{CASE\_ID}\` to WhatsApp chat.

\*\*VOICE SCRIPT\*\*    
\> “I’m sending a WhatsApp link now.    
To continue where we left off, please enter this code in WhatsApp: \*\*{SHORT\_CODE}\*\*.”

\*\*WHATSAPP MESSAGE\*\*    
\> “Namaste 🙏 To continue your call on WhatsApp, reply with this code: \*\*{SHORT\_CODE}\*\*.”

\*\*BOT AFTER CODE\*\*    
\> “Thank you\! I’ve restored your context.    
Do you want help with:    
1\) Visitor info    
2\) Directions    
3\) Donations    
Type 1, 2, or 3.”

\*\*If wrong code\*\*    
\> “Hmm—this code doesn’t match. Please try again, or type \*\*Start\*\* to begin fresh.”

\---

\#\#\# Flow D: User declines WhatsApp (Continue on voice)  
\*\*VOICE SCRIPT\*\*    
\> “No problem. I can still help here on the call.    
Please tell me what you need:    
1\) Temple timings & events    
2\) Directions & parking    
3\) Donations & receipts”

\---

\#\#\# Flow E: User says “I don’t have WhatsApp”  
\*\*VOICE SCRIPT\*\*    
\> “Understood. I can help on this call.    
If you’d like directions or donation links later, you can also check our website or we can connect you to a volunteer during {HOURS}.”

(If you have a public website)    
\> “You can also visit the temple page for details.”

\---

\#\# 3\) Five Error / Fallback Scenarios (User Messages \+ Recovery)

\#\#\# Error 1: Intent Not Understood  
\*\*When:\*\* The user’s message/call input doesn’t match known intents confidently.

\*\*VOICE (Gentle clarification)\*\*    
\> “Sorry, I didn’t fully understand that.    
Are you asking about \*\*timings/events\*\*, \*\*directions\*\*, or \*\*donations\*\*?”

\*\*WhatsApp\*\*    
\> “Sorry—I may have missed that. 🙏    
Please choose one:    
1\) Timings & events    
2\) Directions & parking    
3\) Donations & receipts    
Or type \*\*Menu\*\*.”

\*\*Recovery logic\*\*  
\- Retry classification once    
\- If still unclear → offer examples:    
  \- “Try: ‘What time is aarti?’ / ‘How do I reach the temple?’ / ‘I need a donation receipt’”

\---

\#\#\# Error 2: API Timeout (Backend didn’t respond)  
\*\*When:\*\* Maps/CRM/KB/receipt service times out.

\*\*VOICE\*\*    
\> “One moment—our system is taking longer than usual.    
I can try again, or I can continue this on WhatsApp for faster links. What do you prefer?”

\*\*WhatsApp\*\*    
\> “I’m having trouble reaching our system right now. 🙏    
Please try again in a moment.    
\- Type \*\*Retry\*\* to try again    
\- Type \*\*Menu\*\* to choose a different option    
\- Type \*\*Human\*\* to request a volunteer”

\*\*Recovery logic\*\*  
\- Auto-retry once after 3–5 seconds    
\- If second timeout → offer human escalation \+ log failure

\---

\#\#\# Error 3: Confusing User Input (Mixed details / ambiguous)  
\*\*When:\*\* User sends multiple requests or unclear data (e.g., “tomorrow parking donation receipt”).

\*\*VOICE\*\*    
\> “I heard a few things together. Let’s do one at a time.    
What would you like first: \*\*directions\*\*, \*\*timings\*\*, or \*\*donations\*\*?”

\*\*WhatsApp\*\*    
\> “Got it—there are a few things in your message. 🙏    
What should we do first?    
1\) Timings/events    
2\) Directions/parking    
3\) Donations/receipt”

\*\*Recovery logic\*\*  
\- Ask a single-choice question    
\- Maintain previous message as context note, but proceed stepwise

\---

\#\#\# Error 4: Context Lost (Session reset / user returns later)  
\*\*When:\*\* Bot lost state, WhatsApp reopened, or long gap.

\*\*VOICE\*\*    
\> “Welcome back. I may have lost our earlier context.    
Please tell me what you need now: timings, directions, or donations.”

\*\*WhatsApp\*\*    
\> “Welcome back 🙏 I may have lost the last step.    
Please type one:    
\- \*\*Timings\*\*    
\- \*\*Directions\*\*    
\- \*\*Donations\*\*    
Or type \*\*Start\*\* to begin again.”

\*\*Recovery logic\*\*  
\- Provide “Start” \+ “Menu”    
\- If user uses keywords, route accordingly    
\- If user previously had \`{CASE\_ID}\` and it’s recoverable → attempt restore silently

\---

\#\#\# Error 5: Failed Escalation to Human (No agent available / handoff failed)  
\*\*When:\*\* Volunteer/agent not reachable, shift ended, or handoff integration fails.

\*\*VOICE\*\*    
\> “I’m sorry—no volunteer is available right now.    
I can still help with basic info here, or you can try again during {HOURS}.    
Would you like \*\*timings\*\*, \*\*directions\*\*, or \*\*donations\*\*?”

\*\*WhatsApp\*\*    
\> “I’m sorry—our volunteer team isn’t available right now. 🙏    
I can still help here, or you can try again during {HOURS}.    
Meanwhile, choose:    
1\) Timings/events    
2\) Directions/parking    
3\) Donations/receipt    
Or type \*\*Leave a message\*\*.”

\*\*Recovery logic\*\*  
\- Offer async message capture (if supported):    
  \- collect name \+ question \+ preferred callback    
\- Otherwise provide self-serve menu \+ hours

\---

\#\# 4\) WhatsApp “Safety Nets” (Always Available Commands)  
At any time, user can type:  
\- \*\*Menu\*\* → show main options  
\- \*\*Start\*\* → reset flow  
\- \*\*Human\*\* → request volunteer (with hours fallback)  
\- \*\*Language\*\* → language switch (handled by Nikita’s logic)

\*\*Menu message\*\*    
\> “Namaste 🙏 Main Menu    
1\) Visitor info (timings, events)    
2\) Directions (parking, transit)    
3\) Donations (receipt, recurring)    
Type 1, 2, or 3.”

\---

\#\# 5\) Optional: Hindi \+ Gujarati Variants (Short)  
(Use if language is detected or user requests)

\#\#\# Hindi (WHATSAPP)  
\- Intent not understood:    
\> “माफ़ कीजिए 🙏 मैं समझ नहीं पाया।    
कृपया चुनें:    
1\) समय/कार्यक्रम    
2\) दिशा/पार्किंग    
3\) दान/रसीद    
या \*\*Menu\*\* लिखें।”

\#\#\# Gujarati (WHATSAPP)  
\- Intent not understood:    
\> “માફ કરશો 🙏 મને સમજી ન પડ્યું.    
કૃપા કરીને પસંદ કરો:    
1\) સમય/કાર્યક્રમ    
2\) દિશા/પાર્કિંગ    
3\) દાન/રસીદ    
અથવા \*\*Menu\*\* લખો।”

\---

\#\# 6\) Implementation Notes (Handoff Logic Summary)  
\- If outbound WhatsApp is permitted:  
  \- Send WhatsApp message with \`{WA\_LINK}\` \+ welcome \+ quick options  
\- If outbound not permitted:  
  \- Use “user-initiated” flow and provide number \+ wa.me link  
\- If continuity is required:  
  \- Use \`{SHORT\_CODE}\` and bind voice session \`{CASE\_ID}\` to WhatsApp session  
\- Always provide:  
  \- Menu/Start commands  
  \- Human escalation with hours fallback  
  \- Single-choice recovery prompts for ambiguous inputs  
