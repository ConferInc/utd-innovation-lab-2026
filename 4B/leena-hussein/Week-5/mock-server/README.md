# Mock Server Notes

This folder supports offline integration testing for Week 5.

## Purpose
The mock setup allows Group 4B to test:
- webhook success responses
- Stripe donation responses
- Maps directions responses
- Calendar event responses

## Main Config
See `mock-server-config.json` in the project root.

## Base URL
`http://localhost:3001`

## Usage
Point test requests to the mock endpoints instead of live services when external dependencies are unavailable.