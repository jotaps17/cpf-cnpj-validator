"""
Tests for Project 2: CPF & CNPJ Validator
"""

import pytest
from validator import (
    char_to_value, clean_cpf, clean_cnpj,
    validate_cpf, validate_cnpj, format_cpf, format_cnpj,
    generate_cpf_check_digits, generate_cnpj_check_digits,
    is_alphanumeric_cnpj,
)


# ---------------------------------------------------------------------------
# char_to_value tests
# ---------------------------------------------------------------------------

class TestCharToValue:
    def test_digits(self):
        for i in range(10):
            assert char_to_value(str(i)) == i

    def test_letters(self):
        assert char_to_value("A") == 17
        assert char_to_value("B") == 18
        assert char_to_value("Z") == 42

    def test_lowercase_letters(self):
        assert char_to_value("a") == 17
        assert char_to_value("z") == 42

    def test_invalid_character(self):
        with pytest.raises(ValueError):
            char_to_value("!")
        with pytest.raises(ValueError):
            char_to_value("@")


# ---------------------------------------------------------------------------
# CPF tests
# ---------------------------------------------------------------------------

class TestCPFValidation:
    """Test CPF validation with known valid/invalid numbers."""

    def test_valid_cpf(self):
        # Known valid CPF: 529.982.247-25
        result = validate_cpf("52998224725")
        assert result["valid"] is True

    def test_valid_cpf_formatted(self):
        result = validate_cpf("529.982.247-25")
        assert result["valid"] is True

    def test_invalid_cpf_wrong_check_digit(self):
        result = validate_cpf("52998224720")
        assert result["valid"] is False

    def test_invalid_cpf_all_same_digits(self):
        for d in range(10):
            result = validate_cpf(str(d) * 11)
            assert result["valid"] is False

    def test_invalid_cpf_too_short(self):
        result = validate_cpf("1234")
        assert result["valid"] is False

    def test_invalid_cpf_too_long(self):
        result = validate_cpf("123456789012")
        assert result["valid"] is False

    def test_invalid_cpf_with_letters(self):
        result = validate_cpf("5299822472A")
        assert result["valid"] is False

    def test_format_cpf(self):
        assert format_cpf("52998224725") == "529.982.247-25"

    def test_generate_cpf_check_digits(self):
        full = generate_cpf_check_digits("529982247")
        assert full == "52998224725"

    def test_generate_cpf_invalid_base(self):
        with pytest.raises(ValueError):
            generate_cpf_check_digits("12345")


# ---------------------------------------------------------------------------
# CNPJ tests (traditional numeric)
# ---------------------------------------------------------------------------

class TestCNPJNumericValidation:
    """Test traditional numeric CNPJ validation."""

    def test_valid_cnpj(self):
        # Known valid CNPJ: 11.222.333/0001-81
        result = validate_cnpj("11222333000181")
        assert result["valid"] is True
        assert result["is_alphanumeric"] is False

    def test_valid_cnpj_formatted(self):
        result = validate_cnpj("11.222.333/0001-81")
        assert result["valid"] is True

    def test_invalid_cnpj_wrong_check_digit(self):
        result = validate_cnpj("11222333000182")
        assert result["valid"] is False

    def test_invalid_cnpj_all_same_digits(self):
        result = validate_cnpj("11111111111111")
        assert result["valid"] is False

    def test_invalid_cnpj_too_short(self):
        result = validate_cnpj("1234567")
        assert result["valid"] is False

    def test_format_cnpj(self):
        assert format_cnpj("11222333000181") == "11.222.333/0001-81"

    def test_generate_cnpj_check_digits(self):
        full = generate_cnpj_check_digits("112223330001")
        assert full == "11222333000181"


# ---------------------------------------------------------------------------
# CNPJ tests (new alphanumeric format - July 2026)
# ---------------------------------------------------------------------------

class TestCNPJAlphanumericValidation:
    """
    Test the new alphanumeric CNPJ format.
    Reference example from Serpro/Receita Federal:
    Base: 12ABC34501DE -> CNPJ: 12ABC34501DE35
    """

    def test_alphanumeric_cnpj_example(self):
        """
        Validate the reference example from Receita Federal:
        12.ABC.345/01DE-35

        First check digit calculation:
        Weights:  [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        Values:   [1, 2, 17, 18, 19, 3, 4, 5, 0, 1, 20, 21]
        Products: [5, 8, 51, 36, 171, 24, 28, 30, 0, 4, 60, 42]
        Sum = 459, 459 % 11 = 8, check = 11 - 8 = 3
        """
        result = validate_cnpj("12ABC34501DE35")
        assert result["valid"] is True
        assert result["is_alphanumeric"] is True

    def test_alphanumeric_cnpj_formatted(self):
        result = validate_cnpj("12.ABC.345/01DE-35")
        assert result["valid"] is True
        assert result["is_alphanumeric"] is True

    def test_alphanumeric_cnpj_lowercase(self):
        """Should accept lowercase and convert to upper."""
        result = validate_cnpj("12abc34501de35")
        assert result["valid"] is True

    def test_alphanumeric_cnpj_wrong_check(self):
        result = validate_cnpj("12ABC34501DE99")
        assert result["valid"] is False

    def test_alphanumeric_check_digits_must_be_numeric(self):
        result = validate_cnpj("12ABC34501DEAB")
        assert result["valid"] is False
        assert "numeric" in result["message"].lower()

    def test_is_alphanumeric_detection(self):
        assert is_alphanumeric_cnpj("12ABC34501DE35") is True
        assert is_alphanumeric_cnpj("11222333000181") is False

    def test_generate_alphanumeric_check_digits(self):
        full = generate_cnpj_check_digits("12ABC34501DE")
        assert full == "12ABC34501DE35"

    def test_generate_alphanumeric_invalid_base(self):
        with pytest.raises(ValueError):
            generate_cnpj_check_digits("12ABC")  # too short

    def test_various_alphanumeric_roundtrip(self):
        """Generate check digits, then validate — must always pass."""
        bases = ["AA0000000001", "ZZ9999990001", "A1B2C3D4E5F6", "0000000000AB"]
        for base in bases:
            full = generate_cnpj_check_digits(base)
            result = validate_cnpj(full)
            assert result["valid"] is True, f"Roundtrip failed for base {base}: {result}"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_string_cpf(self):
        result = validate_cpf("")
        assert result["valid"] is False

    def test_empty_string_cnpj(self):
        result = validate_cnpj("")
        assert result["valid"] is False

    def test_whitespace_handling(self):
        result = validate_cpf("  529.982.247-25  ")
        assert result["valid"] is True

    def test_special_chars_stripped(self):
        result = validate_cnpj("11.222.333/0001-81")
        assert result["valid"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
