#!/usr/bin/env python3
"""
Tigrinya Translation Quality & Linguistic Audit Tool
Version 2.0.0 (Grammarly-Style Expanded Engine)

Validates Tigrinya text against morphological, orthographic, and anti-leakage rules:
1. Anti-Amharic intrusion filter (checks against forbidden Amharic lexemes and morphemes)
2. Geʽez punctuation validation (checks for ።, ፣, ፤, ፦, ፧ instead of Latin punctuation)
3. AI-tell dashes & typography (flags --, —, prose -, stray colons, spacing before Geʽez marks)
4. Sacred name orthography (ensures Jesus is spelled strictly as ኢየሱስ)
5. Controlled ecclesiastical house-style spellings
6. Negative-verb morphology filter (flags '*ኣይድወንን' blend and verifies '-ንን' endings)
7. Approved bilingual parenthetical glosses vs. unapproved Latin residue
8. Pro-drop & accusative checks (flags redundant 'ኣነ' and checks 'ነቲ/ነታ')
9. Deterministic auto-fixing (fix_deterministic)
10. Gemini AI Deep Grammar & SOV checker (urllib.request zero-dep)
"""

import sys
import os
import re
import json
import argparse
import urllib.request
import urllib.error
from typing import List, Dict, Any, Tuple, Optional

# Ensure stdout handles UTF-8 on all platforms
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Geʽez punctuation characters
PUNCT_CHARS = "።፣፤፦፧፨.!?,;:\"'()«»[]"

# Ethiopic fidel (letters) character class, strictly excluding punctuation (U+1360-U+1368) and digits (U+1369-U+137C)
FIDEL_CHAR = r"[\u1200-\u135A\u1380-\u139F\u2D80-\u2DDF\uAB00-\uAB2F]"
NOT_FIDEL_PRE = rf"(?<!{FIDEL_CHAR})"
NOT_FIDEL_POST = rf"(?!{FIDEL_CHAR})"

# 1. High-frequency Amharic tokens to reject & their Tigrinya replacements
PROHIBITED_AMHARIC: Dict[str, str] = {
    "እኔ": "Use Tigrinya 'ኣነ' (or drop if subject is unemphasized)",
    "እሱ": "Use Tigrinya 'ንሱ'",
    "እሷ": "Use Tigrinya 'ንሳ'",
    "እነሱ": "Use Tigrinya 'ንሳቶም' (m) / 'ንሳተን' (f)",
    "ምን": "Use Tigrinya 'እንታይ'",
    "የት": "Use Tigrinya 'ኣበይ'",
    "ለምን": "Use Tigrinya 'ስለምንታይ'",
    "መቼ": "Use Tigrinya 'መዓስ'",
    "ማን": "Use Tigrinya 'መን'",
    "እንዴት": "Use Tigrinya 'ከመይ'",
    "ምግብ": "Use Tigrinya 'መግቢ'",
    "ውሃ": "Use Tigrinya 'ማይ'",
    "ልጅ": "Use Tigrinya 'ቆልዓ' (child) or 'ወዲ' (boy/son)",
    "ሴት": "Use Tigrinya 'ሰበይቲ' (woman) or 'ጓል' (girl)",
    "ሰው": "Use Tigrinya 'ሰብ'",
    "ሰውዬ": "Use Tigrinya 'እቲ ሰብኣይ'",
    "ይህ": "Use Tigrinya 'እዚ'",
    "ይህን": "Use Tigrinya 'ነዚ'",
    "ይህች": "Use Tigrinya 'እዚኣ'",
    "ያ": "Use Tigrinya 'እቲ'",
    "ዛሬ": "Use Tigrinya 'ሎሚ'",
    "ትናንት": "Use Tigrinya 'ትማሊ'",
    "ነገ": "Use Tigrinya 'ጽባሕ'",
    "ነው": "Use Tigrinya copula 'እዩ'",
    "ነች": "Use Tigrinya copula 'እያ'",
    "ናት": "Use Tigrinya copula 'እያ'",
    "ናቸው": "Use Tigrinya copula 'እዮም' / 'እየን'",
    "ነኝ": "Use Tigrinya copula 'እየ'",
    "ነህ": "Use Tigrinya copula 'ኢኻ'",
    "ነሽ": "Use Tigrinya copula 'ኢኺ'",
    "የለም": "Use Tigrinya 'የልቦን' or 'የለን'",
}

AMHARIC_REPLACEMENTS: Dict[str, str] = {
    "እኔ": "ኣነ",
    "እሱ": "ንሱ",
    "እሷ": "ንሳ",
    "እነሱ": "ንሳቶም",
    "ምን": "እንታይ",
    "የት": "ኣበይ",
    "ለምን": "ስለምንታይ",
    "መቼ": "መዓስ",
    "ማን": "መን",
    "እንዴት": "ከመይ",
    "ምግብ": "መግቢ",
    "ውሃ": "ማይ",
    "ልጅ": "ቆልዓ",
    "ሴት": "ሰበይቲ",
    "ሰው": "ሰብ",
    "ሰውዬ": "እቲ ሰብኣይ",
    "ይህ": "እዚ",
    "ይህን": "ነዚ",
    "ይህች": "እዚኣ",
    "ያ": "እቲ",
    "ዛሬ": "ሎሚ",
    "ትናንት": "ትማሊ",
    "ነገ": "ጽባሕ",
    "ነው": "እዩ",
    "ነች": "እያ",
    "ናት": "እያ",
    "ናቸው": "እዮም",
    "ነኝ": "እየ",
    "ነህ": "ኢኻ",
    "ነሽ": "ኢኺ",
    "የለም": "የለን",
}

# Regex patterns for morphological intrusions
AMHARIC_PATTERNS = [
    (re.compile(r"\bአል[^\s]+ም\b"), "Amharic negative circumfix 'አል-…-ም'; use Tigrinya 'ኣይ-…-ን'", "amharic_negative_circumfix"),
    (re.compile(r"[^\s]+ዎች\b"), "Amharic plural suffix '-ዎች'; use Tigrinya broken plurals or '-ታት'", "amharic_plural_suffix"),
    (re.compile(r"\bቤት(?!\s*ትምህርቲ|\s*ክርስቲያን|\s*መጻሕፍቲ|\s*ፍርዲ)\b"), "Standalone Amharic 'ቤት'; use Tigrinya 'ገዛ' for home/house", "amharic_standalone_bet"),
    (re.compile(r"\bአገር\b"), "Amharic 'አገር'; use Tigrinya 'ሃገር'", "amharic_ager"),
]

