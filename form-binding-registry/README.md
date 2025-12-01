# Form Binding Registry

This registry contains form-to-instrument binding specifications that map platform-specific form fields to canonical instrument items.

## Structure

```
form-binding-registry/
└── bindings/
    └── example_intake/
        └── 1-0-0.json
```

## Versioning

Each binding spec is versioned using SemVer (e.g., `1.0.0` stored as `1-0-0.json`).

## Schema

All binding specs must validate against `schemas/form_binding_spec.schema.json`.

## Binding Types

Bindings can match form fields to instrument items using:
- `field_key`: Match by platform-specific field identifier (e.g., `entry.123456`)
- `position`: Match by field position in the form (1-indexed)

## Available Bindings

| ID | Form | Instruments | Version |
|----|------|-------------|---------|
| example_intake | googleforms::1FAIpQLSe_example | PHQ-9, GAD-7 | 1.0.0 |
