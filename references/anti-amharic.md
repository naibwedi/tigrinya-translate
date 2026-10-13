# Anti-Amharic Leakage Filter

LLMs and machine translation models (such as NLLB) frequently contaminate Tigrinya output with Amharic vocabulary, morphology, and syntax because of shared Geʽez script and higher training data volume for Amharic.

Before finalizing any Tigrinya translation, scan the output and reject every Amharic form listed below.

---

## 1. High-Frequency Lexical Traps

| English | Tigrinya (REQUIRED) | Amharic Leak (STRICTLY FORBIDDEN) | Notes |
| :--- | :--- | :--- | :--- |
| **I** | **ኣነ** (*ane*) | ❌ **እኔ** (*əne*) | Never use *እኔ*. |
| **He / She** | **ንሱ / ንሳ** (*nisu / nisa*) | ❌ **እሱ / እሷ** (*əssu / əsswa*) | Independent 3rd-person pronouns. |
| **They** | **ንሳቶም / ንሳተን** | ❌ **እነሱ** (*ənnäsu*) | |
| **What** | **እንታይ** (*intay*) | ❌ **ምን** (*mən*) | |
| **Where** | **ኣበይ** (*abäy*) | ❌ **የት** (*yät*) | |
| **Why** | **ስለምንታይ** (*səlämən-tay*) | ❌ **ለምን** (*lämən*) | |
| **When** | **መዓስ** (*mä'as*) | ❌ **መቼ** (*mäče*) | |
| **Who** | **መን** (*män*) | ❌ **ማን** (*man*) | |
| **How** | **ከመይ** (*kämäy*) | ❌ **እንዴት** (*əndet*) | |
| **Food / Meal** | **መግቢ** (*mägbi*) | ❌ **ምግብ** (*məgəb*) | |
| **Water** | **ማይ** (*may*) | ❌ **ውሃ** (*wəha*) | |
| **House / Home** | **ገዛ** (*gäza*) | ❌ **ቤት** (*bet*) | *ቤት* in Tigrinya is only used in compounds like *ቤት ትምህርቲ*. |
| **Child** | **ቆልዓ** (*qol'a*) | ❌ **ልጅ** (*ləǧ*) | |
| **Woman** | **ሰበይቲ** (*säbäyti*) | ❌ **ሴት** (*set*) | |
| **Man / Person** | **ሰብኣይ / ሰብ** | ❌ **ወንድ / ሰው** | |
| **Work** | **ዕዮ / ስራሕ** (*'əyo / səraḥ*) | ❌ **ስራ** (*səra*) | Final ḥ (*ሕ*) is retained in Tigrinya *ስራሕ*. |
| **Country** | **ሃገር** (*hagär*) | ❌ **አገር** (*agär*) | Tigrinya uses *ሃ*, not *አ*. |
| **Today** | **ሎሚ** (*lomi*) | ❌ **ዛሬ** (*zare*) | |
| **Yesterday** | **ትማሊ** (*təmali*) | ❌ **ትናንት** (*tənant*) | |
| **Tomorrow** | **ጽባሕ** (*tsəbaḥ*) | ❌ **ነገ** (*nägä*) | |

---

## 2. Copula & Auxiliary Verbs

| Function | Tigrinya (REQUIRED) | Amharic Leak (FORBIDDEN) |
| :--- | :--- | :--- |
| **He is** | **እዩ** (*əyyu*) | ❌ **ነው** (*näw*) |
| **She is** | **እያ** (*əyya*) | ❌ **ነች / ናት** (*näč / nat*) |
| **They are** | **እዮም / እየን** (*əyyom / əyyän*) | ❌ **ናቸው** (*načäw*) |
| **I am** | **እየ** (*əyyä*) | ❌ **ነኝ** (*nəñ*) |
| **You are (m)** | **ኢኻ** (*ixa*) | ❌ **ነህ** (*näh*) |
| **You are (f)** | **ኢኺ** (*ixi*) | ❌ **ነሽ** (*näš*) |
| **There is (existence)** | **ኣሎ** (*alo*) | ❌ **አለ** (*allä*) |
| **There is not** | **የልቦን / የለን** (*yälbon / yälän*) | ❌ **የለም** (*yälläm*) |

---

## 3. Morphological & Affix Traps

1. **Main Clause Negation:**
   - Tigrinya: **ኣይ-…-ን** (e.g. *ኣይከደን* - he did not go).
   - Reject Amharic: ❌ **አል-…-ም** (*አልሄደም*).
2. **Definite Direct Object:**
   - Tigrinya: Prefix **ን-** + article (**ነቲ** masc., **ነታ** fem., **ነቶም** pl. masc., **ነተን** pl. fem.).
   - Reject Amharic: ❌ Suffix **-u / -ው** or standalone *-(i)n* accusative (e.g. *ቤቱን*).
3. **Plural Marker:**
   - Tigrinya: Broken plurals or suffixes like **-ታት** (*-tat*), **-ቲ** (*-ti*).
   - Reject Amharic: ❌ **-ዎች** (*-oč*). E.g. Tigrinya *መጻሕፍቲ* or *ደብተርታት*; reject ❌ *ደብተሮች*.
4. **Possessive Suffix (3rd Person Singular Masc.):**
   - Tigrinya: **-ኡ** (*-u*) (e.g. *ገዝኡ* - his house, *ስሙ* - his name).
   - Reject Amharic: ❌ **-ው** (*-w*) on vowel stems or *የእሱ*.
