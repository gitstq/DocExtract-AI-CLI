"""
Schema Definition Module
Defines extraction schemas with field types, validation rules, and constraints.
"""

import json
import re
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class FieldType(Enum):
    """Supported field types for extraction."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    EMAIL = "email"
    URL = "url"
    PHONE = "phone"
    CURRENCY = "currency"
    LIST = "list"
    OBJECT = "object"


class SchemaField:
    """Represents a single field in an extraction schema."""

    def __init__(
        self,
        name: str,
        field_type: FieldType,
        description: str = "",
        required: bool = True,
        default: Any = None,
        pattern: Optional[str] = None,
        enum: Optional[List[str]] = None,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        item_type: Optional[FieldType] = None,
        nested_schema: Optional["Schema"] = None,
    ):
        self.name = name
        self.field_type = field_type
        self.description = description
        self.required = required
        self.default = default
        self.pattern = pattern
        self.enum = enum
        self.min_value = min_value
        self.max_value = max_value
        self.item_type = item_type
        self.nested_schema = nested_schema

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """Validate a value against this field's constraints."""
        if value is None:
            if self.required:
                return False, f"Field '{self.name}' is required"
            return True, None

        validators = {
            FieldType.STRING: self._validate_string,
            FieldType.INTEGER: self._validate_integer,
            FieldType.FLOAT: self._validate_float,
            FieldType.BOOLEAN: self._validate_boolean,
            FieldType.DATE: self._validate_date,
            FieldType.EMAIL: self._validate_email,
            FieldType.URL: self._validate_url,
            FieldType.PHONE: self._validate_phone,
            FieldType.CURRENCY: self._validate_currency,
            FieldType.LIST: self._validate_list,
            FieldType.OBJECT: self._validate_object,
        }

        validator = validators.get(self.field_type)
        if validator:
            return validator(value)
        return True, None

    def _validate_string(self, value: Any) -> tuple[bool, Optional[str]]:
        if not isinstance(value, str):
            return False, f"Field '{self.name}' must be a string"
        if self.pattern and not re.match(self.pattern, value):
            return False, f"Field '{self.name}' does not match pattern '{self.pattern}'"
        if self.enum and value not in self.enum:
            return False, f"Field '{self.name}' must be one of {self.enum}"
        return True, None

    def _validate_integer(self, value: Any) -> tuple[bool, Optional[str]]:
        if not isinstance(value, int) or isinstance(value, bool):
            return False, f"Field '{self.name}' must be an integer"
        if self.min_value is not None and value < self.min_value:
            return False, f"Field '{self.name}' must be >= {self.min_value}"
        if self.max_value is not None and value > self.max_value:
            return False, f"Field '{self.name}' must be <= {self.max_value}"
        return True, None

    def _validate_float(self, value: Any) -> tuple[bool, Optional[str]]:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False, f"Field '{self.name}' must be a number"
        if self.min_value is not None and value < self.min_value:
            return False, f"Field '{self.name}' must be >= {self.min_value}"
        if self.max_value is not None and value > self.max_value:
            return False, f"Field '{self.name}' must be <= {self.max_value}"
        return True, None

    def _validate_boolean(self, value: Any) -> tuple[bool, Optional[str]]:
        if not isinstance(value, bool):
            return False, f"Field '{self.name}' must be a boolean"
        return True, None

    def _validate_date(self, value: Any) -> tuple[bool, Optional[str]]:
        if not isinstance(value, str):
            return False, f"Field '{self.name}' must be a date string"
        # Accept ISO 8601 and common formats
        date_patterns = [
            r"^\d{4}-\d{2}-\d{2}$",
            r"^\d{4}/\d{2}/\d{2}$",
            r"^\d{2}-\d{2}-\d{4}$",
            r"^\d{2}/\d{2}/\d{4}$",
        ]
        if not any(re.match(p, value) for p in date_patterns):
            return False, f"Field '{self.name}' must be a valid date"
        return True, None

    def _validate_email(self, value: Any) -> tuple[bool, Optional[str]]:
        if not isinstance(value, str):
            return False, f"Field '{self.name}' must be a string"
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, value):
            return False, f"Field '{self.name}' must be a valid email"
        return True, None

    def _validate_url(self, value: Any) -> tuple[bool, Optional[str]]:
        if not isinstance(value, str):
            return False, f"Field '{self.name}' must be a string"
        pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        if not re.match(pattern, value, re.IGNORECASE):
            return False, f"Field '{self.name}' must be a valid URL"
        return True, None

    def _validate_phone(self, value: Any) -> tuple[bool, Optional[str]]:
        if not isinstance(value, str):
            return False, f"Field '{self.name}' must be a string"
        # Remove common separators and validate
        cleaned = re.sub(r"[\s\-\(\)\.]", "", value)
        if not re.match(r"^\+?[\d]{7,15}$", cleaned):
            return False, f"Field '{self.name}' must be a valid phone number"
        return True, None

    def _validate_currency(self, value: Any) -> tuple[bool, Optional[str]]:
        if not isinstance(value, (int, float, str)):
            return False, f"Field '{self.name}' must be a currency value"
        if isinstance(value, str):
            # Accept formats like "$1,234.56", "€100", "1,234.56 USD"
            pattern = r"^[\$\€\£\¥]?\s*[\d,]+\.?\d*\s*[A-Z]{0,3}$"
            if not re.match(pattern, value.strip()):
                return False, f"Field '{self.name}' must be a valid currency"
        return True, None

    def _validate_list(self, value: Any) -> tuple[bool, Optional[str]]:
        if not isinstance(value, list):
            return False, f"Field '{self.name}' must be a list"
        if self.item_type:
            for i, item in enumerate(value):
                field = SchemaField(f"{self.name}[{i}]", self.item_type)
                valid, error = field.validate(item)
                if not valid:
                    return False, error
        return True, None

    def _validate_object(self, value: Any) -> tuple[bool, Optional[str]]:
        if not isinstance(value, dict):
            return False, f"Field '{self.name}' must be an object"
        if self.nested_schema:
            is_valid, errors = self.nested_schema.validate(value)
            if not is_valid:
                return False, errors[0] if errors else "Validation failed"
        return True, None

    def to_dict(self) -> Dict[str, Any]:
        """Convert field to dictionary representation."""
        result = {
            "name": self.name,
            "type": self.field_type.value,
            "description": self.description,
            "required": self.required,
        }
        if self.default is not None:
            result["default"] = self.default
        if self.pattern:
            result["pattern"] = self.pattern
        if self.enum:
            result["enum"] = self.enum
        if self.min_value is not None:
            result["min_value"] = self.min_value
        if self.max_value is not None:
            result["max_value"] = self.max_value
        if self.item_type:
            result["item_type"] = self.item_type.value
        if self.nested_schema:
            result["nested_schema"] = self.nested_schema.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SchemaField":
        """Create a SchemaField from a dictionary."""
        nested = None
        if "nested_schema" in data:
            nested = Schema.from_dict(data["nested_schema"])
        return cls(
            name=data["name"],
            field_type=FieldType(data["type"]),
            description=data.get("description", ""),
            required=data.get("required", True),
            default=data.get("default"),
            pattern=data.get("pattern"),
            enum=data.get("enum"),
            min_value=data.get("min_value"),
            max_value=data.get("max_value"),
            item_type=FieldType(data["item_type"]) if "item_type" in data else None,
            nested_schema=nested,
        )


