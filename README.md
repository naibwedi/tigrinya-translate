# English ↔ Tigrinya Translator Skill

An AI skill and linguistic reference framework for high-precision, context-aware translation between English and Tigrinya.

Designed for AI assistants (Grok, Antigravity, Gemini, Claude) and developers building Tigrinya NLP tools, this skill enforces authentic Ethiopian/Eritrean Geʽez grammar, eliminates English syntactic calques, and provides comprehensive domain-specific glossaries.

---

## Key Features

- **Strict SOV Word Order:** Enforces Subject-Object-Verb syntax across all clause types.
- **Gerundive Chaining (ወሳኺ ግሲ):** Eliminates unnatural sequential "and" conjunctions by utilizing authentic Tigrinya gerund verbs.
- **Polypersonal Verb Agreement:** Full inflection for person, gender, number, direct object suffixes, and prepositional indirect object enclitics.
- **Accurate Geʽez Orthography:** Etymological fidel selection rules (distinguishing `አ` vs `ዐ`, `ሰ` vs `ሠ`, and `ጸ` vs `ፀ`).
- **Standardized Latin Transliteration:** Complete 250+ character phonetic transliteration table covering primary orders, labiovelars, and Geʽez numerals.
- **Orthodox Tewahedo & Biblical Domain Support:** Specialized terminology for Christology, Mariology, Patristics, and scriptural commentary.
- **Bidirectional Support:** Contextual translation for both English → Tigrinya and Tigrinya → English.

---

## Repository Structure

```
english-tigrinya-translator/
├── SKILL.md                                 # Core agent skill instructions and two-pass translation workflow
├── README.md                                # Project documentation
├── references/
│   ├── grammar-notes.md                     # Morphosyntax, verb conjugation paradigms, negation, and pronouns
│   ├── transliteration-table.md             # Complete Geʽez syllabary to Latin transliteration matrix
│   ├── orthography-and-punctuation.md       # Fidel disambiguation rules, punctuation, and dialect standards
│   ├── theological-glossary.md              # Orthodox Tewahedo theological and biblical vocabulary
│   ├── idioms-and-expressions.md            # Authentic conversational idioms, greetings, and discourse markers
│   └── bibliography-and-sources.md          # Canonical dictionaries, grammars, and patristic reference sources
└── assets/                                  # Linguistic assets and test cases
```

---

## Output Standard

When active, the skill formats translations systematically:

```markdown
**ትግርኛ (Geʽez):**
[Accurate, natural translation in proper Geʽez script]

**Latin Transliteration:**
[Phonetic pronunciation guide]

**Linguistic & Contextual Notes:**
- **ድምጺ / ቅዲ (Register & Tone):** [Polite / Respectful / Casual / Theological]
- **ቀንዲ ምርጫታት (Key Choices):** [Morphological choices, non-literal equivalents, or idiom handling]
- **ካልእ ኣማራጺ (Alternative):** [Optional natural alternative]
```

---

## Reference Guides

- [Grammar & Morphosyntax](file:///references/grammar-notes.md)
- [Transliteration Guide](file:///references/transliteration-table.md)
- [Orthography & Punctuation](file:///references/orthography-and-punctuation.md)
- [Theological & Biblical Glossary](file:///references/theological-glossary.md)
- [Idioms & Common Expressions](file:///references/idioms-and-expressions.md)
- [Bibliography & Reference Literature](file:///references/bibliography-and-sources.md)
