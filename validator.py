"""
Project 2: CPF & CNPJ Validator
================================
Validates both traditional numeric CPF/CNPJ AND the new alphanumeric
CNPJ format taking effect July 2026 (Instrucao Normativa 2.229).

Key change: the first 12 positions of a CNPJ can now contain uppercase
letters (A-Z). Each character is converted to its ASCII decimal value
minus 48 before entering the Modulo 11 check-digit calculation.

Numeric digits: '0'=0, '1'=1, ..., '9'=9
Alpha characters: 'A'=17, 'B'=18, ..., 'Z'=42

The check-digit algorithm (Modulo 11) itself is unchanged.
"""

import re
from typing import Optional


# ---------------------------------------------------------------------------
# Character conversion (new alphanumeric rule)
# ---------------------------------------------------------------------------

def char_to_value(c: str) -> int:
    """
    Convert a single character to its numeric value using the
    new CNPJ alphanumeric rule: ASCII code minus 48.

    '0'-'9' -> 0-9
    'A'-'Z' -> 17-42
    """
    code = ord(c.upper())
    if 48 <= code <= 57:      # digits 0-9
        return code - 48
    elif 65 <= code <= 90:    # letters A-Z
        return code - 48
    else:
        raise ValueError(f"Invalid character for CNPJ: '{c}'")


# ---------------------------------------------------------------------------
# CPF Validation
# ---------------------------------------------------------------------------

def clean_cpf(cpf: str) -> str:
    """Strip formatting characters from a CPF string."""
    return re.sub(r"[.\-/\s]", "", cpf.strip())


def validate_cpf(cpf: str) -> dict:
    """
    Validate a Brazilian CPF (Cadastro de Pessoas Fisicas).

    Algorithm (Modulo 11):
    1. Take the first 9 digits.
    2. Multiply each by weights 10, 9, 8, ..., 2 and sum.
    3. remainder = sum % 11. If remainder < 2 -> digit = 0, else digit = 11 - remainder.
    4. Append first check digit, repeat with weights 11, 10, ..., 2 for 10 digits.
    5. Compare both check digits with the input.

    Returns a dict with 'valid' (bool), 'cpf' (cleaned), and 'message'.
    """
    raw = clean_cpf(cpf)

    if not raw.isdigit():
        return {"valid": False, "cpf": raw, "message": "CPF must contain only digits."}

    if len(raw) != 11:
        return {"valid": False, "cpf": raw, "message": "CPF must have exactly 11 digits."}

    # Reject known invalid sequences (all same digit)
    if raw == raw[0] * 11:
        return {"valid": False, "cpf": raw, "message": "CPF with all identical digits is invalid."}

    digits = [int(d) for d in raw]

    # First check digit
    weights_1 = list(range(10, 1, -1))  # [10, 9, 8, ..., 2]
    total = sum(d * w for d, w in zip(digits[:9], weights_1))
    remainder = total % 11
    check_1 = 0 if remainder < 2 else 11 - remainder

    if digits[9] != check_1:
        return {"valid": False, "cpf": raw, "message": "First check digit does not match."}

    # Second check digit
    weights_2 = list(range(11, 1, -1))  # [11, 10, 9, ..., 2]
    total = sum(d * w for d, w in zip(digits[:10], weights_2))
    remainder = total % 11
    check_2 = 0 if remainder < 2 else 11 - remainder

    if digits[10] != check_2:
        return {"valid": False, "cpf": raw, "message": "Second check digit does not match."}

    return {"valid": True, "cpf": raw, "message": "Valid CPF."}


def format_cpf(cpf: str) -> str:
    """Format a clean CPF string as XXX.XXX.XXX-XX."""
    raw = clean_cpf(cpf)
    if len(raw) != 11:
        return raw
    return f"{raw[:3]}.{raw[3:6]}.{raw[6:9]}-{raw[9:]}"


# ---------------------------------------------------------------------------
# CNPJ Validation (supports both numeric AND alphanumeric)
# ---------------------------------------------------------------------------

