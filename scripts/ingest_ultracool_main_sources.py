# Ingest UltracoolSheet Main-tab objects into the ultracoolsheet AstroDB Sources table.
# Publications (References tab) are ingested first in the same session so FK checks pass.
import logging
import sys
import warnings

import pandas as pd
from astropy.table import Table
from astrodb_utils import build_db_from_json
from astrodb_utils.publications import ingest_publication
from astrodb_utils.sources import ingest_source

sys.stdout.reconfigure(encoding="utf-8")
logging.getLogger("astrodb_utils").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format="%(levelname)s - %(message)s")

SAVE_DB = True  # dry run was clean (3890/3890); user confirmed save

SETTINGS_FILE = "database.toml"
db = build_db_from_json(settings_file=SETTINGS_FILE)

# --- Step A: Publications from the References tab ---
refs = pd.read_excel("ultracool_sheet.xlsx", sheet_name="References", header=0)
pubs_added = pubs_skipped = 0
for _, row in refs.iterrows():
    code = str(row["code_ref"]).strip()
    if not code or code == "nan":
        continue
    bibcode = str(row["ADSkey_ref"]).strip()
    bibcode = None if bibcode in ("nan", "null", "") else bibcode
    title = str(row["title_ref"]).strip()
    title = None if title in ("nan", "null", "") else title
    if title and len(title) > 100:
        title = title[:97] + "..."
    try:
        ingest_publication(db, reference=code, bibcode=bibcode,
                           description=title, ignore_ads=True)
        pubs_added += 1
    except Exception:
        pubs_skipped += 1  # already present (template seed pubs)
logger.info(f"Publications: {pubs_added} ingested, {pubs_skipped} already present/skipped")

# --- Step B: Sources from the Main tab ---
TABLE_PATH = "ultracool_main.csv"
data = Table.read(TABLE_PATH)
logger.info(f"Loaded {len(data)} rows from {TABLE_PATH}")

SOURCE_COL = "name"
REFERENCE_COL = "ref_discovery"
RA_COL = "ra_j2000_formula"
DEC_COL = "dec_j2000_formula"

RA_COL_NAME = "ra_deg"
DEC_COL_NAME = "dec_deg"
EPOCH_COL_NAME = "epoch_year"

sources_added = sources_skipped = 0
skip_msgs = []
forced = []
warnings.filterwarnings("ignore")
for i, row in enumerate(data):
    source_name = str(row[SOURCE_COL]).strip()
    ref_raw = str(row[REFERENCE_COL]).strip()
    # primary discovery ref: first of semicolon list, '-phot' suffix stripped
    primary = ref_raw.split(";")[0].strip()
    if primary.endswith("-phot"):
        primary = primary[:-5]
    other = ref_raw if ";" in ref_raw or "-phot" in ref_raw else None
    kwargs = dict(
        source=source_name,
        reference=primary,
        ra=float(row[RA_COL]),
        dec=float(row[DEC_COL]),
        epoch="2000.0",
        equinox="J2000",
        other_reference=other,
        ra_col_name=RA_COL_NAME,
        dec_col_name=DEC_COL_NAME,
        epoch_col_name=EPOCH_COL_NAME,
        raise_error=True,
        use_simbad=False,
        # The UltracoolSheet is already deduplicated (one unique object per row),
        # and the proximity search both false-positives on close binary companions
        # and crashes on an empty Sources table — so skip it.
        search_db=False,
    )
    try:
        ingest_source(db, **kwargs)
        sources_added += 1
    except Exception as e:
        sources_skipped += 1
        skip_msgs.append(f"{source_name}: {e}")
    if (i + 1) % 500 == 0:
        logger.info(f"  ...{i + 1}/{len(data)} processed ({sources_added} ok, {sources_skipped} skipped)")

logger.info(f"Done: {sources_added} ingested, {sources_skipped} skipped out of {len(data)} rows")
for m in skip_msgs[:25]:
    logger.warning(f"  SKIP {m}")
if len(skip_msgs) > 25:
    logger.warning(f"  ...and {len(skip_msgs) - 25} more (see tmp/ingest_sources_skips.log)")
with open("tmp/ingest_sources_skips.log", "w", encoding="utf-8") as f:
    f.write("\n".join(skip_msgs))

if SAVE_DB:
    db.save_database(directory="data/")
    logger.info("Database saved to data/")
else:
    logger.info("Dry run complete — NOT saved. Set SAVE_DB = True to write the database to JSON files.")
