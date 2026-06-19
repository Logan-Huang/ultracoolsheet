# Parse the UltracoolSheet Main tab CSV and extract column info,
# enriching descriptions/units from the README tab of the source workbook.
import json
import os
import sys

import pandas as pd
from astropy.table import Table

sys.stdout.reconfigure(encoding="utf-8")

CSV_PATH = "ultracool_main.csv"
XLSX_PATH = "ultracool_sheet.xlsx"

# --- Step 2: read the data file ---
reader = None
pandas_method = None
try:
    t = Table.read(CSV_PATH)
    reader = "astropy"
    n_rows = len(t)
    columns = [(c, t[c].dtype) for c in t.columns]
except Exception:
    df = pd.read_csv(CSV_PATH)
    reader = "pandas"
    pandas_method = "read_csv"
    n_rows = len(df)
    columns = [(c, df[c].dtype) for c in df.columns]

os.makedirs("tmp", exist_ok=True)
with open("tmp/astrodb-parse-result.json", "w") as f:
    json.dump({
        "file_path": os.path.abspath(CSV_PATH),
        "reader": reader,
        "format": "csv",
        "pandas_method": pandas_method,
        "n_rows": n_rows,
    }, f)

# --- Step 3: extract metadata from README tab ---
rd = pd.read_excel(XLSX_PATH, sheet_name="README", header=None)

# The Main section starts after the "Main" header row in COLUMN DESCRIPTIONS.
# It ends at the next tab section header (Binaries, Triples+, etc.).
tab_names = {"Binaries", "Triples+", "AgeValues", "FundamentalProperties",
             "References", "Main - In Progress"}
start = None
for i, row in rd.iterrows():
    if str(row[0]).strip() == "Main" and i > 90:
        start = i + 1
        break

meta = {}  # colname -> (unit, description)
for i in range(start, len(rd)):
    name = rd.iloc[i, 0]
    if pd.isna(name):
        continue
    name = str(name).strip()
    if name in tab_names:
        break
    unit = rd.iloc[i, 1]
    desc = rd.iloc[i, 2]
    unit = str(unit).strip() if pd.notna(unit) else ""
    desc = str(desc).strip() if pd.notna(desc) else ""
    meta[name] = (unit, desc)

print(f"README Main-section entries: {len(meta)}")

def dtype_str(dt):
    s = str(dt)
    if s.startswith(("<U", ">U", "|S", "object", "str")):
        return "str"
    return s.replace(">", "").replace("<", "")

def clean(text):
    return " ".join(str(text).split()).replace("|", "\\|")

rows = []
missing_desc = 0
missing_unit = 0
for col, dt in columns:
    unit, desc = meta.get(col, ("", ""))
    # inference for uncertainty columns
    if not desc:
        base = None
        if col.endswith("err") or "err_" in col:
            base = col.replace("err", "", 1)
        if base and base in meta and meta[base][1]:
            desc = f"Uncertainty on {base}"
            if not unit:
                unit = meta[base][0]
    if not desc:
        missing_desc += 1
    if not unit:
        missing_unit += 1
    rows.append((col, clean(desc) if desc else "—",
                 clean(unit) if unit else "—", dtype_str(dt)))

# --- Step 5: output ---
outdir = "astrodb-build-artifacts/ultracool_main-parsed-data-table"
n = 0
base_outdir = outdir
while os.path.exists(outdir):
    n += 1
    outdir = f"{base_outdir}-{n}"
os.makedirs(outdir)

header = f"""# Column Information: ultracool_main.csv

**File:** `ultracool_main.csv`
**Format:** csv
**Reader:** {reader}
**Rows:** {n_rows}
**Columns:** {len(columns)}

"""

notes = [
    "Descriptions and units were extracted from the README tab of the UltracoolSheet workbook (v2.1.0), which documents every Main-tab column.",
    "Source spreadsheet: The UltracoolSheet (Best et al.), Main tab — complete-data objects only.",
    f"{missing_desc} columns have no description; {missing_unit} columns have no units (most are dimensionless flags, names, or reference strings).",
    "Cells with no data contain the string 'null' or NaN per UltracoolSheet conventions.",
]

md = header + "| Column | Description | Units | Type |\n|--------|-------------|-------|------|\n"
for col, desc, unit, dt in rows:
    md += f"| `{col}` | {desc} | {unit} | {dt} |\n"
md += "\n## Notes\n\n" + "\n".join(f"- {x}" for x in notes) + "\n"

md_path = os.path.join(outdir, "ultracool_main-parsed-data-table.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write(md)

html_rows = "\n".join(
    f"<tr><td><code>{col}</code></td><td>{desc.replace(chr(92)+'|','|')}</td><td>{unit}</td><td>{dt}</td></tr>"
    for col, desc, unit, dt in rows)
html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Column Information: ultracool_main.csv</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ccc; padding: 4px 8px; text-align: left; vertical-align: top; }}
th {{ background: #f0f0f0; position: sticky; top: 0; }}
tr:nth-child(even) {{ background: #fafafa; }}
code {{ background: #eef; padding: 1px 4px; border-radius: 3px; }}
</style></head><body>
<h1>Column Information: ultracool_main.csv</h1>
<p><b>File:</b> <code>ultracool_main.csv</code><br>
<b>Format:</b> csv<br><b>Reader:</b> {reader}<br>
<b>Rows:</b> {n_rows}<br><b>Columns:</b> {len(columns)}</p>
<table><thead><tr><th>Column</th><th>Description</th><th>Units</th><th>Type</th></tr></thead>
<tbody>{html_rows}</tbody></table>
<h2>Notes</h2><ul>{"".join(f"<li>{x}</li>" for x in notes)}</ul>
</body></html>"""

html_path = os.path.join(outdir, "ultracool_main-parsed-data-table.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

with open("tmp/astrodb-parse-result.json") as f:
    sidecar = json.load(f)
sidecar["output_md"] = os.path.abspath(md_path)
sidecar["output_html"] = os.path.abspath(html_path)
with open("tmp/astrodb-parse-result.json", "w") as f:
    json.dump(sidecar, f)

print(f"Wrote {md_path} and {html_path}")
print(f"missing descriptions: {missing_desc}, missing units: {missing_unit}")