def clean_cnpj(cnpj: str) -> str:
    """Strip formatting characters from a CNPJ string."""
    return re.sub(r"[.\-/\s]", "", cnpj.strip()).upper()


def is_alphanumeric_cnpj(cnpj: str) -> bool:
    """Check if a cleaned CNPJ contains letters (new format)."""
    return bool(re.search(r"[A-Z]", cnpj[:12]))


def validate_cnpj(cnpj: str) -> dict:
    """
    Validate a Brazilian CNPJ — works for both traditional (numeric)
    and the new alphanumeric format (July 2026+).

    Algorithm (Modulo 11 with alphanumeric conversion):
    1. Clean the CNPJ to 14 characters (12 base + 2 check digits).
    2. Convert each of the first 12 characters to numeric values using
       char_to_value() (ASCII - 48).
    3. First check digit:
       - Weights: [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
       - Sum the products of values * weights.
       - remainder = sum % 11
       - If remainder < 2 -> digit = 0, else digit = 11 - remainder.
    4. Second check digit:
       - Weights: [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
       - Include the first check digit in the sequence (13 values).
       - Same modulo 11 rule.
    5. The last two characters of the CNPJ MUST be numeric digits
       matching the calculated check digits.

    Returns a dict with 'valid', 'cnpj', 'is_alphanumeric', and 'message'.
    """
    raw = clean_cnpj(cnpj)

    if len(raw) != 14:
        return {
            "valid": False, "cnpj": raw,
            "is_alphanumeric": False,
            "message": "CNPJ must have exactly 14 characters."
        }

    # Validate character set: first 12 can be alphanumeric, last 2 must be digits
    base_part = raw[:12]
    check_part = raw[12:]

    if not re.fullmatch(r"[A-Z0-9]{12}", base_part):
        return {
            "valid": False, "cnpj": raw,
            "is_alphanumeric": is_alphanumeric_cnpj(raw),
            "message": "First 12 positions must be digits or uppercase letters."
        }

    if not check_part.isdigit():
        return {
            "valid": False, "cnpj": raw,
            "is_alphanumeric": is_alphanumeric_cnpj(raw),
            "message": "Check digits (positions 13-14) must be numeric."
        }

    alphanumeric = is_alphanumeric_cnpj(raw)

    # For purely numeric CNPJs, reject all-same-digit sequences
    if not alphanumeric and raw == raw[0] * 14:
        return {
            "valid": False, "cnpj": raw,
            "is_alphanumeric": False,
            "message": "CNPJ with all identical digits is invalid."
        }

    # Convert characters to values
    try:
        values = [char_to_value(c) for c in base_part]
    except ValueError as e:
        return {
            "valid": False, "cnpj": raw,
            "is_alphanumeric": alphanumeric,
            "message": str(e)
        }

    # First check digit
    weights_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    total = sum(v * w for v, w in zip(values, weights_1))
    remainder = total % 11
    check_1 = 0 if remainder < 2 else 11 - remainder

    expected_check_1 = int(check_part[0])
    if expected_check_1 != check_1:
        return {
            "valid": False, "cnpj": raw,
            "is_alphanumeric": alphanumeric,
            "message": f"First check digit mismatch: expected {check_1}, got {expected_check_1}."
        }

    # Second check digit
    weights_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    values_13 = values + [check_1]
    total = sum(v * w for v, w in zip(values_13, weights_2))
    remainder = total % 11
    check_2 = 0 if remainder < 2 else 11 - remainder

    expected_check_2 = int(check_part[1])
    if expected_check_2 != check_2:
        return {
            "valid": False, "cnpj": raw,
            "is_alphanumeric": alphanumeric,
            "message": f"Second check digit mismatch: expected {check_2}, got {expected_check_2}."
        }

    return {
        "valid": True, "cnpj": raw,
        "is_alphanumeric": alphanumeric,
        "message": "Valid CNPJ." + (" (alphanumeric format)" if alphanumeric else "")
    }