class Schema:
    """Defines a complete extraction schema with multiple fields."""

    def __init__(self, name: str, description: str = "", fields: Optional[List[SchemaField]] = None):
        self.name = name
        self.description = description
        self.fields = fields or []

    def add_field(self, field: SchemaField) -> "Schema":
        """Add a field to the schema."""
        self.fields.append(field)
        return self

    def validate(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate extracted data against this schema."""
        errors = []
        field_names = {f.name for f in self.fields}

        # Check for unknown fields
        for key in data:
            if key not in field_names:
                errors.append(f"Unknown field '{key}'")

        # Validate each field
        for field in self.fields:
            value = data.get(field.name)
            valid, error = field.validate(value)
            if not valid:
                errors.append(error)

        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "fields": [f.to_dict() for f in self.fields],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Schema":
        """Create a Schema from a dictionary."""
        schema = cls(
            name=data["name"],
            description=data.get("description", ""),
        )
        for field_data in data.get("fields", []):
            schema.add_field(SchemaField.from_dict(field_data))
        return schema

    def to_json(self, indent: int = 2) -> str:
        """Serialize schema to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "Schema":
        """Deserialize schema from JSON string."""
        return cls.from_dict(json.loads(json_str))

    def generate_prompt(self) -> str:
        """Generate an AI prompt describing this schema for extraction."""
        lines = [
            f"Extract the following information from the document:",
            f"Schema: {self.name}",
            f"Description: {self.description}",
            "",
            "Fields to extract:",
        ]
        for field in self.fields:
            req = "(required)" if field.required else "(optional)"
            desc = f" - {field.description}" if field.description else ""
            lines.append(f"  - {field.name}: {field.field_type.value} {req}{desc}")
            if field.enum:
                lines.append(f"    Allowed values: {', '.join(field.enum)}")
            if field.pattern:
                lines.append(f"    Pattern: {field.pattern}")
        lines.extend([
            "",
            "Return ONLY a valid JSON object with the field names as keys.",
            "If a field cannot be found, set its value to null.",
        ])
        return "\n".join(lines)


# Pre-built schema templates
class SchemaTemplates:
    """Collection of pre-built extraction schemas for common use cases."""

    @staticmethod
    def invoice() -> Schema:
        """Schema for invoice extraction."""
        return (
            Schema("Invoice", "Standard invoice document extraction")
            .add_field(SchemaField("invoice_number", FieldType.STRING, "Invoice identifier"))
            .add_field(SchemaField("issue_date", FieldType.DATE, "Invoice issue date"))
            .add_field(SchemaField("due_date", FieldType.DATE, "Payment due date", required=False))
            .add_field(SchemaField("vendor_name", FieldType.STRING, "Company issuing the invoice"))
            .add_field(SchemaField("vendor_address", FieldType.STRING, "Vendor address", required=False))
            .add_field(SchemaField("customer_name", FieldType.STRING, "Customer name"))
            .add_field(SchemaField("subtotal", FieldType.CURRENCY, "Subtotal before tax"))
            .add_field(SchemaField("tax_amount", FieldType.CURRENCY, "Tax amount", required=False))
            .add_field(SchemaField("total_amount", FieldType.CURRENCY, "Total amount due"))
            .add_field(SchemaField("currency", FieldType.STRING, "Currency code (USD, EUR, etc.)", required=False))
            .add_field(SchemaField("line_items", FieldType.LIST, "List of line items", item_type=FieldType.OBJECT,
                                   nested_schema=Schema("LineItem").add_field(
                                       SchemaField("description", FieldType.STRING, "Item description")
                                   ).add_field(
                                       SchemaField("quantity", FieldType.FLOAT, "Quantity")
                                   ).add_field(
                                       SchemaField("unit_price", FieldType.CURRENCY, "Price per unit")
                                   ).add_field(
                                       SchemaField("total", FieldType.CURRENCY, "Line total")
                                   )))
        )

    @staticmethod
    def resume() -> Schema:
        """Schema for resume/CV extraction."""
        return (
            Schema("Resume", "Resume or CV document extraction")
            .add_field(SchemaField("full_name", FieldType.STRING, "Person's full name"))
            .add_field(SchemaField("email", FieldType.EMAIL, "Contact email"))
            .add_field(SchemaField("phone", FieldType.PHONE, "Contact phone", required=False))
            .add_field(SchemaField("location", FieldType.STRING, "City, Country", required=False))
            .add_field(SchemaField("summary", FieldType.STRING, "Professional summary", required=False))
            .add_field(SchemaField("skills", FieldType.LIST, "List of skills", item_type=FieldType.STRING))
            .add_field(SchemaField("experience_years", FieldType.INTEGER, "Total years of experience", required=False))
            .add_field(SchemaField("education", FieldType.LIST, "Education history", required=False, item_type=FieldType.OBJECT,
                                   nested_schema=Schema("Education").add_field(
                                       SchemaField("degree", FieldType.STRING, "Degree name")
                                   ).add_field(
                                       SchemaField("institution", FieldType.STRING, "School/University")
                                   ).add_field(
                                       SchemaField("year", FieldType.STRING, "Graduation year", required=False)
                                   )))
            .add_field(SchemaField("work_experience", FieldType.LIST, "Work history", required=False, item_type=FieldType.OBJECT,
                                   nested_schema=Schema("WorkExperience").add_field(
                                       SchemaField("company", FieldType.STRING, "Company name")
                                   ).add_field(
                                       SchemaField("title", FieldType.STRING, "Job title")
                                   ).add_field(
                                       SchemaField("duration", FieldType.STRING, "Employment period", required=False)
                                   )))
        )

    @staticmethod
    def receipt() -> Schema:
        """Schema for receipt extraction."""
        return (
            Schema("Receipt", "Purchase receipt extraction")
            .add_field(SchemaField("merchant", FieldType.STRING, "Store or merchant name"))
            .add_field(SchemaField("date", FieldType.DATE, "Purchase date"))
            .add_field(SchemaField("time", FieldType.STRING, "Purchase time", required=False))
            .add_field(SchemaField("total", FieldType.CURRENCY, "Total amount paid"))
            .add_field(SchemaField("payment_method", FieldType.STRING, "Payment method", required=False))
            .add_field(SchemaField("items", FieldType.LIST, "Purchased items", item_type=FieldType.OBJECT,
                                   nested_schema=Schema("ReceiptItem").add_field(
                                       SchemaField("name", FieldType.STRING, "Item name")
                                   ).add_field(
                                       SchemaField("price", FieldType.CURRENCY, "Item price")
                                   ).add_field(
                                       SchemaField("quantity", FieldType.INTEGER, "Quantity", required=False, default=1)
                                   )))
        )

    @staticmethod
    def business_card() -> Schema:
        """Schema for business card extraction."""
        return (
            Schema("BusinessCard", "Business card information extraction")
            .add_field(SchemaField("name", FieldType.STRING, "Person's name"))
            .add_field(SchemaField("title", FieldType.STRING, "Job title", required=False))
            .add_field(SchemaField("company", FieldType.STRING, "Company name", required=False))
            .add_field(SchemaField("email", FieldType.EMAIL, "Email address", required=False))
            .add_field(SchemaField("phone", FieldType.PHONE, "Phone number", required=False))
            .add_field(SchemaField("mobile", FieldType.PHONE, "Mobile number", required=False))
            .add_field(SchemaField("website", FieldType.URL, "Company website", required=False))
            .add_field(SchemaField("address", FieldType.STRING, "Physical address", required=False))
        )

    @staticmethod
    def contract() -> Schema:
        """Schema for contract extraction."""
        return (
            Schema("Contract", "Legal contract key information extraction")
            .add_field(SchemaField("contract_type", FieldType.STRING, "Type of contract"))
            .add_field(SchemaField("parties", FieldType.LIST, "Contracting parties", item_type=FieldType.STRING))
            .add_field(SchemaField("effective_date", FieldType.DATE, "Contract effective date"))
            .add_field(SchemaField("expiration_date", FieldType.DATE, "Contract expiration date", required=False))
            .add_field(SchemaField("contract_value", FieldType.CURRENCY, "Total contract value", required=False))
            .add_field(SchemaField("governing_law", FieldType.STRING, "Governing law jurisdiction", required=False))
            .add_field(SchemaField("termination_clause", FieldType.BOOLEAN, "Has termination clause", required=False))
            .add_field(SchemaField("key_terms", FieldType.LIST, "Key contract terms", required=False, item_type=FieldType.STRING))
        )
