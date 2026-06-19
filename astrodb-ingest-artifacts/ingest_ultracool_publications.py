# Ingest the UltracoolSheet References tab into the Publications table.
# Uses ignore_ads=True since bibcodes and titles come from the workbook itself.
import logging
import sys

import pandas as pd
from astrodb_utils import build_db_from_json
from astrodb_utils.publications import ingest_publication

sys.stdout.reconfigure(encoding="utf-8")
logging.getLogger("astrodb_utils").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format="%(levelname)s - %(message)s")

SAVE_DB = False  # set True only after a clean dry run

db = build_db_from_json(settings_file="database.toml")

refs = pd.read_excel("ultracool_sheet.xlsx", sheet_name="References", header=0)
logger.info(f"Loaded {len(refs)} references from the References tab")

added = skipped = 0
errors = []
for _, row in refs.iterrows():
    code = str(row["code_ref"]).strip()
    if not code or code == "nan":
        continue
    bibcode = str(row["ADSkey_ref"]).strip()
    if bibcode in ("nan", "null", ""):
        bibcode = None
    title = str(row["title_ref"]).strip()
    if title in ("nan", "null", ""):
        title = None
    if title and len(title) > 100:
        title = title[:97] + "..."
    try:
        ingest_publication(
            db,
            reference=code,
            bibcode=bibcode,
            description=title,
            ignore_ads=True,
        )
        added += 1
    except Exception as e:
        skipped += 1
        errors.append((code, str(e)))

logger.info(f"Done: {added} ingested, {skipped} skipped out of {len(refs)} rows")
for code, e in errors[:20]:
    logger.warning(f"  {code}: {e}")

if SAVE_DB:
    db.save_database(directory="data/")
    logger.info("Database saved to data/")
else:
    logger.info("Dry run complete — NOT saved. Set SAVE_DB = True to write the database to JSON files.")
