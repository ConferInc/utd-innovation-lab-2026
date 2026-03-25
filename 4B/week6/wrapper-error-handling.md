\# Wrapper Error Handling

\#\# Overview  
This document describes the production-grade error handling added to the Stripe, Google Maps, and Google Calendar service wrappers.

\---

\#\# 1\. Stripe Wrapper

\#\#\# Errors handled  
\- Invalid request errors  
\- API connection errors / timeouts  
\- Stripe API internal errors  
\- Rate limit errors  
\- Circuit breaker open state

\#\#\# Retry strategy  
\- Retries: 3 attempts  
\- Delay: 1 second  
\- Retryable errors:  
  \- \`stripe.APIConnectionError\`  
  \- \`stripe.APIError\`  
  \- \`stripe.RateLimitError\`

\#\#\# Non-retryable errors  
\- Invalid request / bad input  
\- Missing configuration  
\- Amount \<= 0

\#\#\# Fallback behavior  
\- Logs contextual error details  
\- Raises structured application error  
\- Fails fast when circuit breaker is open

\---

\#\# 2\. Google Maps Wrapper

\#\#\# Errors handled  
\- Timeout errors  
\- Temporary client errors  
\- Missing input  
\- Circuit breaker open state

\#\#\# Retry strategy  
\- Retries: 3 attempts  
\- Delay: 1 second  
\- Retryable errors:  
  \- \`TimeoutError\`  
  \- temporary client exceptions

\#\#\# Non-retryable errors  
\- Missing address/origin/destination  
\- Missing API key

\#\#\# Fallback behavior  
\- Logs request context  
\- Raises runtime error after retry exhaustion  
\- Fails fast when circuit breaker is open

\---

\#\# 3\. Google Calendar Wrapper

\#\#\# Errors handled  
\- Timeout errors  
\- Temporary API execution failures  
\- Missing credentials  
\- Missing summary/event input  
\- Circuit breaker open state

\#\#\# Retry strategy  
\- Retries: 3 attempts  
\- Delay: 1 second  
\- Retryable errors:  
  \- \`TimeoutError\`  
  \- temporary API exceptions

\#\#\# Non-retryable errors  
\- Missing credentials file  
\- Invalid summary or input validation failures

\#\#\# Fallback behavior  
\- Logs request context  
\- Raises runtime error after retry exhaustion  
\- Fails fast when circuit breaker is open

\---

\#\# Circuit Breaker Pattern

All wrappers use a shared circuit breaker:  
\- Opens after 3 consecutive failures  
\- While open, requests fail immediately  
\- Automatically resets after timeout window

This prevents repeated calls to unhealthy upstream services.

\---

\#\# Health Checks

Each wrapper exposes a \`health\_check()\` function that reports:  
\- service name  
\- whether required configuration is present  
\- whether the circuit breaker is open

These checks support operational debugging and readiness checks.  
