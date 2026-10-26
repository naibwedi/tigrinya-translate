---
name: english-tigrinya-translator
description: Enforceable English ↔ Tigrinya translator skill. Resolves grammatical choices (gender, number, register, dialect), enforces strict SOV syntax and gerundive past, consults domain glossaries, and filters Amharic leakage.
---

# English ↔ Tigrinya Translator Procedure

When invoked, execute the following five-step decision procedure in order. Every step resolves linguistic choices before generating or finalizing text.

---

## Step 1 — Detect Direction
Identify the requested task:
1. **English → Tigrinya translation** (proceed to Step 2).
2. **Tigrinya → English translation** (proceed to Step 5C).
3. **Grammar & naturalness check** of Tigrinya text supplied by the user (audit against [`references/verb-skeleton.md`](file:///references/verb-skeleton.md) and [`references/anti-amharic.md`](file:///references/anti-amharic.md)).

---

## Step 2 — Resolve Open Choices
Open and consult [`references/decisions.md`](file:///references/decisions.md) before writing any Tigrinya. Resolve each open variable and record the choice in your internal notes:
- **Dialect:** Default to written **Eritrean Tigrinya**. Switch to Tigray Tigrinya only if explicitly requested.
- **Register:** Determine whether the context is **familiar singular** (*ንስኻ* m. / *ንስኺ* f.) or **polite singular** (*ንስኹም* m. / *ንስኽን* f. with plural verb agreement). Default to polite/respectful when addressing elders, strangers, or professionals.
- **English "You" Disambiguation:** Resolve gender (masculine vs. feminine), number (singular vs. plural), and social distance. If translating a short ambiguous sentence, either clarify or provide the primary readings clearly labeled.
- **Domain:**
  - *Conversational / Everyday:* Consult [`references/idioms-and-expressions.md`](file:///references/idioms-and-expressions.md).
  - *Theological / Biblical / Liturgical:* Open and enforce [`references/theological-glossary.md`](file:///references/theological-glossary.md).
  - *Formal / Administrative:* Use standard civic terminology.

---

## Step 3 — Translate
Apply the morphological and syntactic rules documented in the references:
1. **Clause Order:** Strict **Subject – Object – Verb (SOV)**. Relative clauses (prefixed with *ዝ-* or *ዘይ-*) precede head nouns.
2. **Prepositions:** Prepositions (*ኣብ, ን, ብ, ምስ, ካብ, ናብ, ናይ*) precede the noun.
3. **Pronouns & Affixes:** Open [`references/pronouns.md`](file:///references/pronouns.md). Omit independent subject pronouns (*ኣነ, ንሱ, ንሳ*) unless emphasized (pro-drop). Definite direct objects take prefix **ን-** fused with the article (**ነቲ** masc., **ነታ** fem., **ነቶም** pl. m., **ነተን** pl. f.).
4. **Verb Construction:** Open [`references/verb-skeleton.md`](file:///references/verb-skeleton.md).
   - Use the **gerundive** (*ወሳኺ ግሲ*) for completed past actions in main clauses (e.g. *ነቲ መግቢ በሊዐ* "I ate the food"; *መጺኡ* "he arrived").
   - Chain sequential actions with gerunds, not English-style conjunctions (*-ን* or *እሞ*).
   - Main-clause negation takes **ኣይ-…-ን**; subordinate negation takes **ዘይ-** (drop *-ን*).
   - Yes/no questions take the particle **ዶ**.
   - Express "have" and "must" using **ኣሎ** plus pronominal suffixes (*ኣሎኒ*, *ክኸይድ ኣሎኒ*).
   - Do not force regular *fäläṭä* vowel patterns onto laryngeal or weak roots.
5. **Benchmarks:** Open [`references/examples.md`](file:///references/examples.md) when handling comparable sentence structures.

---

## Step 4 — Check Before Answering (Pre-flight Audit)
Verify the draft against these mandatory filters:
1. **Anti-Amharic Filter:** Open [`references/anti-amharic.md`](file:///references/anti-amharic.md) and reject every Amharic intrusion (e.g., ensure *ኣነ* not *እኔ*, *እዩ* not *ነው*, *መግቢ* not *ምግብ*, *ማይ* not *ውሃ*, *ገዛ* not *ቤት*, *ኣይ-…-ን* not *አል-…-ም*).
2. **Agreement Consistency:** Check that verb person, number, and gender endings match the decisions made in Step 2.
3. **Orthography & Punctuation:** Open [`references/orthography.md`](file:///references/orthography.md). Ensure *አ* vs *ዐ*, *ሰ* vs *ሠ*, and *ጸ* vs *ፀ* are consistent. Use Geʽez punctuation (`።`, `፣`, `፤`, `፦`).
   - Outside supplied verbatim Scripture quotations, enforce the controlled house spellings in the reference, including **ሕይወት**, **መሥዋዕት**, **ነቢያት**, **ቤተ ክርስቲያን**, **ሠለስተ**, **ሥልጣን**, **ምሥጢር**, **መሠረት**, **ሥምረት**, **ድኅነት**, **ኃጢኣት**, **ጊዜ**, and **ኰከብ**.
   - Use **፧** for questions. Retain standard Eritrean **መጹ**; do not replace it mechanically with **መጽኡ**.
4. **Latin Gemination:** In the Latin pronunciation line, mark gemination by doubling the consonant (e.g. *qärräbä* vs *qäräbä*).

---

## Step 5 — Shape the Answer

### A. For Single Sentences or Short Messages:
```markdown
**ትግርኛ (Geʽez):**
[Natural, grammatically verified translation]

**Latin Transliteration:**
[Accurate Latin pronunciation with gemination marked — see references/orthography.md]

**Notes:**
- Register: [Polite / Familiar / Formal]
- Key Choices: [Brief justification of agreement, vocabulary, or idiom decisions]
```

### B. For Paragraphs or Extended Documents:
Provide the full Tigrinya text directly. Include Latin transliteration only if the user explicitly requested it. Restrict notes to choices that affect meaning or register.

### C. For Tigrinya → English Translations:
Provide natural, idiomatic English. Add brief notes only where grammatical features (such as gerundive chaining, gender distinction, or cultural idioms) cannot be mapped cleanly into English.

---

## Reference Library
- Decisions & Registers: [`references/decisions.md`](file:///references/decisions.md)
- Pronouns & Affixes: [`references/pronouns.md`](file:///references/pronouns.md)
- Verb System & Paradigms: [`references/verb-skeleton.md`](file:///references/verb-skeleton.md)
- Orthography, Punctuation & Transliteration: [`references/orthography.md`](file:///references/orthography.md)
- Anti-Amharic Rejection Filter: [`references/anti-amharic.md`](file:///references/anti-amharic.md)
- Benchmark Translation Examples: [`references/examples.md`](file:///references/examples.md)
- Theological & Patristic Glossary: [`references/theological-glossary.md`](file:///references/theological-glossary.md)
- Idioms & Discourse Markers: [`references/idioms-and-expressions.md`](file:///references/idioms-and-expressions.md)
- Canonical Dictionaries & Literature: [`references/bibliography-and-sources.md`](file:///references/bibliography-and-sources.md)
