"""Pydantic models for instrument and binding specifications."""

from typing import Literal

from pydantic import BaseModel, Field


class Interpretation(BaseModel):
    """Score interpretation band."""

    min: int
    max: int
    label: str
    severity: int | None = None
    description: str | None = None


class InstrumentScale(BaseModel):
    """Scale definition within an instrument."""

    scale_id: str
    name: str
    items: list[str]
    method: Literal["sum", "average", "sum_then_double"]
    reversed_items: list[str] = Field(default_factory=list)
    min: int | None = None
    max: int | None = None
    missing_allowed: int = 0
    interpretations: list[Interpretation]


class InstrumentItem(BaseModel):
    """Item (question) definition within an instrument."""

    item_id: str
    position: int
    text: str
    response_map: dict[str, int]
    aliases: dict[str, str] = Field(default_factory=dict)


class InstrumentSpec(BaseModel):
    """Complete instrument specification."""

    type: Literal["instrument_spec"]
    instrument_id: str
    version: str
    name: str
    kind: Literal["questionnaire", "scale", "inventory", "checklist"]
    locale: str | None = None
    aliases: list[str] = Field(default_factory=list)
    description: str | None = None
    items: list[InstrumentItem]
    scales: list[InstrumentScale]

    def get_item(self, item_id: str) -> InstrumentItem | None:
        """Get an item by its ID."""
        for item in self.items:
            if item.item_id == item_id:
                return item
        return None

    def get_scale(self, scale_id: str) -> InstrumentScale | None:
        """Get a scale by its ID."""
        for scale in self.scales:
            if scale.scale_id == scale_id:
                return scale
        return None


class Binding(BaseModel):
    """Single item binding mapping form field to instrument item."""

    item_id: str
    by: Literal["field_key", "position"]
    value: str | int


class BindingSection(BaseModel):
    """Section of bindings for a single instrument."""

    name: str | None = None
    instrument_id: str
    instrument_version: str
    bindings: list[Binding]


class FormBindingSpec(BaseModel):
    """Complete form binding specification."""

    type: Literal["form_binding_spec"]
    form_id: str
    binding_id: str
    version: str
    description: str | None = None
    sections: list[BindingSection]

    def get_section_for_instrument(self, instrument_id: str) -> BindingSection | None:
        """Get the binding section for a specific instrument."""
        for section in self.sections:
            if section.instrument_id == instrument_id:
                return section
        return None
