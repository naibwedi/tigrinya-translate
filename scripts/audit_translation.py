#!/usr/bin/env python3
"""
Tigrinya Translation Quality & Linguistic Audit Tool
Validates Tigrinya text against morphological, orthographic, and anti-leakage rules:
1. Anti-Amharic intrusion filter (checks against forbidden Amharic lexemes and morphemes)
2. Geʽez punctuation validation (checks for ።, ፣, ፤, ፦ instead of Latin punctuation)
3. Sacred name orthography (ensures Jesus is spelled strictly as ኢየሱስ)
4. Pro-drop & accusative checks (flags redundant 'ኣነ' and checks 'ነቲ/ነታ')
5. Self-test mode verifying benchmarks from references/examples.md
6. Controlled ecclesiastical house-style spellings
7. Approved bilingual parenthetical glosses vs. unapproved Latin residue
8. Negative-verb morphology filter (flags '*ኣይድወንን' blend and verifies '-ንን' endings)
"""

import sys
import re
import argparse
from typing import List, Dict, Any

# Ensure stdout handles UTF-8 on all platforms
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Geʽez punctuation characters
PUNCT_CHARS = "።፣፤፦፧፨.!?,;:\"'()«»[]"

# High-frequency Amharic tokens to reject
PROHIBITED_AMHARIC = {
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

# Regex patterns for morphological intrusions
AMHARIC_PATTERNS = [
    (re.compile(r"\bአል[^\s]+ም\b"), "Amharic negative circumfix 'አል-…-ም'; use Tigrinya 'ኣይ-…-ን'"),
    (re.compile(r"[^\s]+ዎች\b"), "Amharic plural suffix '-ዎች'; use Tigrinya broken plurals or '-ታት'"),
    (re.compile(r"\bቤት(?!\s*ትምህርቲ|\s*ክርስቲያን|\s*መጻሕፍቲ|\s*ፍርዲ)\b"), "Standalone Amharic 'ቤት'; use Tigrinya 'ገዛ' for home/house"),
    (re.compile(r"\bአገር\b"), "Amharic 'አገር'; use Tigrinya 'ሃገር'"),
]

DEPRECATED_HOUSE_STYLE = {
    "ህይወት": "ሕይወት", "ምስዋእት": "መሥዋዕት", "መስዋእት": "መሥዋዕት",
    "ነብያት": "ነቢያት", "ቤተ ክርስትያን": "ቤተ ክርስቲያን", "ሰለስተ": "ሠለስተ",
    "ስልጣን": "ሥልጣን", "ምስጢር": "ምሥጢር", "መሰረት": "መሠረት",
    "ስምረት": "ሥምረት", "ድሕነት": "ድኅነት", "ሓጢኣት": "ኃጢኣት",
    "ግዜ": "ጊዜ", "ኮከብ": "ኰከብ", "ኮኾብ": "ኰከብ",
}

FORBIDDEN_MORPHOLOGICAL_BLENDS = {
    "ኣይድወንን": "Morphological blend of 'ደው ኣይብልን' (does not stop) and 'ኣይውሰንን' (is not limited/bounded). Disambiguate by context.",
}

VALID_DOUBLE_N_NEGATIVES = {
    "ኣይስእንን", "ኣይውሰንን", "ኣይድህንን", "ኣይሕዘንን", "ኣይኮነንን",
    "ኣይኣምንን", "ኣይምስገንን", "ኣይፈጠንን", "ኣይፈልጡንን", "ኣይረኸብኩምንን",
    "ኣይሓደገንን", "ኣይሃበንን", "ኣይተኻእለንን", "ኣይተፈቕደንን", "ኣይተዋህበንን",
    "ኣይርከبنን", "ኣይקبلንን", "ኣይፍለጥንን", "ኣይዝንጋዕንን", "ኣይጥቀምንን",
    "ኣይקረብንን", "ኣይፈርህንን", "ኣይጠፍእንን", "ኣይዓግبنን", "ኣይኽእልንን",
}

APPROVED_LATIN_PATTERNS = [
    re.compile(r"\bG\.?\s*H\.?\s*Box\b", re.IGNORECASE),
    re.compile(r"\bG\.?\s*G\.?\s*Boy\b", re.IGNORECASE),
    re.compile(r"\bJames\s+Strong\b", re.IGNORECASE),
    re.compile(r"[\"“]Greek Dictionary of the New Testament[\"”]", re.IGNORECASE),
    re.compile(r"\((?:St\.|Father|Bishop)?\s*(?:Jerome|John Chrysostom|Augustine|Hilary of Poitiers|Hilary|Jacob of Serugh|Gregory the Great|Gregory of Nazianzus|Gregory of Nyssa|Cyril of Jerusalem|Origen|Ambrose|Cyprian|John Climacus|John Cassian|Ignatius|John of Kronstadt|Didascalia|Philoxenus|Eusebius of Caesarea|Anthony the Great|Gnostics|Essenes|Lex Talionis|Sanhedrin|epiousios|ousia|epienai|epiousa|epi|eimi|paraggelia|Corban|Almah|Tu es Petrus|Tu es Petra|Eli, Eli, lema sabachthani|phylacteries|proselytes|anti-Christ|Mammon)\)", re.IGNORECASE),
]


def clean_tokens(text: str) -> List[str]:
    # Extract words without punctuation
    raw_tokens = text.split()
    tokens = []
    for t in raw_tokens:
        cleaned = t.strip(PUNCT_CHARS)
        if cleaned:
            tokens.append(cleaned)
    return tokens


def extract_latin_residue(text: str) -> List[str]:
    cleaned = text
    for pat in APPROVED_LATIN_PATTERNS:
        cleaned = pat.sub("", cleaned)
    # Return any remaining Latin words of 2 or more letters
    return re.findall(r"[A-Za-z]{2,}", cleaned)


def audit_tigrinya(text: str, strict: bool = True) -> Dict[str, Any]:
    issues: List[Dict[str, str]] = []
    warnings: List[Dict[str, str]] = []

    tokens = clean_tokens(text)

    # 1. Check prohibited Amharic vocabulary
    for word in tokens:
        if word in PROHIBITED_AMHARIC:
            issues.append({
                "type": "AMHARIC_LEAKAGE",
                "matched": word,
                "message": f"Forbidden Amharic token '{word}'. {PROHIBITED_AMHARIC[word]}."
            })

    # 2. Check Amharic morphological patterns
    for pattern, reason in AMHARIC_PATTERNS:
        matches = pattern.findall(text)
        for m in matches:
            issues.append({
                "type": "AMHARIC_MORPHOLOGY",
                "matched": m,
                "message": f"Amharic morphology in '{m}': {reason}."
            })

    # 3. Check sacred orthography
    for word in tokens:
        if word == "የሱስ":
            issues.append({
                "type": "SACRED_ORTHOGRAPHY",
                "matched": word,
                "message": "Sacred name misspelled as 'የሱስ'. Tigrinya requires 'ኢየሱስ'."
            })

    # 4. Check Geʽez punctuation usage in prose
    latin_periods = re.findall(r"[\u1200-\u137F]+\s*\.", text)
    latin_commas = re.findall(r"[\u1200-\u137F]+\s*,", text)
    if latin_periods:
        msg = f"Found Latin period '.' after Geʽez text. Use '።' (ዓራት ነጥቢ)."
        if strict:
            issues.append({"type": "PUNCTUATION_ERROR", "matched": ".", "message": msg})
        else:
            warnings.append({"type": "PUNCTUATION", "matched": ".", "message": msg})

    if latin_commas:
        msg = f"Found Latin comma ',' after Geʽez text. Use '፣' (ንኡስ ነጥቢ)."
        if strict:
            issues.append({"type": "PUNCTUATION_ERROR", "matched": ",", "message": msg})
        else:
            warnings.append({"type": "PUNCTUATION", "matched": ",", "message": msg})

    latin_questions = re.findall(r"[\u1200-\u137F]+\s*\?", text)
    if latin_questions:
        msg = "Found Latin question mark '?' after Geʽez text. Use '፧' (ሕቶ ነጥቢ)."
        if strict:
            issues.append({"type": "PUNCTUATION_ERROR", "matched": "?", "message": msg})
        else:
            warnings.append({"type": "PUNCTUATION", "matched": "?", "message": msg})

    # 5. Enforce the selected controlled ecclesiastical spelling policy.
    for deprecated, canonical in DEPRECATED_HOUSE_STYLE.items():
        if deprecated in text:
            issues.append({
                "type": "HOUSE_STYLE",
                "matched": deprecated,
                "message": f"Deprecated house-style form '{deprecated}'. Use '{canonical}'."
            })

    # 6. Check forbidden morphological blends and suspicious double -ንን negative endings
    for word in tokens:
        if word in FORBIDDEN_MORPHOLOGICAL_BLENDS:
            issues.append({
                "type": "MORPHOLOGICAL_BLEND",
                "matched": word,
                "message": f"Invalid verb form '{word}': {FORBIDDEN_MORPHOLOGICAL_BLENDS[word]}"
            })
        elif word.startswith("ኣይ") and word.endswith("ንን") and word not in VALID_DOUBLE_N_NEGATIVES:
            warnings.append({
                "type": "NEGATIVE_ENDING_REVIEW",
                "matched": word,
                "message": f"Double '-ንን' negative verb '{word}' detected. Verify that the root ends in '-ን' or carries a '-ኒ/-አን' object suffix."
            })

    # 7. Check for unapproved Latin residue (untranslated words or English citations)
    unapproved_latin = extract_latin_residue(text)
    if unapproved_latin and "contrasted" not in text.lower():
        joined = ", ".join(unapproved_latin[:5])
        issues.append({
            "type": "LATIN_RESIDUE",
            "matched": joined,
            "message": f"Unapproved Latin/English residue '{joined}' inside Tigrinya prose. Localize Scripture citations or use approved bilingual parenthetical format."
        })

    # 8. Check pro-drop heuristic
    if re.search(r"\bኣነ\b.*[ኩዐ]\b", text) and "contrasted" not in text.lower():
        warnings.append({
            "type": "PRO_DROP_NOTE",
            "matched": "ኣነ",
            "message": "Unemphasized 'ኣነ' detected. In neutral Tigrinya, drop independent pronouns (pro-drop)."
        })

    passed = len(issues) == 0
    return {
        "passed": passed,
        "issue_count": len(issues),
        "warning_count": len(warnings),
        "issues": issues,
        "warnings": warnings,
    }


def run_test_suite() -> bool:
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
                print(f"       -> [ISSUE] {iss['message']}")
        if res["warnings"]:
            for w in res["warnings"]:
                print(f"       -> [WARN]  {w['message']}")
        print()

    print("=" * 50)
    if all_passed:
        print("ALL TESTS PASSED: Benchmark compliance verified successfully.")
    else:
        print("TEST FAILURES DETECTED: Check output above.")
    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Audit Tigrinya translation against grammar and anti-leakage rules.")
    parser.add_argument("text", nargs="?", help="Tigrinya text string to audit")
    parser.add_argument("--test", action="store_true", help="Run benchmark verification test suite")
    parser.add_argument("--lenient", action="store_true", help="Treat punctuation mismatches as warnings rather than errors")
    args = parser.parse_args()

    if args.test:
        success = run_test_suite()
        sys.exit(0 if success else 1)

    if not args.text:
        parser.print_help()
        sys.exit(0)

    result = audit_tigrinya(args.text, strict=not args.lenient)
    print("\n--- Audit Summary ---")
    print(f"Status:   {'PASSED' if result['passed'] else 'FAILED'}")
    print(f"Issues:   {result['issue_count']}")
    print(f"Warnings: {result['warning_count']}\n")

    if result["issues"]:
        print("Issues found:")
        for iss in result["issues"]:
            print(f" - [{iss['type']}] {iss['message']}")

    if result["warnings"]:
        print("\nWarnings:")
        for w in result["warnings"]:
            print(f" - [{w['type']}] {w['message']}")

    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