# 2. Controlled ecclesiastical house-style spellings
DEPRECATED_HOUSE_STYLE: Dict[str, str] = {
    "ህይወት": "ሕይወት",
    "ምስዋእት": "መሥዋዕት",
    "መስዋእት": "መሥዋዕት",
    "መስዋእቲ": "መሥዋዕት",
    "ነብያት": "ነቢያት",
    "ቤተ ክርስትያን": "ቤተ ክርስቲያን",
    "ሰለስተ": "ሠለስተ",
    "ስልጣን": "ሥልጣን",
    "ምስጢር": "ምሥጢር",
    "መሰረት": "መሠረት",
    "ስምረት": "ሥምረት",
    "ድሕነት": "ድኅነት",
    "ሓጢኣት": "ኃጢኣት",
    "ግዜ": "ጊዜ",
    "ኮከብ": "ኰከብ",
    "ኮኾብ": "ኰከብ",
}

# 3. Forbidden morphological blends
FORBIDDEN_MORPHOLOGICAL_BLENDS: Dict[str, str] = {
    "ኣይድወንን": "Morphological blend of 'ደው ኣይብልን' (does not stop) and 'ኣይውሰንን' (is not limited/bounded). Disambiguate by context.",
}

# Valid root-final -ን negative verbs
VALID_DOUBLE_N_NEGATIVES = {
    "ኣይስእንን", "ኣይውሰንን", "ኣይድህንን", "ኣይሕዘንን", "ኣይኮነንን",
    "ኣይኣምንን", "ኣይምስገንን", "ኣይፈጠንን", "ኣይፈልጡንን", "ኣይረኸብኩምንን",
    "ኣይሓደገንን", "ኣይሃበንን", "ኣይተኻእለንን", "ኣይተፈቕደንን", "ኣይተዋህበንን",
    "ኣይርከበንን", "ኣይቅበለንን", "ኣይፍለጥንን", "ኣይዝንጋዕንን", "ኣይጥቀምንን",
    "ኣይቀረበንን", "ኣይፈርሀንን", "ኣይጠፍእንን", "ኣይዓገበንን", "ኣይኽእልንን",
}

# Approved Latin transliterations, scholarly citations, and bilingual patristic glosses
APPROVED_LATIN_PATTERNS = [
    re.compile(r"\bG\.?\s*H\.?\s*Box\b", re.IGNORECASE),
    re.compile(r"\bG\.?\s*G\.?\s*Boy\b", re.IGNORECASE),
    re.compile(r"\bJames\s+Strong\b", re.IGNORECASE),
    re.compile(r"[\"“]Greek Dictionary of the New Testament[\"”]", re.IGNORECASE),
    re.compile(
        r"\((?:St\.|Father|Bishop)?\s*(?:Jerome|John Chrysostom|Augustine|Hilary of Poitiers|Hilary|"
        r"Jacob of Serugh|Gregory the Great|Gregory of Nazianzus|Gregory of Nyssa|Cyril of Jerusalem|"
        r"Origen|Ambrose|Cyprian|John Climacus|John Cassian|Ignatius|John of Kronstadt|Didascalia|"
        r"Philoxenus|Eusebius of Caesarea|Anthony the Great|Gnostics|Essenes|Lex Talionis|Sanhedrin|"
        r"epiousios|ousia|epienai|epiousa|epi|eimi|paraggelia|Corban|Almah|Tu es Petrus|Tu es Petra|"
        r"Eli, Eli, lema sabachthani|phylacteries|proselytes|anti-Christ|Mammon)\)",
        re.IGNORECASE,
    ),
]


def clean_tokens(text: str) -> List[str]:
    """Extract words without punctuation."""
    raw_tokens = text.split()
    tokens = []
    for t in raw_tokens:
        cleaned = t.strip(PUNCT_CHARS)
        if cleaned:
            tokens.append(cleaned)
    return tokens


def get_protected_spans(text: str) -> List[Tuple[int, int]]:
    """
    Find spans that must NEVER be treated as AI dashes:
    1. Numeric chapter/verse ranges (e.g. 1-9, 21–28, 13:31-32)
    2. Compound Tigrinya words (e.g. ስነ-ምግባር, ቤተ-መቕደስ, ቅድመ-ዓለም)
    3. Negative prefixes (e.g. ዘይ-ተፈልጠ)
    4. Leading quote bullets (+ at line start)
    """
    spans: List[Tuple[int, int]] = []

    # 1. Numeric ranges: digits + hyphen/dash + digits
    for m in re.finditer(r"\b\d+\s*[-–—]\s*\d+\b", text):
        spans.append((m.start(), m.end()))

    # 2. Compound Tigrinya words: Geʽez letters - Geʽez letters
    for m in re.finditer(rf"{FIDEL_CHAR}+-{FIDEL_CHAR}+", text):
        spans.append((m.start(), m.end()))

    # 3. Negative prefixes: \bዘይ-Geʽez
    for m in re.finditer(rf"\bዘይ-{FIDEL_CHAR}+", text):
        spans.append((m.start(), m.end()))

    # 4. Leading plus bullets: ^\+\s+
    for m in re.finditer(r"^\+\s+", text, re.MULTILINE):
        spans.append((m.start(), m.end()))

    return spans


def is_span_protected(start: int, end: int, protected_spans: List[Tuple[int, int]]) -> bool:
    """Check if [start, end) intersects with any protected span."""
    for p_start, p_end in protected_spans:
        if not (end <= p_start or start >= p_end):
            return True
    return False


def extract_latin_residue(text: str) -> List[Tuple[int, int, str]]:
    """Find unapproved Latin words of 2 or more letters with character offsets."""
    mask = list(text)
    for pat in APPROVED_LATIN_PATTERNS:
        for m in pat.finditer(text):
            for i in range(m.start(), m.end()):
                mask[i] = " "
    masked_text = "".join(mask)

    residue: List[Tuple[int, int, str]] = []
    for m in re.finditer(r"[A-Za-z]{2,}", masked_text):
        residue.append((m.start(), m.end(), m.group(0)))
    return residue


