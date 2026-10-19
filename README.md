# CPF/CNPJ Validator

A command-line validator for Brazilian CPF and CNPJ numbers, including the
new alphanumeric CNPJ format that takes effect in July 2026 under
Instrução Normativa RFB 2.229.

## Features

- **CPF validation**: standard Módulo 11 check-digit algorithm (weights
  10→2 then 11→2), with rejection of all-identical-digit sequences and
  malformed input.
- **CNPJ validation**, both formats:
  - Traditional numeric CNPJ (14 digits).
  - New alphanumeric CNPJ (July 2026+): the first 12 positions may contain
    uppercase letters A–Z in addition to digits; the 2 check digits remain
    numeric. Each character is converted to its numeric value as
    `ord(char) - 48` (so `'0'-'9'` → 0–9 and `'A'-'Z'` → 17–42) before the
    same Módulo 11 algorithm is applied with CNPJ-specific weights.
- **Check-digit generation**: given a 9-digit CPF base or a 12-character
  CNPJ base (numeric or alphanumeric), computes the two valid check digits.
- Accepts formatted or unformatted input (`529.982.247-25` or
  `52998224725`), case-insensitive for CNPJ letters.

## Stack

Pure Python standard library (`re`), no runtime dependencies. Tests with
`pytest`.

## Running it

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python validator.py --help
```

```bash
# Validate CPF
python validator.py cpf 529.982.247-25

# Validate a traditional CNPJ
python validator.py cnpj 11.222.333/0001-81

# Validate a new alphanumeric CNPJ
python validator.py cnpj 12.ABC.345/01DE-35

# Generate check digits from a base
python validator.py gen-cpf 529982247
python validator.py gen-cnpj 12ABC34501DE
```

## Tests

```bash
pip install -r requirements.txt
pytest test_validator.py -v
```

Covers character conversion (digits and letters), CPF validation (valid,
invalid, edge cases), traditional numeric CNPJ, the new alphanumeric CNPJ
against the official Receita Federal reference example, check-digit
generation, generate-then-validate roundtrips, and edge cases (empty
strings, whitespace, invalid characters).

## Screenshots

> _placeholder — add a terminal screenshot of a CPF and CNPJ validation run here_

## License

MIT — see [LICENSE](LICENSE).
