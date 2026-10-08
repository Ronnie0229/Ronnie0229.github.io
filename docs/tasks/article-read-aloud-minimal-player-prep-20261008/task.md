# Article Read-Aloud — Minimal Article Player Preparation

状态：PASS_MINIMAL_ARTICLE_AUDIO_PLAYER_PREP / READY_FOR_AUDIO_UPLOAD_AND_REAL_URL_BINDING_AUTHORIZATION
日期：2026-10-08

## Accepted Pilot audio

PROJECT_OWNER second-listening result: PASS.

Accepted local delivery candidate:
`artifacts/read-aloud/pilot/post-32d30724d859c99c/pilot-repaired-64k.mp3`

SHA-256:
`67e0286b29312f24bfc6c5aa9e6cdcd3cdee1a3d15612d3c2e9518c1634e8a47`

Known accepted limitation:
- `著名` remains mispronounced;
- PROJECT_OWNER has explicitly stopped further improvement for this Pilot and approved continuing.

## Goal

Prepare the smallest Website-side article audio player support without publishing audio yet.

## Implementation

- add optional frontmatter field `audioUrl`;
- render a native HTML `<audio controls preload="metadata">` only when `audioUrl` is present;
- position it after article header/tags and before article body;
- add minimal accessible label/text and responsive styling;
- no JS audio framework;
- no autoplay;
- no waveform/timeline/highlight/feed;
- no publication hard gate.

## This task does NOT authorize

- R2 upload;
- NAS copy;
- production deploy;
- adding a fake/placeholder URL to the real Pilot article;
- commit/push.

## Verification

- content schema tests / relevant tests;
- player rendering coverage;
- full Website test suite;
- Astro build;
- git diff --check.

## Expected stop

`PASS_MINIMAL_ARTICLE_AUDIO_PLAYER_PREP / READY_FOR_AUDIO_UPLOAD_AND_REAL_URL_BINDING_AUTHORIZATION`