def find_gemini_api_key(explicit_key: Optional[str] = None) -> Optional[str]:
    r"""
    Discover GEMINI_API_KEY from:
    1. Explicit function argument
    2. os.environ['GEMINI_API_KEY']
    3. .env.local / .env in current directory
    4. .env.local / .env in script parent directories
    5. Peer project c:\Users\naibm\Documents\projects\tigrinya-catena\.env.local
    """
    if explicit_key and explicit_key.strip():
        return explicit_key.strip()

    if os.environ.get("GEMINI_API_KEY"):
        val = os.environ.get("GEMINI_API_KEY", "").strip()
        if val:
            return val

    candidates = [
        os.path.join(os.getcwd(), ".env.local"),
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.path.dirname(__file__), "..", ".env.local"),
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        r"c:\Users\naibm\Documents\projects\tigrinya-catena\.env.local",
        r"c:\Users\naibm\Documents\projects\tigrinya-catena\.env",
    ]

    for p in candidates:
        if os.path.isfile(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY="):
                            key = line.split("=", 1)[1].strip().strip("\"'")
                            if key:
                                return key
            except Exception:
                pass

    return None


def calculate_score(
    issues: List[Dict[str, Any]],
    warnings: List[Dict[str, Any]],
    suggestions: List[Dict[str, Any]]
) -> int:
    """
    Writing Quality Score (0-100) using category-weighted deductions:
    - anti_amharic error: -10
    - grammar_sov error: -10
    - theological_glossary error: -8
    - punctuation_ai error: -5
    - orthography_house_style error: -5
    - warning: -4
    - suggestion: -2
    """
    score = 100
    for iss in issues:
        cat = iss.get("category", "")
        if cat in ("anti_amharic", "grammar_sov"):
            score -= 10
        elif cat == "theological_glossary":
            score -= 8
        elif cat in ("punctuation_ai", "orthography_house_style"):
            score -= 5
        else:
            score -= 5

    for w in warnings:
        score -= 4

    for s in suggestions:
        score -= 2

    return max(0, min(100, score))


def audit_tigrinya(text: str, strict: bool = True) -> Dict[str, Any]:
    """
    Comprehensive linguistic audit of Tigrinya text.
    Returns structured findings with exact character offsets, categories,
    severities, replacements, and rule IDs.
    """
    raw_findings: List[Dict[str, Any]] = []
    protected_spans = get_protected_spans(text)

    # 1. Prohibited Amharic vocabulary (anti_amharic)
    for word, reason in PROHIBITED_AMHARIC.items():
        pattern = re.compile(rf"{NOT_FIDEL_PRE}{re.escape(word)}{NOT_FIDEL_POST}")
        for m in pattern.finditer(text):
            rep = AMHARIC_REPLACEMENTS.get(word)
            raw_findings.append({
                "start": m.start(),
                "end": m.end(),
                "category": "anti_amharic",
                "severity": "error",
                "matched": m.group(0),
                "replacement": rep,
                "message": f"Forbidden Amharic token '{word}'. {reason}.",
                "rule_id": f"amharic_token_{word}",
                "deterministic": True,
                "type": "AMHARIC_LEAKAGE",
            })

    # 2. Amharic morphological patterns (anti_amharic)
    for pattern, reason, rule_id in AMHARIC_PATTERNS:
        for m in pattern.finditer(text):
            rep = None
            if rule_id == "amharic_standalone_bet":
                rep = "ገዛ"
            elif rule_id == "amharic_ager":
                rep = "ሃገር"
            raw_findings.append({
                "start": m.start(),
                "end": m.end(),
                "category": "anti_amharic",
                "severity": "error",
                "matched": m.group(0),
                "replacement": rep,
                "message": f"Amharic morphology in '{m.group(0)}': {reason}.",
                "rule_id": rule_id,
                "deterministic": rep is not None,
                "type": "AMHARIC_MORPHOLOGY",
            })

    # 3. Sacred orthography (orthography_house_style)
    jesus_pattern = re.compile(rf"{NOT_FIDEL_PRE}የሱስ{NOT_FIDEL_POST}")
    for m in jesus_pattern.finditer(text):
        raw_findings.append({
            "start": m.start(),
            "end": m.end(),
            "category": "orthography_house_style",
            "severity": "error",
            "matched": m.group(0),
            "replacement": "ኢየሱስ",
            "message": "Sacred name misspelled as 'የሱስ'. Tigrinya requires 'ኢየሱስ'.",
            "rule_id": "sacred_name_jesus",
            "deterministic": True,
            "type": "SACRED_ORTHOGRAPHY",
        })

    # 4. Controlled ecclesiastical house-style spellings (orthography_house_style)
    for deprecated, canonical in DEPRECATED_HOUSE_STYLE.items():
        pattern = re.compile(rf"{NOT_FIDEL_PRE}{re.escape(deprecated)}{NOT_FIDEL_POST}")
        for m in pattern.finditer(text):
            raw_findings.append({
                "start": m.start(),
                "end": m.end(),
                "category": "orthography_house_style",
                "severity": "error",
                "matched": m.group(0),
                "replacement": canonical,
                "message": f"Deprecated house-style form '{deprecated}'. Use '{canonical}'.",
                "rule_id": f"house_style_{deprecated}",
                "deterministic": True,
                "type": "HOUSE_STYLE",
            })

    # 5. Forbidden morphological blends (orthography_house_style / grammar_sov)
    for blend, reason in FORBIDDEN_MORPHOLOGICAL_BLENDS.items():
        pattern = re.compile(rf"{NOT_FIDEL_PRE}{re.escape(blend)}{NOT_FIDEL_POST}")
        for m in pattern.finditer(text):
            rep = "ደው ኣይብልን" if ("ጥራይ" in text or "ደው" in text) else ("ኣይውሰንን" if ("ቦታ" in text or "ጊዜ" in text) else "ደው ኣይብልን")
            raw_findings.append({
                "start": m.start(),
                "end": m.end(),
                "category": "orthography_house_style",
                "severity": "error",
                "matched": m.group(0),
                "replacement": rep,
                "message": f"Invalid verb form '{blend}': {reason}",
                "rule_id": "morphological_blend_aydiwennin",
                "deterministic": True,
                "type": "MORPHOLOGICAL_BLEND",
            })

    # 6. Spacing before Geʽez punctuation (punctuation_ai)
    for m in re.finditer(r"[ \t]+([።፣፤፦፧፨])", text):
        raw_findings.append({
            "start": m.start(),
            "end": m.end(),
            "category": "punctuation_ai",
            "severity": "error",
            "matched": m.group(0),
            "replacement": m.group(1),
            "message": f"Found space immediately before Geʽez punctuation '{m.group(1)}'. Geʽez punctuation must not have leading spaces.",
            "rule_id": "pre_punctuation_space",
            "deterministic": True,
            "type": "PUNCTUATION_ERROR",
        })

    # 7. Missing space after Geʽez punctuation when followed by Geʽez word (punctuation_ai)
    for m in re.finditer(r"([።፣፤፦፧])([\u1200-\u137F])", text):
        raw_findings.append({
            "start": m.start(),
            "end": m.end(),
            "category": "punctuation_ai",
            "severity": "warning",
            "matched": m.group(0),
            "replacement": f"{m.group(1)} {m.group(2)}",
            "message": f"Missing space after Geʽez punctuation '{m.group(1)}' before word '{m.group(2)}'.",
            "rule_id": "missing_post_punctuation_space",
            "deterministic": True,
            "type": "PUNCTUATION",
        })

    # 8. Stray Latin punctuation in Geʽez prose (punctuation_ai)
    # 8a. Latin question mark after Geʽez word
    for m in re.finditer(rf"(?<={FIDEL_CHAR})\s*\?", text):
        raw_findings.append({
            "start": m.start(),
            "end": m.end(),
            "category": "punctuation_ai",
            "severity": "error" if strict else "warning",
            "matched": m.group(0),
            "replacement": "፧",
            "message": "Found Latin question mark '?' after Geʽez text. Use '፧' (ሕቶ ነጥቢ).",
            "rule_id": "latin_question_mark",
            "deterministic": True,
            "type": "PUNCTUATION_ERROR" if strict else "PUNCTUATION",
        })

    # 8b. Latin comma after Geʽez word
    for m in re.finditer(rf"(?<={FIDEL_CHAR})\s*,(?!\d)", text):
        raw_findings.append({
            "start": m.start(),
            "end": m.end(),
            "category": "punctuation_ai",
            "severity": "error" if strict else "warning",
            "matched": m.group(0),
            "replacement": "፣ ",
            "message": "Found Latin comma ',' after Geʽez text. Use '፣' (ንኡስ ነጥቢ).",
            "rule_id": "latin_comma",
            "deterministic": True,
            "type": "PUNCTUATION_ERROR" if strict else "PUNCTUATION",
        })

    # 8c. Latin period after Geʽez word (excluding single-fidel outline markers like ሀ., ለ.)
    for m in re.finditer(rf"({FIDEL_CHAR}{{2,}})(\s*\.)(?!\d)", text):
        raw_findings.append({
            "start": m.start(2),
            "end": m.end(2),
            "category": "punctuation_ai",
            "severity": "error" if strict else "warning",
            "matched": m.group(2),
            "replacement": "።",
            "message": "Found Latin period '.' after Geʽez text. Use '።' (ዓራት ነጥቢ).",
            "rule_id": "latin_period",
            "deterministic": True,
            "type": "PUNCTUATION_ERROR" if strict else "PUNCTUATION",
        })

    # 8d. Latin colon in verse/citation numbers: e.g. 6:1 -> 6፡1
    for m in re.finditer(r"\b(\d+)\s*:\s*(\d+)(?!\d)", text):
        raw_findings.append({
            "start": m.start(),
            "end": m.end(),
            "category": "punctuation_ai",
            "severity": "error",
            "matched": m.group(0),
            "replacement": f"{m.group(1)}፡{m.group(2)}",
            "message": f"Found Latin colon ':' in verse citation '{m.group(0)}'. Use Geʽez two-dots '፡'.",
            "rule_id": "latin_colon_verse",
            "deterministic": True,
            "type": "PUNCTUATION_ERROR",
        })

    # 8e. Latin colon between Geʽez words: e.g. በለ: ኣነ -> በለ፦ ኣነ
    for m in re.finditer(rf"(?<={FIDEL_CHAR})\s*:\s*(?={FIDEL_CHAR})", text):
        raw_findings.append({
            "start": m.start(),
            "end": m.end(),
            "category": "punctuation_ai",
            "severity": "error",
            "matched": m.group(0),
            "replacement": "፦ ",
            "message": "Found Latin colon ':' between Geʽez words. Use Geʽez preface colon '፦ '.",
            "rule_id": "latin_colon_prose",
            "deterministic": True,
            "type": "PUNCTUATION_ERROR",
        })

    # 9. AI Dashes in Prose (punctuation_ai)
    # Detect double/triple dashes (--), em-dashes (—), prose en-dashes (–), and prose spaced hyphens ( - )
    # While strictly protecting numeric ranges, compounds, negative prefixes, and bullets
    dash_candidates = [
        (re.compile(r"\s*--+\s*"), "ai_double_dash", "፦ "),
        (re.compile(r"\s*—\s*"), "ai_em_dash", "፦ "),
        (re.compile(r"(?<!\d)\s*–\s*(?!\d)"), "ai_en_dash", "፤ "),
        (re.compile(r"(?<!\d)\s+-\s+(?!\d)"), "ai_spaced_hyphen", "፤ "),
    ]

    for pat, rule_id, default_rep in dash_candidates:
        for m in pat.finditer(text):
            if is_span_protected(m.start(), m.end(), protected_spans):
                continue
            # Determine appropriate Geʽez punctuation replacement
            # Check context: if preceding quote/speech verb or followed by quote/speech verb
            pre_context = text[max(0, m.start() - 25):m.start()]
            post_context = text[m.end():min(len(text), m.end() + 25)]
            is_speech = any(k in pre_context for k in ("በለ", "ይብል", "ከምዚ", "ይትረጎም")) or any(k in post_context for k in ("“", "‘", "‹", "\"", "ከምዚ", "በለ"))
            rep = "፦ " if is_speech else default_rep

            raw_findings.append({
                "start": m.start(),
                "end": m.end(),
                "category": "punctuation_ai",
                "severity": "error",
                "matched": m.group(0),
                "replacement": rep,
                "message": f"Found AI-generated prose dash '{m.group(0)}'. Replace with Geʽez punctuation ('{rep.strip()}').",
                "rule_id": "ai_dash_prose",
                "deterministic": True,
                "type": "PUNCTUATION_ERROR",
            })

    # 10. Suspicious double -ንን negative endings review (grammar_sov)
    tokens = clean_tokens(text)
    for word in tokens:
        if word.startswith("ኣይ") and word.endswith("ንን") and word not in VALID_DOUBLE_N_NEGATIVES and word not in FORBIDDEN_MORPHOLOGICAL_BLENDS:
            m = re.search(rf"(?<![\u1200-\u137F]){re.escape(word)}(?![\u1200-\u137F])", text)
            start = m.start() if m else 0
            end = m.end() if m else len(word)
            raw_findings.append({
                "start": start,
                "end": end,
                "category": "grammar_sov",
                "severity": "warning",
                "matched": word,
                "replacement": None,
                "message": f"Double '-ንን' negative verb '{word}' detected. Verify that the root ends in '-ን' or carries a '-ኒ/-አን' object suffix.",
                "rule_id": "negative_ending_review",
                "deterministic": False,
                "type": "NEGATIVE_ENDING_REVIEW",
            })

    # 11. Unapproved Latin residue (theological_glossary)
    residue_list = extract_latin_residue(text)
    if residue_list and "contrasted" not in text.lower():
        for r_start, r_end, word in residue_list:
            raw_findings.append({
                "start": r_start,
                "end": r_end,
                "category": "theological_glossary",
                "severity": "error",
                "matched": word,
                "replacement": None,
                "message": f"Unapproved Latin/English residue '{word}' inside Tigrinya prose. Localize Scripture citations or use approved bilingual parenthetical format.",
                "rule_id": "unapproved_latin_residue",
                "deterministic": False,
                "type": "LATIN_RESIDUE",
            })

    # 12. Pro-drop heuristic (grammar_sov)
    pro_drop_match = re.search(r"\b(ኣነ)\b.*[ኩዐ]\b", text)
    if pro_drop_match and "contrasted" not in text.lower():
        m_start = pro_drop_match.start(1)
        m_end = pro_drop_match.end(1)
        raw_findings.append({
            "start": m_start,
            "end": m_end,
            "category": "grammar_sov",
            "severity": "suggestion" if not strict else "warning",
            "matched": "ኣነ",
            "replacement": "",
            "message": "Unemphasized 'ኣነ' detected. In neutral Tigrinya, drop independent pronouns (pro-drop).",
            "rule_id": "pro_drop_redundant_subject",
            "deterministic": False,
            "type": "PRO_DROP_NOTE",
        })

    # Sort findings by start offset ascending, and deduplicate identical/overlapping spans
    raw_findings.sort(key=lambda x: (x["start"], -x["end"]))
    seen_spans = set()
    deduped_findings: List[Dict[str, Any]] = []
    last_end = -1
    for f in raw_findings:
        span_key = (f["start"], f["end"], f["rule_id"])
        if span_key in seen_spans:
            continue
        seen_spans.add(span_key)
        if f["start"] < last_end:
            continue
        deduped_findings.append(f)
        last_end = f["end"]

    # Segregate into issues (error), warnings, and suggestions
    issues = [f for f in deduped_findings if f["severity"] == "error"]
    warnings = [f for f in deduped_findings if f["severity"] == "warning"]
    suggestions = [f for f in deduped_findings if f["severity"] == "suggestion"]

    score = calculate_score(issues, warnings, suggestions)
    passed = len(issues) == 0

    return {
        "passed": passed,
        "score": score,
        "issue_count": len(issues),
        "warning_count": len(warnings),
        "suggestion_count": len(suggestions),
        "issues": issues,
        "warnings": warnings,
        "suggestions": suggestions,
        "all_findings": deduped_findings,
    }


def fix_deterministic(text: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Applies all deterministic fixes to text in a safe, multi-stage pipeline:
    1. Pre-punctuation and post-punctuation spacing
    2. Stray Latin colons, question marks, commas, and periods
    3. AI dashes (--+, —, prose –, prose -) with protection of verse ranges, compounds, & prefixes
    4. Sacred name 'ኢየሱስ' & controlled house style
    5. Prohibited Amharic 1:1 vocabulary tokens
    6. Contextual resolution of '*ኣይድወንን'
    Returns (fixed_text, list_of_applied_fixes).
    """
    applied_fixes: List[Dict[str, Any]] = []
    current_text = text

    # Step 1: Fix spacing before Geʽez punctuation marks
    def _fix_pre_punct_space(m):
        punct = m.group(1)
        applied_fixes.append({
            "start": m.start(),
            "end": m.end(),
            "matched": m.group(0),
            "replacement": punct,
            "rule_id": "pre_punctuation_space",
        })
        return punct

    current_text = re.sub(r"[ \t]+([።፣፤፦፧፨])", _fix_pre_punct_space, current_text)

    # Step 2: Fix missing space after Geʽez punctuation marks before words
    def _fix_missing_post_punct(m):
        punct = m.group(1)
        word_char = m.group(2)
        rep = f"{punct} {word_char}"
        applied_fixes.append({
            "start": m.start(),
            "end": m.end(),
            "matched": m.group(0),
            "replacement": rep,
            "rule_id": "missing_post_punctuation_space",
        })
        return rep

    current_text = re.sub(r"([።፣፤፦፧])([\u1200-\u137F])", _fix_missing_post_punct, current_text)

    # Step 3: Stray Latin colons
    # 3a. Verse citations: 6:1 -> 6፡1
    def _fix_latin_colon_verse(m):
        rep = f"{m.group(1)}፡{m.group(2)}"
        applied_fixes.append({
            "start": m.start(),
            "end": m.end(),
            "matched": m.group(0),
            "replacement": rep,
            "rule_id": "latin_colon_verse",
        })
        return rep

    current_text = re.sub(r"\b(\d+)\s*:\s*(\d+)(?!\d)", _fix_latin_colon_verse, current_text)

    # 3b. Prose Latin colon between Geʽez words: በለ: ኣነ -> በለ፦ ኣነ
    def _fix_latin_colon_prose(m):
        applied_fixes.append({
            "start": m.start(),
            "end": m.end(),
            "matched": m.group(0),
            "replacement": "፦ ",
            "rule_id": "latin_colon_prose",
        })
        return "፦ "

    current_text = re.sub(rf"(?<={FIDEL_CHAR})\s*:\s*(?={FIDEL_CHAR})", _fix_latin_colon_prose, current_text)

    # Step 4: Stray Latin question marks, commas, and periods attached to Geʽez words
    def _fix_latin_question(m):
        applied_fixes.append({
            "start": m.start(),
            "end": m.end(),
            "matched": m.group(0),
            "replacement": "፧",
            "rule_id": "latin_question_mark",
        })
        return "፧"

    current_text = re.sub(rf"(?<={FIDEL_CHAR})\s*\?", _fix_latin_question, current_text)

    def _fix_latin_comma(m):
        applied_fixes.append({
            "start": m.start(),
            "end": m.end(),
            "matched": m.group(0),
            "replacement": "፣ ",
            "rule_id": "latin_comma",
        })
        return "፣ "

    current_text = re.sub(rf"(?<={FIDEL_CHAR})\s*,(?!\d)", _fix_latin_comma, current_text)

    def _fix_latin_period(m):
        applied_fixes.append({
            "start": m.start(2),
            "end": m.end(2),
            "matched": m.group(2),
            "replacement": "።",
            "rule_id": "latin_period",
        })
        return f"{m.group(1)}።"

    current_text = re.sub(rf"({FIDEL_CHAR}{{2,}})(\s*\.)(?!\d)", _fix_latin_period, current_text)

    # Step 5: Sacred orthography 'የሱስ' -> 'ኢየሱስ'
    def _fix_jesus(m):
        applied_fixes.append({
            "start": m.start(),
            "end": m.end(),
            "matched": m.group(0),
            "replacement": "ኢየሱስ",
            "rule_id": "sacred_name_jesus",
        })
        return "ኢየሱስ"

    current_text = re.sub(rf"{NOT_FIDEL_PRE}የሱስ{NOT_FIDEL_POST}", _fix_jesus, current_text)

    # Step 6: Controlled house-style spellings
    for deprecated, canonical in DEPRECATED_HOUSE_STYLE.items():
        pattern = re.compile(rf"{NOT_FIDEL_PRE}{re.escape(deprecated)}{NOT_FIDEL_POST}")

        def _make_house_replacer(dep, can):
            def _replacer(m):
                applied_fixes.append({
                    "start": m.start(),
                    "end": m.end(),
                    "matched": m.group(0),
                    "replacement": can,
                    "rule_id": f"house_style_{dep}",
                })
                return can
            return _replacer

        current_text = pattern.sub(_make_house_replacer(deprecated, canonical), current_text)

    # Step 7: Morphological blend 'ኣይድወንን' contextual fix
    if "ኣይድወንን" in current_text:
        blend_rep = "ደው ኣይብልን" if ("ጥራይ" in current_text or "ደው" in current_text) else ("ኣይውሰንን" if ("ቦታ" in current_text or "ጊዜ" in current_text) else "ደው ኣይብልን")

        def _fix_blend(m):
            applied_fixes.append({
                "start": m.start(),
                "end": m.end(),
                "matched": m.group(0),
                "replacement": blend_rep,
                "rule_id": "morphological_blend_aydiwennin",
            })
            return blend_rep

        current_text = re.sub(rf"{NOT_FIDEL_PRE}ኣይድወንን{NOT_FIDEL_POST}", _fix_blend, current_text)

    # Step 8: Prohibited Amharic 1:1 tokens
    for amh, tig in AMHARIC_REPLACEMENTS.items():
        pattern = re.compile(rf"{NOT_FIDEL_PRE}{re.escape(amh)}{NOT_FIDEL_POST}")

        def _make_amh_replacer(a, t):
            def _replacer(m):
                applied_fixes.append({
                    "start": m.start(),
                    "end": m.end(),
                    "matched": m.group(0),
                    "replacement": t,
                    "rule_id": f"amharic_token_{a}",
                })
                return t
            return _replacer

        current_text = pattern.sub(_make_amh_replacer(amh, tig), current_text)

    # Step 9: AI Dashes with strict protection of verse ranges, compounds, & negative prefixes
    # Shield protected spans using temporary placeholders
    shielded_tokens: Dict[str, str] = {}
    shield_counter = 0

    def _shield_match(m):
        nonlocal shield_counter
        placeholder = f"__PROTECTED_SPAN_{shield_counter}__"
        shield_counter += 1
        shielded_tokens[placeholder] = m.group(0)
        return placeholder

    # Shield numeric ranges (e.g. 1-9, 21–28)
    current_text = re.sub(r"\b\d+\s*[-–—]\s*\d+\b", _shield_match, current_text)
    # Shield compound Tigrinya words (e.g. ስነ-ምግባር, ቤተ-መቕደስ)
    current_text = re.sub(rf"{FIDEL_CHAR}+-{FIDEL_CHAR}+", _shield_match, current_text)
    # Shield negative prefixes (e.g. ዘይ-ተፈልጠ)
    current_text = re.sub(rf"\bዘይ-{FIDEL_CHAR}+", _shield_match, current_text)
    # Shield leading bullets
    current_text = re.sub(r"^\+\s+", _shield_match, current_text, flags=re.MULTILINE)

    # Replace AI prose dashes
    def _make_dash_replacer(default_punct):
        def _dash_replacer(m):
            pre = current_text[max(0, m.start() - 25):m.start()]
            post = current_text[m.end():min(len(current_text), m.end() + 25)]
            is_speech = any(k in pre for k in ("በለ", "ይብል", "ከምዚ", "ይትረጎም")) or any(k in post for k in ("“", "‘", "‹", "\"", "ከምዚ", "በለ"))
            rep = "፦ " if is_speech else default_punct
            applied_fixes.append({
                "start": m.start(),
                "end": m.end(),
                "matched": m.group(0),
                "replacement": rep,
                "rule_id": "ai_dash_prose",
            })
            return rep
        return _dash_replacer

    current_text = re.sub(r"\s*--+\s*", _make_dash_replacer("፦ "), current_text)
    current_text = re.sub(r"\s*—\s*", _make_dash_replacer("፦ "), current_text)
    current_text = re.sub(r"(?<!\d)\s*–\s*(?!\d)", _make_dash_replacer("፤ "), current_text)
    current_text = re.sub(r"(?<!\d)\s+-\s+(?!\d)", _make_dash_replacer("፤ "), current_text)

    # Restore shielded tokens
    for placeholder, original in shielded_tokens.items():
        current_text = current_text.replace(placeholder, original)

    # Final cleanup of any lingering multiple spaces or space before Geʽez marks
    current_text = re.sub(r"[ \t]+([።፣፤፦፧፨])", r"\1", current_text)
    current_text = re.sub(r"[ \t]{2,}", " ", current_text)

    return current_text.strip(), applied_fixes


def run_gemini_grammar_check(
    text: str,
    api_key: Optional[str] = None,
    model: str = "gemini-2.5-flash"
) -> Dict[str, Any]:
    """
    Zero-dependency Gemini AI grammar check using Python standard library urllib.request.
    Performs deep syntactic analysis of SOV order, gerundive past clause chaining,
    natural pro-drop ellipsis, agreement, and patristic register.
    """
    resolved_key = find_gemini_api_key(api_key)
    if not resolved_key:
        return {
            "available": False,
            "error": "GEMINI_API_KEY could not be found in environment or .env.local files.",
            "issues": [],
            "score": 0,
            "summary": "AI grammar check unavailable without API key.",
        }

    prompt = f"""You are an authoritative Tigrinya grammarian and Orthodox Tewahedo ecclesiastical linguistic auditor.
Analyze the following Tigrinya text and evaluate it rigorously against these 5 core linguistic rules:
1. Strict SOV Word Order: Tigrinya is strictly Subject-Object-Verb. The finite matrix verb or copula (እዩ, እያ, እዮም, ነበረ, ይብል) must be clause-final. Flag any SVO or English/Greek conjunction calques.
2. Gerundive Past Clause Chaining: Actions occurring in sequence must be chained using gerundive verb forms (ወሳኺ ግሲ: መጺኡ፣ በሊዑ፣ ኸደ), never English-style coordinating conjunctions ('-ን' or 'እሞ').
3. Natural Pro-Drop: Independent subject pronouns (ኣነ, ንሱ, ንሳ, etc.) should be omitted unless contrastive or heavily emphasized.
4. Morphological Agreement: Verify gender, number, and politeness agreement (e.g. polite 'ንስኹም' takes 2nd person plural verb agreement).
5. Ecclesiastical Register & Terminology: Enforce sacred name orthography (ኢየሱስ strictly), Orthodox ecclesiastical terms, and appropriate Geʽez punctuation.

Tigrinya Text to Check:
\"\"\"{text}\"\"\"

Respond with a single valid JSON object strictly matching this schema:
{{
  "score": <integer from 0 to 100>,
  "summary": "<concise analytical summary in English or Tigrinya>",
  "issues": [
    {{
      "matched": "<exact substring from the input text containing the error>",
      "start": <character offset start or 0>,
      "end": <character offset end or 0>,
      "category": "<one of: grammar_sov, punctuation_ai, orthography_house_style, anti_amharic, theological_glossary>",
      "severity": "<one of: error, warning, suggestion>",
      "replacement": "<recommended replacement text>",
      "message": "<clear explanation of why this violates Tigrinya grammar/register>",
      "rule_id": "<machine_readable_id>"
    }}
  ],
  "improved_text": "<fully corrected, natural Tigrinya text>"
}}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={resolved_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw_content = data["candidates"][0]["content"]["parts"][0]["text"]
            result = json.loads(raw_content)

            # Safeguard character offsets: align with exact text indices
            for iss in result.get("issues", []):
                matched = iss.get("matched", "")
                if matched and matched in text:
                    idx = text.find(matched)
                    iss["start"] = idx
                    iss["end"] = idx + len(matched)
                iss["deterministic"] = False

            result["available"] = True
            return result
    except urllib.error.HTTPError as e:
        # Fallback to gemini-1.5-flash if gemini-2.5-flash returned 404
        if model != "gemini-1.5-flash" and e.code == 404:
            return run_gemini_grammar_check(text, api_key=resolved_key, model="gemini-1.5-flash")
        err_msg = f"HTTP {e.code}: {e.reason}"
        try:
            err_body = e.read().decode("utf-8")
            err_msg += f" - {err_body}"
        except Exception:
            pass
        return {"available": False, "error": err_msg, "issues": [], "score": 0}
    except Exception as e:
        return {"available": False, "error": str(e), "issues": [], "score": 0}


def run_test_suite() -> bool:
    """
    Expanded benchmark and unit test suite verifying:
    - 20 canonical benchmarks
    - AI dash detection in prose (--+, —, prose –)
    - Protected verse ranges (21–28, 1-9), compound words (ስነ-ምግባር), negative prefixes (ዘይ-), bullets
    - Pre-punctuation and post-punctuation spacing
    - Stray Latin colons, commas, question marks, and periods
    - Exact character offset integrity
    - Deterministic auto-fixer pipeline
    """
    print("=== Running Tigrinya Skill Benchmark Test Suite ===\n")
    test_cases = [
        # (text, should_pass, description)
        ("ነቲ መግቢ በሊዐ።", True, "Benchmark: 'I ate the food' (pro-drop, correct past gerundive, Ge'ez punctuation)"),
        ("መጺኡ፣ መግቡ በሊዑ፣ ናብ ገዛ ኸደ።", True, "Benchmark: Sequential gerundive chaining without English 'and'"),
        ("ኢየሱስ ክርስቶስ ጎይታ እዩ።", True, "Benchmark: Sacred name 'ኢየሱስ' + copula 'እዩ'"),
        ("እኔ ምግብ በላሁ።", False, "Amharic contamination: 'እኔ' + 'ምግብ'"),
        ("ንሱ ወደ ቤት ሄደ።", False, "Amharic contamination: standalone 'ቤት'"),
        ("ይህ ሰውዬ አስተማሪ ነው።", False, "Amharic contamination: 'ነው' copula + 'ይህ'"),
        ("ትማሊ መጽሓፍ ኣንቢበ.", False, "Punctuation failure: Latin period '.' instead of '።'"),
        ("የሱስ ናብ ገዛ መጺኡ።", False, "Sacred orthography failure: 'የሱስ' instead of 'ኢየሱስ'"),
        ("እቲ ምስጢር ኣብ ህይወት ይግለጽ።", False, "House-style failure: mystery and life spellings"),
        ("ስለምንታይ ኰከብ ተጠቒሙ?", False, "Punctuation failure: Latin question mark after Geʽez text"),
        ("እቲ ምሥጢር ኣብ ሕይወት ይግለጽ።", True, "Controlled ecclesiastical house-style benchmark"),
        ("ኣብ ክልተ ትኸፍሎ፧ ነቲ ተዋህዶ ተፍርሶ ኣለኻ፧", True, "Theological dialogue benchmark from Google AI Studio"),
        ("ኣብቲ ግብራዊ ኃጢኣት ጥራይ ኣይድወንን እዩ።", False, "Morphological blend failure: '*ኣይድወንን' instead of 'ደው ኣይብልን'"),
        ("ኣብቲ ግብራዊ ኃጢኣት ጥራይ ደው ኣይብልን እዩ።", True, "Corrected phrasal negative: 'ደው ኣይብልን'"),
        ("ብቦታ ወይ ብጊዜ ኣይውሰንን እዩ።", True, "Valid root-final '-ን' negative verb: 'ኣይውሰንን'"),
        ("ቅዱስ ጀሮም (St. Jerome) ከምዚ በለ (Matt 6፡1)።", False, "Latin residue failure: unlocalized English Scripture citation (Matt 6:1)"),
        ("ቅዱስ ጀሮም (St. Jerome) ከምዚ በለ (ማቴዎስ 6፡1)።", True, "Approved bilingual patristic attribution and localized Tigrinya citation"),
        ("እቶም ግኖስቲካውያን (Gnostics) ከምዚ በሉ።", True, "Approved bilingual historical sect gloss: ግኖስቲካውያን (Gnostics)"),
        ("እታ “ኤፒኡስዮስ” (epiousios) እትብል ቃል ካብ “ኡስያ” (ousia) ዝመጸት እያ።", True, "Approved Greek/Latin etymology glosses"),
        ("G. H. Box ወንጌላዊ ቅዱስ ማቴዎስ ይብል።", True, "Approved direct English modern scholar reference"),

        # --- New R2 Tests for Punctuation, Dashes, Spacing, & Protection Rules ---
        ("እቲ ምስጢር -- ከምዚ እዩ።", False, "AI double dash '--' in prose rejected in favor of Geʽez punctuation"),
        ("ቅዱስ ጳውሎስ — ከምዚ በለ።", False, "AI em-dash '—' in prose rejected in favor of Geʽez punctuation"),
        ("ናይ እግዚኣብሔር ጸጋ - ንዂሉ ይበጽሕ።", False, "AI prose spaced hyphen ' - ' rejected in favor of '፤'"),
        ("ማቴዎስ 21–28 ኣንብብ።", True, "Numeric verse range with en-dash '21–28' strictly preserved"),
        ("ናይ 1-9 ፍቕድታት ኣንብብ።", True, "Numeric verse range with hyphen '1-9' strictly preserved"),
        ("ስነ-ምግባር ክህልወና ይግባእ።", True, "Compound Tigrinya word 'ስነ-ምግባር' strictly preserved"),
        ("ዘይ-ተፈልጠ ነገር የለን።", True, "Negative prefix 'ዘይ-ተፈልጠ' strictly preserved"),
        ("+ ቅዱስ ዮሐንስ ኣፈወርቅ ከምዚ በለ።", True, "Patristic quote bullet '+ ' strictly preserved"),
        ("ንሱ መጺኡ ።", False, "Erroneous space before Geʽez ' ።' detected"),
        ("እወ ፣ ንሱ እዩ ።", False, "Multiple spaces before Geʽez punctuation ' ፣' and ' ።' detected"),
        ("ማቴዎስ 6:1", False, "Latin colon in Scripture reference '6:1' detected (requires '6፡1')"),
        ("ከምዚ በለ: ኣነ እየ", False, "Latin colon in Geʽez prose detected (requires '፦ ')"),
        ("መጺኡ, በሊዑ።", False, "Stray Latin comma ',' in Geʽez prose detected (requires '፣')"),
        ("እዚ ጽቡቕ ነው።", False, "Amharic copula 'ነው' detected with replacement and offset"),
    ]

    all_passed = True
    for text, expected_pass, description in test_cases:
        res = audit_tigrinya(text, strict=True)
        success = (res["passed"] == expected_pass)
        status_label = "PASS" if success else "FAIL"
        if not success:
            all_passed = False

        print(f"[{status_label}] {description}")
        print(f"       Input: \"{text}\"")
        if not res["passed"]:
            for iss in res["issues"]:
                print(f"       -> [ISSUE] ({iss['category']}) {iss['message']} [rule: {iss['rule_id']}]")
        if res["warnings"]:
            for w in res["warnings"]:
                print(f"       -> [WARN]  ({w['category']}) {w['message']}")
        print()

    # --- Test 35: Deterministic Auto-Fixer Pipeline Integrity ---
    print("--- Testing Deterministic Auto-Fixer Pipeline ---")
    dirty_input = "እቲ ምስጢር -- ኣብ ህይወት እዩ ።"
    fixed_output, fixes = fix_deterministic(dirty_input)
    expected_fixed = "እቲ ምሥጢር፦ ኣብ ሕይወት እዩ።"
    fix_success = (fixed_output == expected_fixed)
    if not fix_success:
        all_passed = False
    print(f"[{'PASS' if fix_success else 'FAIL'}] fix_deterministic: '{dirty_input}' -> '{fixed_output}'")
    if not fix_success:
        print(f"       Expected: '{expected_fixed}'")
        print(f"       Got:      '{fixed_output}'")
    print(f"       Fixes applied count: {len(fixes)}")
    print()

    # --- Test 36: Character Offset Precision Integrity ---
    print("--- Testing Character Offset Precision Integrity ---")
    offset_test_text = "እኔ ምግብ በላሁ። ይህ አስተማሪ ነው።"
    offset_res = audit_tigrinya(offset_test_text, strict=True)
    offset_success = True
    for iss in offset_res["issues"]:
        extracted = offset_test_text[iss["start"]:iss["end"]]
        if extracted != iss["matched"]:
            offset_success = False
            print(f"       [OFFSET MISMATCH] Expected '{iss['matched']}', slice gave '{extracted}' at [{iss['start']}:{iss['end']}]")
    if not offset_success:
        all_passed = False
    print(f"[{'PASS' if offset_success else 'FAIL'}] Character offsets perfectly match text slices for all {len(offset_res['issues'])} issues.")
    print()

    total_tests = len(test_cases) + 2
    print("=" * 50)
    if all_passed:
        print(f"ALL {total_tests} TESTS PASSED: Benchmark compliance verified successfully.")
    else:
        print("TEST FAILURES DETECTED: Check output above.")
    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Audit Tigrinya translation against grammar, typography, and anti-leakage rules.")
    parser.add_argument("text", nargs="?", help="Tigrinya text string to audit")
    parser.add_argument("--test", action="store_true", help="Run benchmark verification test suite")
    parser.add_argument("--fix", action="store_true", help="Run deterministic auto-fixing on input text")
    parser.add_argument("--ai", action="store_true", help="Run Gemini AI deep grammar check")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--lenient", action="store_true", help="Treat punctuation mismatches as warnings rather than errors")
    parser.add_argument("--studio", action="store_true", help="Launch local Web Studio HTTP server")
    parser.add_argument("--port", type=int, default=8765, help="Port for Web Studio server (default: 8765)")
    args = parser.parse_args()

    if args.studio:
        from studio import run_server
        run_server(port=args.port)
        return

    if args.test:
        success = run_test_suite()
        sys.exit(0 if success else 1)

    if not args.text:
        parser.print_help()
        sys.exit(0)

    if args.fix:
        fixed_text, fixes = fix_deterministic(args.text)
        if args.json:
            print(json.dumps({"original": args.text, "fixed": fixed_text, "fixes": fixes}, ensure_ascii=False, indent=2))
        else:
            print(fixed_text)
        sys.exit(0)

    if args.ai:
        ai_res = run_gemini_grammar_check(args.text)
        if args.json:
            print(json.dumps(ai_res, ensure_ascii=False, indent=2))
        else:
            print("\n--- Gemini AI Grammar Analysis ---")
            if not ai_res.get("available"):
                print(f"Status: Unavailable ({ai_res.get('error')})")
            else:
                print(f"Score:   {ai_res.get('score')}/100")
                print(f"Summary: {ai_res.get('summary')}")
                if ai_res.get("issues"):
                    print("\nIssues:")
                    for iss in ai_res["issues"]:
                        print(f" - [{iss.get('category')}] {iss.get('matched')} -> {iss.get('replacement')}: {iss.get('message')}")
                if ai_res.get("improved_text"):
                    print(f"\nImproved Text:\n{ai_res['improved_text']}")
        sys.exit(0)

    result = audit_tigrinya(args.text, strict=not args.lenient)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result["passed"] else 1)

    print("\n--- Audit Summary ---")
    print(f"Status:   {'PASSED' if result['passed'] else 'FAILED'}")
    print(f"Score:    {result['score']}/100")
    print(f"Issues:   {result['issue_count']}")
    print(f"Warnings: {result['warning_count']}\n")

    if result["issues"]:
        print("Issues found:")
        for iss in result["issues"]:
            print(f" - [{iss['category']}] [{iss['rule_id']}] {iss['message']} (start={iss['start']}, end={iss['end']})")

    if result["warnings"]:
        print("\nWarnings:")
        for w in result["warnings"]:
            print(f" - [{w['category']}] [{w['rule_id']}] {w['message']} (start={w['start']}, end={w['end']})")

    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
