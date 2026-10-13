# English ↔ Tigrinya Translator Skill

An enforceable AI translation skill and linguistic reference framework for high-precision, context-aware translation between English and Tigrinya.

Designed for AI assistants (Grok, Claude, Codex, Antigravity) and developers building Tigrinya NLP tools, this skill enforces authentic Eritrean Geʽez grammar, eliminates English syntactic calques, filters out Amharic leakage, and provides comprehensive domain-specific glossaries.

---

## Key Features

- **Strict SOV Word Order:** Enforces Subject-Object-Verb syntax across all clause types.
- **Gerundive Chaining (ወሳኺ ግሲ):** Eliminates unnatural sequential "and" conjunctions by utilizing authentic Tigrinya gerund verbs.
- **Polypersonal Verb Agreement:** Full inflection for person, gender, number, direct object suffixes, and prepositional indirect object enclitics.
- **Anti-Amharic Filtration:** Actively filters out high-frequency Amharic lexical and morphological contaminations (*እኔ, ምግብ, ውሃ, ቤት, ነው, አል-…-ም, -ዎች*).
- **Accurate Geʽez Orthography:** Etymological fidel selection rules (distinguishing `አ` vs `ዐ`, `ሰ` vs `ሠ`, and `ጸ` vs `ፀ`).
- **Standardized Latin Transliteration:** Unified phonetic transliteration system marking consonant gemination (doubling), ejectives, and pharyngeals.
- **Orthodox Tewahedo & Biblical Domain Support:** Specialized terminology for Christology, Mariology, Patristics, and scriptural commentary.
- **Bidirectional Support:** Contextual translation for both English → Tigrinya and Tigrinya → English.

---

## Repository Structure

```
english-tigrinya-translator/
├── SKILL.md                                 # Core agent skill instructions and 5-step decision procedure
├── README.md                                # Project documentation
├── scripts/
│   └── audit_translation.py                 # Automated linguistic quality audit and benchmark runner
├── references/
│   ├── decisions.md                         # Dialect defaults, register rules, and English "you" resolution
│   ├── pronouns.md                          # Independent pronouns, polite forms, vocatives, and affix tables
│   ├── verb-skeleton.md                     # The 4 stems (√ፈለጠ model), gerundive-as-past, copula, and auxiliaries
│   ├── orthography.md                       # Punctuation, fidel disambiguation, labiovelars, and Latin transliteration
│   ├── anti-amharic.md                      # Rejection list for Amharic words, copulas, and suffixes
│   ├── examples.md                          # 15-item evaluation benchmark set with full linguistic rationales
│   ├── theological-glossary.md              # Orthodox Tewahedo theological and biblical vocabulary
│   ├── idioms-and-expressions.md            # Authentic conversational idioms, greetings, and discourse markers
│   └── bibliography-and-sources.md          # Canonical dictionaries, grammars, and patristic reference sources
└── docs/
    ├── plan.md                              # Implementation specification and roadmap
    └── review.md                            # Comprehensive linguistic audit and gap analysis
```

---

## Installation & Assistant Discovery

This skill is configured for universal discovery across modern AI developer tools via directory junctions:

* **Claude:** `~/.claude/skills/english-tigrinya-translator`
* **Codex:** `~/.codex/skills/english-tigrinya-translator`
* **Grok:** `~/.grok/skills/english-tigrinya-translator`

To verify with Grok CLI:
```powershell
grok inspect
```
The skill should appear under the `Skills` list with source `user`.

---

## Automated Linguistic Audit

Run the automated validation script against benchmark sentences or interactive text:

```powershell
# Run the built-in benchmark test suite:
python scripts/audit_translation.py --test

# Audit an individual translation string:
python scripts/audit_translation.py "ነቲ መግቢ በሊዐ።"
```

---

## Reference Guides

- [Decisions & Register](file:///references/decisions.md)
- [Pronouns & Affixes](file:///references/pronouns.md)
- [Verb System & Paradigms](file:///references/verb-skeleton.md)
- [Orthography, Punctuation & Transliteration](file:///references/orthography.md)
- [Anti-Amharic Rejection Filter](file:///references/anti-amharic.md)
- [Benchmark Translation Examples](file:///references/examples.md)
- [Theological & Biblical Glossary](file:///references/theological-glossary.md)
- [Idioms & Common Expressions](file:///references/idioms-and-expressions.md)
- [Bibliography & Reference Literature](file:///references/bibliography-and-sources.md)
