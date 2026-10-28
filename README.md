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
├── vercel.json                              # Zero-config Vercel deployment configuration
├── public/
│   └── index.html                           # Static Grammarly-style Tigrinya Studio UI for Vercel
├── api/
│   └── index.py                             # Vercel Python Serverless Function (/api/check, /api/fix, /api/ai-check)
├── scripts/
│   ├── audit_translation.py                 # Automated linguistic quality audit, auto-fixer, and CLI
│   ├── studio.py                            # Local Web Studio HTTP server & request handler
│   ├── sync_skill.py                        # Multi-repository SHA-256 skill synchronizer
│   └── test_studio.py                       # Automated studio API & UI integration tests
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

## Automated Linguistic Audit, Auto-Fixing & Web Studio

### 1. Interactive Grammarly-Style Web Studio (Local & Vercel Cloud)
Launch the standalone zero-dependency Web Studio locally with color-coded underlines, interactive popover cards, 1-click replacement, and writing quality scoring:

```powershell
python scripts/studio.py
# or
python scripts/audit_translation.py --studio
```
Open `http://localhost:8765` in any browser.

#### Deploying to Vercel
This repository is pre-configured for zero-config deployment on **Vercel**:
1. Import `naibwedi/english-tigrinya-translator` into Vercel.
2. Add `GEMINI_API_KEY` under **Project Settings → Environment Variables** to enable the cloud **✨ Deep AI Check** button.
3. Deploy — Vercel serves `public/index.html` at `/` and routes `/api/check`, `/api/fix`, `/api/ai-check`, and `/api/health` to `api/index.py`.

### 2. Benchmark Verification Test Suite
Run the 36-test benchmark test suite verifying punctuation, dash preservation, Geʽez spacing, and character offsets:

```powershell
python scripts/audit_translation.py --test
```

### 3. Deterministic Auto-Fixing CLI
Fix AI dashes, pre-punctuation spacing, stray Latin colons, and house-style variants while protecting verse ranges and compound words:

```powershell
python scripts/audit_translation.py --fix "እቲ ምስጢር -- ኣብ ህይወት እዩ ።"
# Output: "እቲ ምሥጢር፦ ኣብ ሕይወት እዩ።"
```

### 4. Deep Gemini AI Grammar Check
Run deep semantic and syntactic analysis (SOV, gerund chaining, pro-drop) using Gemini AI:

```powershell
python scripts/audit_translation.py --ai "ነቲ መግቢ በሊዐ።"
```

### 5. Multi-Repository Skill Synchronization
Synchronize canonical skill updates across `tigrinya-catena` and global Antigravity skill folders:

```powershell
python scripts/sync_skill.py
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
