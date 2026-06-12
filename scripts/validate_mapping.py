# Validate the UltracoolSheet -> AstroDB schema mapping:
# nullable violations and type mismatches against schema.yaml.
import re
import sys

import numpy as np
import pandas as pd
import yaml

sys.stdout.reconfigure(encoding="utf-8")

MATCH_MD = "tmp/schema-match-result.md"
DATA = "ultracool_main.csv"
SCHEMA = "schema.yaml"

# --- parse mapping from match-result markdown ---
mapping = []  # (col, table, field, conf)
pat = re.compile(r"\| `([^`]+)` \| .* \| → (\w+) \| `([^`]+)` \| (🟢|🟡|🔴) ")
for line in open(MATCH_MD, encoding="utf-8"):
    if not line.startswith("| `"):
        continue
    cells = [c.strip() for c in line.split(" | ")]
    col = cells[0].lstrip("| ").strip("`")
    table = cells[4]
    field = cells[5].strip("`")
    if table.startswith("→ "):
        mapping.append((col, table[2:], field))
print(f"Mapped columns to validate: {len(mapping)}")

# --- parse schema.yaml ---
schema = yaml.safe_load(open(SCHEMA, encoding="utf-8"))
schema_fields = {}
for tbl in schema.get("tables", []):
    tname = tbl["name"]
    schema_fields[tname] = {}
    for c in tbl.get("columns", []):
        schema_fields[tname][c["name"]] = {
            "datatype": c.get("datatype"),
            "nullable": c.get("nullable", True),
            "length": c.get("length"),
        }
print(f"Schema tables: {sorted(schema_fields)}")

# --- load data (pandas; treat 'null' sentinel strings as NA per UltracoolSheet docs) ---
df = pd.read_csv(DATA, na_values=["null", "NaN", ""], keep_default_na=True, low_memory=False)
n_rows = len(df)

COMPAT = {
    "string": ("object", "str"),
    "double": ("float64", "float32", "float16", "int64", "int32"),
    "float": ("float64", "float32", "int64", "int32"),
    "int": ("int64", "int32", "int16", "int8"),
    "long": ("int64", "int32"),
    "boolean": ("bool",),
    "timestamp": ("datetime64", "object", "str"),
}

def effective_dtype(s):
    d = str(s.dtype)
    if d != "object":
        return d
    # object column: if all non-null values parse as float, call it float64
    vals = s.dropna()
    if len(vals) == 0:
        return "object"
    try:
        pd.to_numeric(vals)
        return "float64"
    except (ValueError, TypeError):
        return "object"

null_violations = []
type_mismatches = []
clean = []
warnings = []

for col, table, field in mapping:
    if col not in df.columns:
        warnings.append(f"Column `{col}` not found in data file")
        continue
    if table not in schema_fields:
        warnings.append(f"Table `{table}` not in schema.yaml (mapping for `{col}`)")
        continue
    if field not in schema_fields[table]:
        warnings.append(f"Field `{table}.{field}` not in schema.yaml (mapping for `{col}`)")
        continue
    spec = schema_fields[table][field]
    s = df[col]
    nulls = int(s.isna().sum())
    if str(s.dtype) == "object":
        nulls += int((s.astype(str).str.strip() == "").sum())
    dt = effective_dtype(s)

    ok = True
    if not spec["nullable"] and nulls > 0:
        null_violations.append((col, f"{table}.{field}", nulls, n_rows, 100 * nulls / n_rows))
        ok = False
    exp = spec["datatype"]
    compat_list = COMPAT.get(exp, ())
    compatible = dt in compat_list or (dt == "object" and exp == "string")
    if not compatible:
        type_mismatches.append((col, dt, f"{table}.{field}", exp))
        ok = False
    if ok:
        clean.append((col, f"{table}.{field}", nulls))

# all-null columns among mapped
all_null = [c for c, t, f in mapping if c in df.columns and df[c].isna().all()]

# --- report ---
out = []
out.append("## Schema Mapping Validation Report")
out.append(f"Source: `{DATA}` → `{SCHEMA}`")
out.append("Date: 2026-06-12\n")

out.append(f"### Nullable Violations  ({len(null_violations)} issues)")
if null_violations:
    out.append("| Data Column | Maps To | Null Count | Total Rows | % Null |")
    out.append("|---|---|---|---|---|")
    for c, mf, n, tot, pct in null_violations:
        out.append(f"| `{c}` | {mf} | {n} | {tot} | {pct:.1f}% |")
else:
    out.append("None.")
out.append("")

out.append(f"### Type Mismatches  ({len(type_mismatches)} issues)")
if type_mismatches:
    out.append("| Data Column | Data Type | Maps To | Expected Type | Compatible? |")
    out.append("|---|---|---|---|---|")
    for c, dt, mf, exp in type_mismatches:
        out.append(f"| `{c}` | {dt} | {mf} | {exp} | ❌ No |")
else:
    out.append("None.")
out.append("")

out.append(f"### Clean Mappings  ({len(clean)} columns OK)")
out.append("<details><summary>Expand</summary>\n")
for c, mf, n in clean:
    out.append(f"- `{c}` → {mf}" + (f" ({n} nulls, field nullable)" if n else ""))
out.append("\n</details>\n")

if warnings:
    out.append(f"### Warnings  ({len(warnings)})")
    for w in warnings:
        out.append(f"- {w}")
    out.append("")

if all_null:
    out.append("### All-null mapped columns")
    for c in all_null:
        out.append(f"- `{c}`")
    out.append("")

out.append("### Summary")
out.append(f"- {len(null_violations)} nullable violations found (columns with nulls in non-nullable fields)")
out.append(f"- {len(type_mismatches)} type mismatches found")
out.append(f"- {len(clean)} columns passed validation cleanly")
out.append("")
out.append("**Next steps:**")
out.append("- For nullable violations: filter out null rows before ingest (standard practice — a missing measurement simply produces no row in that data table), fill with a default, or relax the schema field.")
out.append("- For type mismatches: add a type-cast step in the ingestion script.")
out.append("- Note: data was loaded treating the literal string 'null' as missing, per UltracoolSheet conventions. Sentinel values (-999 in PS1 errors, 'Inf' in PS1 proper motions) must additionally be cleaned at ingest time.")

report = "\n".join(out)
with open("tmp/schema-validation-report.md", "w", encoding="utf-8") as f:
    f.write(report)

print(f"\nNullable violations: {len(null_violations)}")
print(f"Type mismatches: {len(type_mismatches)}")
print(f"Clean: {len(clean)}")
print(f"Warnings: {len(warnings)}")
for w in warnings:
    print("  WARN:", w)
if null_violations:
    for c, mf, n, tot, pct in null_violations[:20]:
        print(f"  NULLVIO: {c} -> {mf}: {n}/{tot} ({pct:.1f}%)")
if type_mismatches:
    for c, dt, mf, exp in type_mismatches[:30]:
        print(f"  TYPE: {c} ({dt}) -> {mf} expects {exp}")
print("Report: tmp/schema-validation-report.md")
