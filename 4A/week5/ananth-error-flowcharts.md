## Visitor Inquiry Flow — Error Handling Added

```mermaid
stateDiagram-v2
[*] --> SessionInitialization

SessionInitialization --> Greeting
Greeting --> UserInquiry

UserInquiry --> TempleTimings : ask timings
UserInquiry --> EventInformation : ask events
UserInquiry --> VisitorGuidelines : ask rules

UserInquiry --> IntentFailure : unclear request

IntentFailure --> ClarificationPrompt
ClarificationPrompt --> UserInquiry : user clarifies

ClarificationPrompt --> FallbackState : repeated failure
FallbackState --> HumanSupport : escalate

TempleTimings --> ResponseDelivered
EventInformation --> ResponseDelivered
VisitorGuidelines --> ResponseDelivered

ResponseDelivered --> AskMoreHelp

AskMoreHelp --> UserInquiry : yes
AskMoreHelp --> EndSession : no

EndSession --> [*]
```

## Temple Directions Flow — Error Handling Added

```mermaid
stateDiagram-v2
[*] --> SessionInitialization

SessionInitialization --> Greeting
Greeting --> DirectionRequest

DirectionRequest --> AskStartingLocation

AskStartingLocation --> GPSLocation
AskStartingLocation --> ManualAddress
AskStartingLocation --> InvalidLocation

InvalidLocation --> RetryLocationInput
RetryLocationInput --> AskStartingLocation

RetryLocationInput --> FallbackNavigation : repeated failure

GPSLocation --> GenerateRoute
ManualAddress --> GenerateRoute

GenerateRoute --> RouteNotFound
RouteNotFound --> RetryLocationInput

GenerateRoute --> ProvideDirections

FallbackNavigation --> HumanSupport

ProvideDirections --> AskMoreHelp

AskMoreHelp --> DirectionRequest : yes
AskMoreHelp --> EndSession : no

EndSession --> [*]
```

## Donation Request Flow — Error Handling Added

```mermaid
stateDiagram-v2
[*] --> SessionInitialization

SessionInitialization --> Greeting
Greeting --> DonationIntent

DonationIntent --> ProvideDonationOptions

ProvideDonationOptions --> OnlineDonation
ProvideDonationOptions --> TempleDonation
ProvideDonationOptions --> InvalidSelection

InvalidSelection --> RetrySelection
RetrySelection --> ProvideDonationOptions

OnlineDonation --> PaymentGateway

PaymentGateway --> PaymentSuccess
PaymentGateway --> PaymentFailure

PaymentFailure --> RetryPayment
RetryPayment --> PaymentGateway

RetryPayment --> RollbackDonationState : repeated failure

RollbackDonationState --> DonationIntent

TempleDonation --> ProvideTempleDetails

PaymentSuccess --> ConfirmationMessage
ProvideTempleDetails --> ConfirmationMessage

ConfirmationMessage --> AskMoreHelp

AskMoreHelp --> DonationIntent : yes
AskMoreHelp --> EndSession : no

EndSession --> [*]
```
## Intent Recognition Error Handling

```mermaid
stateDiagram-v2
[*] --> UserInput

UserInput --> IntentRecognition

IntentRecognition --> IntentMatched : intent detected
IntentRecognition --> IntentFailure : intent unclear

IntentMatched --> ProcessIntent

IntentFailure --> ClarificationPrompt
ClarificationPrompt --> IntentRecognition : user retries

ClarificationPrompt --> FallbackState : repeated failure

FallbackState --> HumanSupport : escalate

ProcessIntent --> ContinueConversation

ContinueConversation --> [*]
```
## External API Failure Handling

```mermaid
stateDiagram-v2
[*] --> ServiceRequest

ServiceRequest --> CallExternalAPI

CallExternalAPI --> APISuccess : response received
CallExternalAPI --> APIFailure : timeout / error

APIFailure --> RetryAPI

RetryAPI --> CallExternalAPI : retry
RetryAPI --> FallbackService : repeated failure

FallbackService --> CachedResponse
FallbackService --> HumanSupport

APISuccess --> ProcessResponse

ProcessResponse --> ContinueConversation

ContinueConversation --> [*]
```



