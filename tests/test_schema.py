"""Tests for schema module."""

import json
import pytest
from docextract.schema import Schema, SchemaField, FieldType, SchemaTemplates


class TestSchemaField:
    """Test cases for SchemaField."""

    def test_string_validation(self):
        field = SchemaField("name", FieldType.STRING, required=True)
        assert field.validate("John") == (True, None)
        assert field.validate(None) == (False, "Field 'name' is required")
        assert field.validate(123) == (False, "Field 'name' must be a string")

    def test_string_pattern(self):
        field = SchemaField("code", FieldType.STRING, pattern=r"^[A-Z]{3}\d{3}$")
        assert field.validate("ABC123") == (True, None)
        assert field.validate("abc123")[0] == False

    def test_string_enum(self):
        field = SchemaField("status", FieldType.STRING, enum=["active", "inactive"])
        assert field.validate("active") == (True, None)
        assert field.validate("pending")[0] == False

    def test_integer_validation(self):
        field = SchemaField("age", FieldType.INTEGER, min_value=0, max_value=150)
        assert field.validate(25) == (True, None)
        assert field.validate(-1)[0] == False
        assert field.validate(200)[0] == False
        assert field.validate("25")[0] == False

    def test_float_validation(self):
        field = SchemaField("price", FieldType.FLOAT, min_value=0)
        assert field.validate(19.99) == (True, None)
        assert field.validate(-1.0)[0] == False

    def test_boolean_validation(self):
        field = SchemaField("active", FieldType.BOOLEAN)
        assert field.validate(True) == (True, None)
        assert field.validate(False) == (True, None)
        assert field.validate("true")[0] == False

    def test_email_validation(self):
        field = SchemaField("email", FieldType.EMAIL)
        assert field.validate("test@example.com") == (True, None)
        assert field.validate("invalid")[0] == False
        assert field.validate("test@")[0] == False

    def test_url_validation(self):
        field = SchemaField("website", FieldType.URL)
        assert field.validate("https://example.com") == (True, None)
        assert field.validate("not-a-url")[0] == False

    def test_phone_validation(self):
        field = SchemaField("phone", FieldType.PHONE)
        assert field.validate("+1-234-567-8900") == (True, None)
        assert field.validate("123")[0] == False

    def test_date_validation(self):
        field = SchemaField("date", FieldType.DATE)
        assert field.validate("2024-01-15") == (True, None)
        assert field.validate("15/01/2024") == (True, None)
        assert field.validate("not-a-date")[0] == False

    def test_currency_validation(self):
        field = SchemaField("amount", FieldType.CURRENCY)
        assert field.validate("$1,234.56") == (True, None)
        assert field.validate(100) == (True, None)
        assert field.validate("invalid")[0] == False

    def test_list_validation(self):
        field = SchemaField("items", FieldType.LIST, item_type=FieldType.STRING)
        assert field.validate(["a", "b", "c"]) == (True, None)
        assert field.validate("not-a-list")[0] == False

    def test_object_validation(self):
        nested = Schema("Nested").add_field(SchemaField("name", FieldType.STRING))
        field = SchemaField("data", FieldType.OBJECT, nested_schema=nested)
        assert field.validate({"name": "test"}) == (True, None)
        assert field.validate("not-an-object")[0] == False

    def test_optional_field(self):
        field = SchemaField("optional", FieldType.STRING, required=False)
        assert field.validate(None) == (True, None)
        assert field.validate("value") == (True, None)

    def test_to_dict(self):
        field = SchemaField("test", FieldType.STRING, description="A test field")
        d = field.to_dict()
        assert d["name"] == "test"
        assert d["type"] == "string"
        assert d["description"] == "A test field"

    def test_from_dict(self):
        data = {"name": "test", "type": "string", "description": "A test", "required": True}
        field = SchemaField.from_dict(data)
        assert field.name == "test"
        assert field.field_type == FieldType.STRING


class TestSchema:
    """Test cases for Schema."""

    def test_basic_validation(self):
        schema = Schema("Test").add_field(SchemaField("name", FieldType.STRING))
        is_valid, errors = schema.validate({"name": "John"})
        assert is_valid == True
        assert errors == []

    def test_missing_required_field(self):
        schema = Schema("Test").add_field(SchemaField("name", FieldType.STRING, required=True))
        is_valid, errors = schema.validate({})
        assert is_valid == False
        assert len(errors) == 1

    def test_unknown_field(self):
        schema = Schema("Test").add_field(SchemaField("name", FieldType.STRING))
        is_valid, errors = schema.validate({"name": "John", "extra": "value"})
        assert is_valid == False
        assert "Unknown field 'extra'" in errors

    def test_serialization(self):
        schema = Schema("Test", "A test schema").add_field(SchemaField("name", FieldType.STRING))
        json_str = schema.to_json()
        restored = Schema.from_json(json_str)
        assert restored.name == "Test"
        assert restored.description == "A test schema"
        assert len(restored.fields) == 1

    def test_generate_prompt(self):
        schema = Schema("Invoice").add_field(SchemaField("total", FieldType.CURRENCY))
        prompt = schema.generate_prompt()
        assert "Invoice" in prompt
        assert "total" in prompt
        assert "Return ONLY a valid JSON" in prompt


class TestSchemaTemplates:
    """Test cases for built-in schema templates."""

    def test_invoice_schema(self):
        schema = SchemaTemplates.invoice()
        assert schema.name == "Invoice"
        field_names = [f.name for f in schema.fields]
        assert "invoice_number" in field_names
        assert "total_amount" in field_names
        assert "line_items" in field_names

    def test_resume_schema(self):
        schema = SchemaTemplates.resume()
        assert schema.name == "Resume"
        field_names = [f.name for f in schema.fields]
        assert "full_name" in field_names
        assert "skills" in field_names
        assert "work_experience" in field_names

    def test_receipt_schema(self):
        schema = SchemaTemplates.receipt()
        assert schema.name == "Receipt"
        field_names = [f.name for f in schema.fields]
        assert "merchant" in field_names
        assert "items" in field_names

    def test_business_card_schema(self):
        schema = SchemaTemplates.business_card()
        assert schema.name == "BusinessCard"
        field_names = [f.name for f in schema.fields]
        assert "name" in field_names
        assert "email" in field_names

    def test_contract_schema(self):
        schema = SchemaTemplates.contract()
        assert schema.name == "Contract"
        field_names = [f.name for f in schema.fields]
        assert "parties" in field_names
        assert "contract_value" in field_names
