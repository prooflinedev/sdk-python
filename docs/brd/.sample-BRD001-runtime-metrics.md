# BRD001: SDK Runtime Metrics

## Problem
Users running `proofline-sdk` in production have no built-in way to observe request latency, retry counts, or error rates without wrapping every client call manually.

## Goal
Provide lightweight runtime metrics hooks in `ProoflineClient` and `AsyncProoflineClient` so applications can track SDK request performance and reliability.

## Business Value
- Faster troubleshooting of slow or failing API calls.
- Easy integration with standard monitoring tools (Prometheus, OpenTelemetry, Datadog) without adding heavy SDK dependencies.

## Success Criteria
- Users can pass an optional metrics callback/collector to the client.
- Every HTTP request records duration, status code, and retry count.
- Zero overhead when metrics collection is not configured.
