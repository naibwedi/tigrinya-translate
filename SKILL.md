---
name: english-tigrinya-translator
description: Precise English to Tigrinya (and reverse) translation that preserves meaning, enforces SOV grammar, correct Geʽez script, verb agreement, and natural tone. Use when translating text, messages, documents, idioms, or checking Tigrinya grammar and naturalness.
---

# English ↔ Tigrinya Contextual Translator

## Overview

Provides context-aware, natural translations between English and Tigrinya. Prioritizes fluent, idiomatic Tigrinya over literal word-for-word rendering while strictly respecting SOV structure, verb morphology, and appropriate register.

## Core Principles

- Produce natural, fluent Tigrinya — never English word-order calques.
- Enforce **SOV (Subject–Object–Verb)** word order.
- Match verb conjugations and object pronouns to subject person, number, and gender.
- Prefer culturally authentic equivalents for idioms and fixed expressions.
- Default to polite/respectful register unless casual tone is clearly requested.
- Keep Geʽez orthography standard and consistent.

## Translation Workflow

1. **Analyze**
   - Register: Formal / Polite / Casual / Intimate
   - Domain: everyday conversation, religious, technical, emotional, legal, etc.
   - Identify idioms, culture-specific concepts, or ambiguous phrases that need non-literal treatment.

2. **Translate**
   - Output correct Geʽez script.
   - Maintain strict SOV order.
   - Apply accurate verb morphology and possessive/object suffixes.
   - Use natural collocations and common Tigrinya phrasing.

3. **Verify (internal checklist)**
   - SOV order is correct.
   - Verb agrees with the subject in person, number, and gender.
   - Tone matches the requested or implied register.
   - No leakage of English syntax.
   - The result would sound natural to a native speaker.

## Output Format

Always structure the response as follows:

**Tigrinya (Geʽez):**
[natural, grammatically correct translation]

**Latin transliteration:**
[clear, consistent Latin-script pronunciation guide — omit only if the user explicitly does not want it]

**Notes:**
- Tone: [Formal / Polite / Casual / etc.]
- Key choices: [brief explanation of non-literal renderings, agreement decisions, or residual ambiguities]
- Alternatives (optional): [1–2 other natural options when useful]

## Special Cases

- **Idioms & proverbs**: Prefer authentic Tigrinya equivalents rather than literal translation.
- **Proper names**: Retain as commonly used in Tigrinya contexts, or keep original form when appropriate.
- **Ambiguity**: When the English source is ambiguous, note the possible readings and select the most probable one (or ask the user for clarification).
- **Tigrinya → English**: Provide natural, idiomatic English plus short notes on any cultural or grammatical points that do not map cleanly.
- **Religious / biblical language**: Handle with care and appropriate formality; prefer established ecclesiastical phrasing when relevant.

## Consistency Notes

- Prefer standard Tigrinya (as used in Eritrea and northern Ethiopia) unless a specific dialect is requested.
- When multiple natural renderings exist, choose the most widely understood form and note alternatives if helpful.
- For longer documents, maintain consistent terminology and register throughout.
