# Mobile Agents (Android + iOS)

This folder is intentionally a scaffold.

## Goal
- Android Agent (APK): Voice-first control + Google Fit ingest
- iOS Agent: Voice control + HealthKit ingest

## Backend contract
- POST /health/ingest (to be added in next step)
- POST /voice-chat (already added): audio -> STT -> AI -> TTS

## Next step
Implement lightweight apps that:
1) capture microphone audio
2) send it to /voice-chat
3) play returned OPUS audio
4) periodically read HealthKit/Google Fit and POST to /health/ingest
