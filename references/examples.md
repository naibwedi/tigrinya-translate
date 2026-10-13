# Benchmark Translation Examples & Evaluation Set

This document serves as the human test set and benchmark reference for evaluating English ↔ Tigrinya translations.

Every item documents the decision, the verified Tigrinya text, the Latin transliteration with gemination, and the grammatical rationale.

---

## The 15 Benchmark Evaluation Pairs

### 1. "I ate the food."
* **Tigrinya:** **ነቲ መግቢ በሊዐ።**
* **Latin:** *näti mägbi bäliʿä.*
* **Verification Criteria:**
  * Pro-drop: No independent pronoun **ኣነ** (subject is fully marked on the verb).
  * Direct Object: Definite accusative **ነቲ** (*ን-* + *እቲ*). Noun is **መግቢ** (meal/food), never *እኽሊ* (grain/crops) or Amharic *ምግብ*.
  * Past Tense: Standard 1st person singular gerundive ends in 1st-order **ዐ** (**በሊዐ**), never 5th-order *በሊዔ*.

---

### 2. "She ate the food."
* **Tigrinya:** **ነቲ መግቢ በሊዓ።**
* **Latin:** *näti mägbi bäliʿa.*
* **Verification Criteria:**
  * Feminine 3rd-person singular gerundive **በሊዓ** (*bäliʿa*).
  * Definite object marker **ነቲ** consistent with masculine gender of *መግቢ*.

---

### 3. "Did you see my sister?"
* **Tigrinya (to female friend):** **ንሓፍተይ ርኢኺያዶ፧**
  * *Latin:* *nə-ḥaftäy rəʾixiyyado?*
* **Tigrinya (to male friend):** **ንሓፍተይ ርኢኻያዶ፧**
  * *Latin:* *nə-ḥaftäy rəʾixayyado?*
* **Verification Criteria:**
  * Definite direct object takes prefix **ን-** (*ንሓፍተይ*).
  * Possessive 1st-person suffix on noun (*-ይ*).
  * Feminine direct object suffix on verb (*-ያ* referring to sister).
  * Yes/no question marker **-ዶ**.

---

### 4. "Please sit down." (to a respected man / elder)
* **Tigrinya:** **ኮፍ በሉ፤** (or **ተቐመጡ።**)
* **Latin:** *kof bälu.* (or *täqämäṭu.*)
* **Verification Criteria:**
  * Plural polite agreement (**በሉ** / **ተቐመጡ**) addressing a single individual with honorific respect.
  * Explicitly noted as polite register.

---

### 5. "Please sit down." (to a female friend)
* **Tigrinya:** **ኮፍ በሊ።**
* **Latin:** *kof bäli.*
* **Verification Criteria:**
  * Feminine singular imperative ending in 3rd-order **ሊ** (**በሊ**).
  * Familiar peer register.

---

### 6. "I do not know."
* **Tigrinya:** **ኣይፈልጥን እየ።**
* **Latin:** *ay-fälləṭən əyyä.*
* **Verification Criteria:**
  * Negative circumfix **ኣይ-…-ን** on imperfective verb + auxiliary copula **እየ**.
  * No independent pronoun **ኣነ**. Reject Amharic *አላውቅም*.

---

### 7. "the man who ate"
* **Tigrinya:** **ዝበልዐ ሰብኣይ።**
* **Latin:** *zə-bälʿä säbʾay.*
* **Verification Criteria:**
  * Relative clause prefix **ዝ-** (*zə-*) attached to verb preceding head noun *ሰብኣይ*.

---

### 8. "Hagos met Almaz."
* **Tigrinya:** **ሓጎስ ንኣልማዝ ረኺቡዋ።**
* **Latin:** *ḥagos nə-almaz räxibuwa.*
* **Verification Criteria:**
  * Strict SOV word order: Subject (ሓጎስ) – Object (ንኣልማዝ) – Verb (ረኺቡዋ).
  * Definite proper noun object marked with **ን-** (*ንኣልማዝ*).
  * Verb incorporates 3rd-person feminine object suffix **-ዋ** (*-wa*).

---

### 9. "I have a house."
* **Tigrinya:** **ገዛ ኣሎኒ።**
* **Latin:** *gäza aloni.*
* **Verification Criteria:**
  * Tigrinya house is **ገዛ**, never standalone Amharic *ቤት*.
  * Possession expressed via **ኣሎ** + 1st-person object suffix **-ኒ** (*ኣሎኒ*).

---

### 10. "He is Eritrean."
* **Tigrinya:** **ኤርትራዊ እዩ።**
* **Latin:** *ertrawi əyyu.*
* **Verification Criteria:**
  * Copula is Tigrinya **እዩ**, never Amharic *ነው*.
  * Pro-drop: Subject pronoun *ንሱ* is omitted in neutral statements.

---

### 11. "There is no water."
* **Tigrinya:** **ማይ የልቦን።** (or **ማይ የለን።**)
* **Latin:** *may yälbon.* (or *may yälän.*)
* **Verification Criteria:**
  * Water is **ማይ**, never Amharic *ውሃ*.
  * Negative existence is **የልቦን** or **የለን**, never Amharic *የለም*.

---

### 12. "Come in and sit down." (to male peer)
* **Tigrinya:** **ኣቲኻ ኮፍ በል。**
* **Latin:** *atixa kof bäl.*
* **Verification Criteria:**
  * Sequential actions chained using masculine gerundive **ኣቲኻ** (*atixa*), NOT an English conjunction *እሞ* or *-ን*.
  * Concluding verb is imperative **በል**.

---

### 13. "Piece of cake." (Idiom)
* **Tigrinya:** **ቀሊል ነገር።** (or authentic idiom: **ማይ ምስታይ እዩ።**)
* **Latin:** *qälil nägär.* (or *may məstay əyyu.*)
* **Verification Criteria:**
  * Conceptual equivalent ("easy thing" or "like drinking water").
  * Absolute rejection of word-for-word calques like *ቁራጽ ኬክ*.

---

### 14. Multi-Sentence Paragraph (Consistency Benchmark)
* **Rule:** Maintain identical addressee register, pronoun perspective, and vocabulary choices across the entire paragraph.
* **Latin Transliteration:** Omitted for extended prose unless explicitly requested by the user.

---

### 15. Reverse Translation: "ነቲ መግቢ በሊዐ።"
* **English Output:** *"I ate the food."*
* **Linguistic Note:**
  * Explicitly note in the output that the Tigrinya source is pro-drop (subject "I" is indicated entirely by the verb inflection *በሊዐ*, without an independent pronoun *ኣነ*).
