# English ↔ Tigrinya skill — review

Reviewed 13 October 2026. This file is the check of the skill as it exists today, plus the language research behind the plan in `docs/plan.md`.

The package is a Grok skill: instructions for the model, not a translator program. Nothing in the folder conjugates a verb or checks a spelling. Quality depends on how specific those instructions are, and on whether Grok loads them at all.

## Where it lives

```
Documents/projects/english-tigrinya-translator/
├── SKILL.md                  # 69 lines, the instructions Grok would follow
├── references/grammar-notes.md   # 27 lines
├── assets/                   # empty
├── README.md
└── docs/                     # this review and the plan
```

Grok only discovers a skill when `SKILL.md` sits in a skill directory it scans. The usual places are:

| Location | Scope |
| --- | --- |
| `<repo>/.grok/skills/<name>/SKILL.md` | This repository |
| `~/.grok/skills/<name>/SKILL.md` | All projects for this user |
| `~/.claude/skills/` and `~/.cursor/skills/` | Compatibility paths |
| A directory listed under `[skills] paths` in `~/.grok/config.toml` | Extra roots |

`C:\Users\naibm\.grok\skills` does not exist. `config.toml` has no extra skill path. This folder is a normal project directory, so Grok does not load it. Asking for a Tigrinya translation in a new session will not run these instructions.

The README says to place the folder in `~/.grok/skills/`. That is the right install step. It has not been done.

Sibling files are not loaded with the skill. The user guide says long reference material belongs in sibling files, and `SKILL.md` must tell the model to read them. `SKILL.md` never mentions `references/grammar-notes.md`. Even after install, that file would sit unused unless the model happened to open it.

## What the skill asks for

`SKILL.md` tells the model to:

- Translate English ↔ Tigrinya in natural language, with Geʽez script.
- Keep clause order subject–object–verb.
- Match the verb to person, number, and gender.
- Default to a polite register.
- Prefer real Tigrinya idioms.
- Always answer with three blocks: Tigrinya, a Latin pronunciation guide, and notes on tone and word choice.
- Treat religious language carefully and prefer established church phrasing.

The description in the frontmatter is specific enough for automatic invocation once the skill is installed. It names translation, messages, documents, idioms, and grammar checks. Optional fields that would help are not set: `when-to-use`, `argument-hint`.

## What holds up

These choices match the language and the way skills should be written:

- Clause order in Tigrinya is subject–object–verb. That part of the instruction is right.
- Verbs agree with the subject in person, number, and, for second and third person, gender. Ten person/number/gender combinations, not the seven English has.
- Idioms should use a Tigrinya expression when one exists.
- Register matters. Tigrinya has a real polite-address system.
- A separate `references/` folder is the right place for tables. The folder is the right idea and the wrong contents.
- The skill is one workflow. It does not try to be a dictionary app, a transliterator product, and a grammar textbook at once.

## What is wrong or too thin

### The only worked example is off

`references/grammar-notes.md` gives:

> "I ate the food" → ኣነ ንእኽሊ በሊዔ

Three separate problems:

1. **Noun.** እኽሊ is grain or cereal. A meal is መግቢ.
2. **Definiteness.** "The" is a real word in Tigrinya (እቲ masculine, እታ feminine). A definite object also takes the accusative prefix ን-. "The food" as an object is ነቲ መግቢ.
3. **Verb spelling and pronoun.** The usual past in a main clause is the gerundive. For a regular verb the first-person gerundive ends in *-ä*, written with the first-order letter, as in ፈሊጠ *fäläṭä* "I knew". The matching spelling of "I ate" is በሊዐ. The file writes በሊዔ, with the fifth-order vowel ዔ. ኣነ is the emphatic "I". A neutral sentence drops it, because Tigrinya is pro-drop: the verb already says who the subject is.

A neutral rendering of "I ate the food" is ነቲ መግቢ በሊዐ. ኣነ ነቲ መግቢ በሊዐ is what you say when "I" is contrasted with someone else.

That example is the only concrete Tigrinya in the whole skill. A model that imitates it will copy the mistakes.

### The grammar file states duties and gives no forms

