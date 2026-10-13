# Plan — make the English ↔ Tigrinya skill enforceable

Companion to `docs/review.md`. This is the work order. It does not change `SKILL.md` yet.

## Goal

When the skill is invoked, the model resolves the choices that change the Tigrinya sentence, then translates, then checks the result against a short list of forms. A reader should be able to tell which decisions were made. A later edit should be able to test those decisions against a fixed set of sentences.

## Rules for the edit itself

- One home per fact. Steps live in `SKILL.md`. Paradigms live in `references/`. The README only says how to install and run the skill. This `docs/` folder is for people, and `SKILL.md` does not tell the model to read it.
- `SKILL.md` names each reference file and the moment to open it. A file the procedure never opens is dead.
- Add a form only if it can be tied to a published paradigm (see the source list in the review). If a suffix has light and heavy variants, say so, and do not collapse them into one ending.
- Keep the skill body a procedure. The long tables stay in `references/`.
- Leave the other Tigrinya projects (`Tigrigna-to-latin-traslator`, `tigrinya-catena`, `haymanote-abew`) alone. This package is the translator skill.

## Phase 0 — Install it

The skill does nothing until Grok can see it.

1. Create `C:\Users\naibm\.grok\skills\`.
2. Put this folder there as `english-tigrinya-translator`, or make a directory link so the copy in `Documents\projects` stays the one you edit.
3. Confirm with `grok inspect` that the source is `user` and the name is `english-tigrinya-translator`.
4. In a new session, `/english-tigrinya-translator` should load the instructions.

Do this before judging translation quality. Until it is installed, a good or bad translation is the base model, not this skill.

## Phase 1 — Replace the procedure

Rewrite `SKILL.md` so the steps are decisions, in this order.

1. **Detect direction.** English → Tigrinya, Tigrinya → English, or a grammar check of Tigrinya the user already wrote.
2. **Resolve the open choices** and state them in the notes:
   - Dialect default: written Eritrean Tigrinya. Switch only if the user asks for Tigray usage.
   - Register: casual, familiar, or polite. Polite singular uses the plural pronoun and plural verb (ንስኹም / ንስኽን, and the matching plural endings). Familiar singular uses ንስኻ / ንስኺ.
   - English "you": gender, number, and respect. If the text does not settle them, ask before translating a short text. For a long text, pick the most likely reading, mark it, and keep it for the whole text.
   - Domain: everyday, formal, technical, religious. Religious text uses formal modern Tigrinya unless a phrase is in the reference list.
3. **Translate.**
   - Clause order: subject, object, verb.
   - Prepositions before the noun.
   - Drop independent pronouns unless the person is emphasized.
   - Definite direct object: article plus ን- (ነቲ, ነታ, ነቶም, ነተን).
   - Main-clause past: gerundive. Use the perfect or a compound tense only when the meaning needs it, and say why in the notes.
   - Negation: ኣይ-…-ን on a main clause. Drop -ን in a subordinate clause.
   - Questions: ዶ for yes/no. Content questions stay in place. A cleft with እዩ plus ዝ- is normal Tigrinya and is allowed.
   - "Have" and "must": ኣሎ plus a suffix, when that is the meaning.
4. **Check before answering.**
   - Open `references/anti-amharic.md` and reject any form on that list.
   - Verb ending matches the person, number, and gender decided in step 2.
   - One register for the whole text.
   - Gemination marked in the Latin line.
   - Spelling of look-alike letters consistent with the first choice in the document.
5. **Shape the answer.**
   - One sentence or a short message: Tigrinya, Latin, notes.
   - A paragraph or more: Tigrinya text, then notes only for choices that change meaning. Latin only if the user asks.
   - Tigrinya → English: idiomatic English, plus notes where gender, a proverb, or a gerundive chain does not map cleanly.

Delete the broken food example from `grammar-notes.md` in this phase. The corrected sentence belongs in `references/examples.md`:

- Neutral: ነቲ መግቢ በሊዐ. Latin: *näti mägbi bäliʿä.* "I ate the food."
- Contrastive subject: ኣነ ነቲ መግቢ በሊዐ. "I ate the food."

እኽሊ stays available for "grain", not for "a meal".

## Phase 2 — Fill `references/` and point at them

Replace the single thin grammar note with files the procedure opens. Each file is tables and short rules.

| File | Contents | Open it when |
| --- | --- | --- |
| `references/decisions.md` | Dialect default, register, the polite-plural rule, what to do when "you" is unresolved | Step 2, every translation |
| `references/pronouns.md` | Ten independent pronouns, polite forms, vocative ኣታ / ኣቲ, possessive suffixes, direct-object suffixes, prepositional suffixes. Note light vs heavy object suffixes | Any pronoun, possession, or object marker |
| `references/verb-skeleton.md` | The four stems, subject affixes (use the ፈለጠ table as the regular model), gerundive-as-past, negation, ዶ, copula, ኣሎ, "have/must". One sentence on laryngeal and *w/y* roots: do not force the regular vowel pattern onto them | Any finite verb |
| `references/orthography.md` | Look-alike letters, punctuation, and the Latin system below | Writing the Tigrinya or the Latin line |
| `references/anti-amharic.md` | The contrast list from the review, kept here as the only copy | The check step |
| `references/examples.md` | 20 to 30 checked pairs covering the cases in Phase 3 | When unsure of a construction; also the human test set |

Latin system, owned only by `orthography.md`:

- Vowels: *ä* (first order), *u*, *i*, *a*, *e*, *ə* (sixth order), *o*.
- Ejectives with an apostrophe: *t'*, *č'*, *p'*, *k'*, *s'*.
- Pharyngeals: *ḥ* for ሐ, *ʿ* for ዐ.
- Gemination written by doubling the consonant: *bäliʿä* has none; a doubled consonant must show, as in *qärräbä* versus *qäräbä*.
- Hyphens only at a morpheme boundary in a teaching note, not in a normal pronunciation line.

`grammar-notes.md` goes away once those files exist, so the old example cannot be reused.

`assets/` stays empty until there is a real asset. Do not keep a placeholder directory as if it did work.

## Phase 3 — Evaluation set

Put the prompts in `references/examples.md` and score a run by hand. Each item records the decision (gender, register, tense) and the Tigrinya. Pass means the decision is visible and the form matches the paradigm, not that a native speaker has signed off. A native-speaker pass is a separate later check.

Minimum set:

| # | English | What must be true in the output |
| --- | --- | --- |
| 1 | I ate the food. | ነቲ መግቢ በሊዐ. No ኣነ. Not እኽሊ. Not በሊዔ. |
| 2 | She ate the food. | Feminine gerundive, feminine article ነታ if the noun is treated feminine, or a justified gender for መግቢ kept consistent. |
| 3 | Did you see my sister? | ዶ, feminine "you" if that reading is stated, possessive on ሓፍተይ. |
| 4 | Please sit down. (to a respected man) | Plural polite agreement, one addressee, noted as polite. |
| 5 | Please sit down. (to a female friend) | Feminine singular imperative. |
| 6 | I do not know. | ኣይ-…-ን, first person. |
| 7 | the man who ate | Relative ዝ- before the noun. |
| 8 | Hagos met Almaz. | ን- on the definite object. |
| 9 | I have a house. | ኣሎኒ or an equivalent existence construction. ገዛ, not ቤት. |
| 10 | He is Eritrean. | Copula እዩ. Pro-drop. Not ነው. |
| 11 | There is no water. | Negative existence. ማይ, not ውሃ. |
| 12 | Come in and sit down. (m.) | Gerundive chain, then imperative. |
| 13 | A short proverb, asked as an idiom | A Tigrinya proverb, or a note that none was used. No word-for-word calque presented as an idiom. |
| 14 | A 150-word paragraph | One Tigrinya block. Same "you" and the same register throughout. Latin omitted. |
| 15 | Reverse: ነቲ መግቢ በሊዐ | "I ate the food." Note that the subject pronoun is absent in the source. |

Fail any item that uses an Amharic form from `anti-amharic.md`.

Run these only after Phase 0, in a fresh session that invokes the skill, so the test is of the skill and not of a chat that already contains this review.

## Phase 4 — Only if you ask

- A domain glossary (church, medical, school, software) as its own reference file, each term with a source.
- A Tigray-variety note, with pairs you actually use, once the Eritrean default is stable.
- A tiny script that checks a draft for the Amharic strings and for the letters በሊዔ when the intended word is በሊዐ. The script is a backstop. The procedure stays the real fix.
- Publishing as a plugin so another machine can install it. Local `~/.grok/skills` is enough for your own sessions.

## Work order

1. Phase 0, and confirm `grok inspect`.
2. Phase 1 procedure plus the corrected food example.
3. Pronouns, verb skeleton, orthography, anti-Amharic list.
4. The 15-item set, then a manual run.
5. Phase 4 only on request.

## Done when

- `grok inspect` lists the skill.
- `SKILL.md` tells the model which reference file to open at which step.
- The food example in the package is ነቲ መግቢ በሊዐ.
- A fresh `/english-tigrinya-translator` run of items 1, 4, 6, and 10 matches the table in Phase 3.
- No rule is copied into both `SKILL.md` and a reference file.