def format_cnpj(cnpj: str) -> str:
    """Format a clean CNPJ string as XX.XXX.XXX/XXXX-XX."""
    raw = clean_cnpj(cnpj)
    if len(raw) != 14:
        return raw
    return f"{raw[:2]}.{raw[2:5]}.{raw[5:8]}/{raw[8:12]}-{raw[12:]}"


# ---------------------------------------------------------------------------
# Utility: generate check digits
# ---------------------------------------------------------------------------

def generate_cpf_check_digits(base_9: str) -> str:
    """Given the first 9 digits of a CPF, compute and return the full 11-digit CPF."""
    base = clean_cpf(base_9)
    if len(base) != 9 or not base.isdigit():
        raise ValueError("Provide exactly 9 numeric digits.")

    digits = [int(d) for d in base]

    weights_1 = list(range(10, 1, -1))
    total = sum(d * w for d, w in zip(digits, weights_1))
    r = total % 11
    c1 = 0 if r < 2 else 11 - r
    digits.append(c1)

    weights_2 = list(range(11, 1, -1))
    total = sum(d * w for d, w in zip(digits, weights_2))
    r = total % 11
    c2 = 0 if r < 2 else 11 - r
    digits.append(c2)

    return "".join(str(d) for d in digits)


def generate_cnpj_check_digits(base_12: str) -> str:
    """
    Given the first 12 characters of a CNPJ (numeric or alphanumeric),
    compute and return the full 14-character CNPJ.
    """
    base = re.sub(r"[.\-/\s]", "", base_12.strip()).upper()
    if len(base) != 12:
        raise ValueError("Provide exactly 12 characters.")
    if not re.fullmatch(r"[A-Z0-9]{12}", base):
        raise ValueError("Characters must be digits or uppercase letters.")

    values = [char_to_value(c) for c in base]

    weights_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    total = sum(v * w for v, w in zip(values, weights_1))
    r = total % 11
    c1 = 0 if r < 2 else 11 - r

    weights_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    values_13 = values + [c1]
    total = sum(v * w for v, w in zip(values_13, weights_2))
    r = total % 11
    c2 = 0 if r < 2 else 11 - r

    return base + str(c1) + str(c2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="CPF / CNPJ Validator (supports new alphanumeric CNPJ 2026)"
    )
    sub = parser.add_subparsers(dest="command")

    p_cpf = sub.add_parser("cpf", help="Validate a CPF")
    p_cpf.add_argument("value", help="CPF number")

    p_cnpj = sub.add_parser("cnpj", help="Validate a CNPJ")
    p_cnpj.add_argument("value", help="CNPJ (numeric or alphanumeric)")

    p_gen_cpf = sub.add_parser("gen-cpf", help="Generate check digits for a CPF base")
    p_gen_cpf.add_argument("base", help="First 9 digits of the CPF")

    p_gen_cnpj = sub.add_parser("gen-cnpj", help="Generate check digits for a CNPJ base")
    p_gen_cnpj.add_argument("base", help="First 12 characters of the CNPJ")

    args = parser.parse_args()

    if args.command == "cpf":
        result = validate_cpf(args.value)
        print(f"CPF: {format_cpf(result['cpf'])}")
        print(f"Valid: {result['valid']}")
        print(f"Message: {result['message']}")

    elif args.command == "cnpj":
        result = validate_cnpj(args.value)
        print(f"CNPJ: {format_cnpj(result['cnpj'])}")
        print(f"Valid: {result['valid']}")
        print(f"Alphanumeric: {result['is_alphanumeric']}")
        print(f"Message: {result['message']}")

    elif args.command == "gen-cpf":
        full = generate_cpf_check_digits(args.base)
        print(f"Full CPF: {format_cpf(full)}")

    elif args.command == "gen-cnpj":
        full = generate_cnpj_check_digits(args.base)
        print(f"Full CNPJ: {format_cnpj(full)}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