It says object markers attach to the verb, and possessive suffixes attach to the noun. It does not list a single suffix. It says verbs agree in gender and does not show one masculine/feminine pair. Those lines do not change model output. The forms have to live somewhere the procedure actually reads.

The same SOV, register, and idiom rules are repeated in `SKILL.md`, `grammar-notes.md`, and `README.md`. The reference file should be the home of the paradigms. The skill file should be the home of the steps.

### "Strict SOV" is only the clause order

Subject–object–verb is the default clause order. Other orders are also fixed, and they are not "verb at the end" copied onto every phrase:

- Tigrinya uses **prepositions** (ኣብ, ን, ብ, ምስ, ካብ, ናብ, ናይ), which stand before the noun.
- A definite direct object is marked with ን- (ነቲ መግቢ).
- Adjectives agree in gender and number. Many follow the noun. Modifiers do not all precede the head.
- A relative clause is a prefix ዝ- / ዘይ- on the verb, and the clause usually comes before the noun.
- Yes/no questions use the particle ዶ.
- Negation on a main clause is the circumfix ኣይ-…-ን. In a subordinate clause the final -ን drops.
- The normal past in a main clause is the gerundive (በሊዐ "I ate"), which is also the form that chains clauses (ገዲፍካ ተዛረብ "stop and speak").
- The copula (እዩ "he is") and the verb of existence (ኣሎ "there is / he exists") are irregular. "Have" and "must" are ኣሎ plus an object suffix (ኣሎኒ "I have / I must"), not a verb meaning "have".

An instruction that only says "keep SOV" does not stop English adjective order, English question order, a copied "have", or a perfect used where a native speaker would use the gerundive.

### Polite is a grammatical choice, and the skill does not say so

Polite address to one person uses the plural pronoun without -ኻት- / -ኣት-, and the verb agrees plural:

| | Familiar singular | Polite singular |
| --- | --- | --- |
| you (m.) | ንስኻ | ንስኹም |
| you (f.) | ንስኺ | ንስኽን |
| he | ንሱ | ንሶም |
| she | ንሳ | ንሰን |

"Default to polite" without this table gets a wordy sentence that is still familiar singular, or a plural verb aimed at one reader with no warning. English "you" also hides gender. The procedure never stops to resolve gender, number, and respect before it translates. That is the decision that most often makes a Tigrinya sentence wrong.

There is also a vocative used to call someone: ኣታ (masculine singular) beside ንስኻ. The skill does not mention it.

### The Latin line has no writing system

Gemination (a doubled consonant) changes meaning. /kʼɐrrɐbɐ/ "he brought forth" and /kʼɐrɐbɐ/ "he came closer" differ only by that doubling. The Geʽez script does not write gemination. A pronunciation guide that does not mark it is not a pronunciation guide.

The file says "clear, consistent Latin" and never picks a system. Vowel letters, ejectives (`t'`, `č'`, `k'`), the pharyngeals ዐ and ሐ, and gemination will drift from answer to answer.

### "Always" three-part output

Every reply must be Tigrinya, then Latin, then notes. That fits a sentence or a short message. For a page of text it doubles the length and invites a note on every line. Long text needs one Tigrinya document, one transliteration only if asked, and notes only for choices that change meaning.

### Church language with no phrase list

"Prefer established ecclesiastical phrasing" sends the model looking for a liturgy it was not given. Much public Tigrinya parallel text is biblical, so models already over-produce that register. The instruction should point at a list. Until that list exists, formal modern Tigrinya is the honest default, with a note that a church term was not supplied.

### Amharic will leak in, and nothing forbids it

Tigrinya and Amharic share the Geʽez script and are both Ethio-Semitic. They are not mutually intelligible. Models mix them. The skill never says to reject Amharic forms. High-value contrasts:

| English | Tigrinya | Amharic form to reject |
| --- | --- | --- |
| I | ኣነ | እኔ |
| he / she | ንሱ / ንሳ | እሱ / እሷ |
| what | እንታይ | ምን |
| he is | እዩ | ነው |
| there is (m.) | ኣሎ | አለ |
| he did not … | ኣይ-…-ን | አል-…-ም |
| the (m.) | እቲ | suffix -u / -ው |
| food | መግቢ | ምግብ |
| water | ማይ | ውሃ |
| house | ገዛ | ቤት |

### Dialect is named and not defined

"Standard Tigrinya as used in Eritrea and northern Ethiopia" treats two large written traditions as one. Asmara school and press Tigrinya and Tigray Tigrinya differ in vocabulary and in some pronouns. The skill should pick one default (written Eritrean Tigrinya is the practical one for a single default) and switch only when the user asks. It should not claim a single academy spelling for ሐ / ኀ / ኸ and the other look-alike letters until a specific orthography book is chosen and followed.

Look-alike letters that must stay consistent inside one document: ሀ ሐ ኀ ኸ, አ ዐ, ሰ ሠ, ጸ ፀ, and the labialized series (ኰ, ጐ, and the rest). ሠ is rare in modern Tigrinya spelling.

### No test set

There is no list of inputs with an expected shape. "Sound natural to a native speaker" cannot be checked from the skill files alone.

## Language facts the next version has to encode

These are the facts behind the gaps above. Sources are at the end.

**Identity.** Tigrinya (ትግርኛ, *təgrəñña*), ISO 639-1 `ti`, ISO 639-3 `tir`. Ethio-Semitic. Spoken in Eritrea and in Ethiopia's Tigray Region, and in the diaspora. Ethnologue's 28th edition, as cited on the English Wikipedia, puts speakers at about 9.9 million (2022–2023). It is not Tigre, and it is not Geʽez.

**Script.** Geʽez abugida, left to right, Unicode block Ethiopic (U+1200). Each letter is a consonant plus a vowel. Modern Tigrinya separates words with spaces. Sentence punctuation uses ። and ፣, and also `?` and `!`.

**Pronouns.** Ten basic forms, plus polite plurals used for one respected person, plus a vocative for calling. Independent pronouns appear when the person is emphasized. Otherwise the verb suffix or prefix carries the subject.

**Verb.** A verb is a root (usually three consonants), a derived stem (simple, passive/reflexive, causative, frequentative, reciprocal), a tense-aspect-mood stem, and a subject conjugation. The four stems are perfect, imperfect, jussive/imperative, and gerundive. Object and prepositional suffixes stack on the end. Auxiliaries (ኣሎ, ነበረ, ኮነ, the copula) build the finer tenses. The skill cannot ship every class. It can ship the agreement endings, the gerundive-as-past rule, negation, the copula, ኣሎ, and a rule to avoid inventing a stem when the root class is uncertain.

**Possession and objects.** Possessive suffixes on the noun (ገዛይ "my house"). Direct-object suffixes on the verb, with a light and a heavy (geminated) variant. ን- on a definite noun phrase for the accusative (ሓጎስ ንኣልማዝ ረኺቡዋ "Hagos met Almaz").

**This skill versus machine translation.** Google Translate, Meta's NLLB-200 (`tir_Ethi`), and smaller Horn of Africa systems already translate this pair. Public parallel text is small next to high-resource pairs, and a large share of it is religious, so untuned output drifts toward church diction or toward Amharic. A skill is useful if it forces the decisions those systems miss: gender of "you", polite plural, gerundive past, definite ን-, and an Amharic filter. It is not useful if it only repeats "be natural".

## Sources

- English Wikipedia, "Tigrinya language" and "Tigrinya grammar", including the personal-pronoun table, the preposition list, and the grammatical-features section. Speaker count via Ethnologue 28 (2025), cited there. Retrieved 13 October 2026.
- English Wikipedia, "Tigrinya verbs": conjugation of ፈለጠ, showing perfect, imperfect, jussive, and gerundive, and the note that laryngeal and semivowel roots deviate. Retrieved 13 October 2026.
- Grok user guide, `08-skills.md`: discovery paths, frontmatter, and the rule that reference files are read only when the skill says to read them.
- Skill package on disk: `SKILL.md`, `references/grammar-notes.md`, `README.md`.

Grammars named by the Wikipedia grammar article, for the later reference pass: Leslau 1941, Amanuel Sahle 1998 *Säwasəw Təgrəñña*, Mason (ed.) 1996, Voigt 1977, Tadross and Abraham Teklu 2015. This review did not re-check every suffix against those books. The plan treats published tables as the source for anything added to `references/`, and treats this review's examples as the ones checked against the Wikipedia conjugation pattern.
