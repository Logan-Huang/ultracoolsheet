# Ingest all UltracoolSheet Main-tab measurements into the ultracoolsheet AstroDB:
# lookup tables, Photometry, Parallaxes, ProperMotions, RadialVelocities,
# SourceTypes, Associations, ModeledParameters, CompanionRelationships, Positions.
import logging
import sys

import numpy as np
import pandas as pd
from sqlalchemy import insert
from astrodb_utils import build_db_from_json
from astrodb_utils.photometry import ingest_photometry_filter

sys.stdout.reconfigure(encoding="utf-8")
logging.getLogger("astrodb_utils").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format="%(levelname)s - %(message)s")

SAVE_DB = True  # dry run was clean (~99.5k rows); user authorized full ingestion

db = build_db_from_json(settings_file="database.toml")
conn = db.engine.connect()

df = pd.read_csv("ultracool_main.csv", na_values=["null"], low_memory=False)
logger.info(f"Loaded {len(df)} rows")

pubs = {r[0] for r in conn.execute(db.metadata.tables["Publications"].select().with_only_columns(
    db.metadata.tables["Publications"].c.reference)).fetchall()}
logger.info(f"{len(pubs)} publications in DB")

dropped = {}  # reason -> count

def clean_ref(val):
    """First code of a ;-separated list, '-phot' suffix stripped; None if not in Publications."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None
    code = str(val).split(";")[0].strip()
    if code.endswith("-phot"):
        code = code[:-5]
    return code if code in pubs else None

# ============ LOOKUP TABLES ============

# --- Telescopes ---
tel_tbl = db.metadata.tables["Telescopes"]
existing_tel = {r[0] for r in conn.execute(tel_tbl.select().with_only_columns(tel_tbl.c.telescope))}
new_tels = [
    {"telescope": "PS1", "description": "Pan-STARRS1 1.8m survey telescope, Haleakala", "reference": None},
    {"telescope": "Spitzer", "description": "Spitzer Space Telescope", "reference": None},
    {"telescope": "UKIRT", "description": "United Kingdom Infrared Telescope, Maunakea", "reference": None},
]
new_tels = [t for t in new_tels if t["telescope"] not in existing_tel]
if new_tels:
    conn.execute(insert(tel_tbl), new_tels)
logger.info(f"Telescopes added: {[t['telescope'] for t in new_tels]}")

# --- PhotometryFilters (SVO fetch, manual fallback) ---
pf_tbl = db.metadata.tables["PhotometryFilters"]
existing_bands = {r[0] for r in conn.execute(pf_tbl.select().with_only_columns(pf_tbl.c.band))}
# (telescope, instrument, filter) -> manual fallback (ucd, eff_wavelength_A, width_A)
WANTED_FILTERS = [
    ("PAN-STARRS", "PS1", "g", ("em.opt.B", 4866.0, 1180.0)),
    ("PAN-STARRS", "PS1", "r", ("em.opt.R", 6215.0, 1400.0)),
    ("PAN-STARRS", "PS1", "i", ("em.opt.I", 7545.0, 1290.0)),
    ("PAN-STARRS", "PS1", "z", ("em.opt.I", 8679.0, 1040.0)),
    ("PAN-STARRS", "PS1", "y", ("em.opt.I", 9633.0, 630.0)),
    ("UKIRT", "WFCAM", "Y", ("em.IR.NIR", 10310.0, 1020.0)),
    ("MKO", "NSFCam", "J", ("em.IR.J", 12500.0, 1600.0)),
    ("MKO", "NSFCam", "H", ("em.IR.H", 16350.0, 2900.0)),
    ("MKO", "NSFCam", "K", ("em.IR.K", 22000.0, 3400.0)),
    ("MKO", "NSFCam", "Lp", ("em.IR.3-4um", 37700.0, 7000.0)),
    ("MKO", "NSFCam", "Mp", ("em.IR.4-8um", 46800.0, 2400.0)),
    ("Spitzer", "IRAC", "I1", ("em.IR.3-4um", 35500.0, 7430.0)),
    ("Spitzer", "IRAC", "I2", ("em.IR.4-8um", 44930.0, 10100.0)),
]
filters_added, filters_manual = [], []
for tel, inst, filt, fallback in WANTED_FILTERS:
    band_id = f"{tel}/{inst}.{filt}"
    if band_id in existing_bands:
        continue
    try:
        ingest_photometry_filter(db, telescope=tel, instrument=inst, filter_name=filt)
        filters_added.append(band_id)
    except Exception:
        ucd, wave, width = fallback
        conn.execute(insert(pf_tbl), [{"band": band_id, "ucd": ucd,
                                       "effective_wavelength_angstroms": wave,
                                       "width_angstroms": width}])
        filters_manual.append(band_id)
logger.info(f"Filters via SVO: {filters_added}")
logger.info(f"Filters manual fallback: {filters_manual}")

# --- ParameterList ---
pl_tbl = db.metadata.tables["ParameterList"]
existing_params = {r[0] for r in conn.execute(pl_tbl.select().with_only_columns(pl_tbl.c.parameter))}
if "distance" not in existing_params:
    conn.execute(insert(pl_tbl), [{"parameter": "distance", "description": "Distance to the source"}])
    logger.info("ParameterList: added 'distance'")

# --- AssociationList (BANYAN hypotheses with prob >= 0.8) ---
assoc_mask = df["banyan_sigma_max_prob_young"] >= 0.8
assoc_names = sorted(df.loc[assoc_mask, "banyan_sigma_max_hypo_young"].dropna().unique())
al_tbl = db.metadata.tables["AssociationList"]
existing_assoc = {r[0] for r in conn.execute(al_tbl.select().with_only_columns(al_tbl.c.association))}
new_assoc = [{"association": a, "association_type": "moving group",
              "comments": "BANYAN Sigma hypothesis name", "reference": None}
             for a in assoc_names if a not in existing_assoc]
if new_assoc:
    conn.execute(insert(al_tbl), new_assoc)
logger.info(f"AssociationList: {len(new_assoc)} added ({assoc_mask.sum()} sources with prob>=0.8)")

# --- SourceTypeList ---
def clean_spt(val):
    s = str(val).strip()
    unc = None
    if s.endswith("::"):
        s, unc = s[:-2].strip(), "2-subtype uncertainty"
    elif s.endswith(":"):
        s, unc = s[:-1].strip(), "1-subtype uncertainty"
    return s, unc

spt_values = set()
for col in ("spt_opt", "spt_ir"):
    for v in df[col].dropna():
        spt_values.add(clean_spt(v)[0])
stl_tbl = db.metadata.tables["SourceTypeList"]
existing_st = {r[0] for r in conn.execute(stl_tbl.select().with_only_columns(stl_tbl.c.source_type))}
new_st = [{"source_type": s, "comments": None} for s in sorted(spt_values) if s not in existing_st]
if new_st:
    conn.execute(insert(stl_tbl), new_st)
logger.info(f"SourceTypeList: {len(new_st)} added")

# --- CompanionList ---
def clean_companion(val):
    s = str(val).strip()
    if s in ("N", "", "nan"):
        return None, None
    uncertain = s.endswith("?")
    s = s.rstrip("?").strip()
    primary = s.split("/")[0].strip()
    return primary, ("companionship uncertain" if uncertain else None)

companions = {}
for v in df["has_higher_mass_companion"].dropna():
    name, _ = clean_companion(v)
    if name:
        companions[name] = "higher-mass companion (host star)"
for v in df["multiplesystem_resolved_in_this_table"].dropna():
    s = str(v).strip()
    if s == "N" or ":" not in s:
        continue
    name = s.rsplit(":", 1)[0].strip()
    if name:
        companions.setdefault(name, "resolved multiple-system component (also a UCS source)")
cl_tbl = db.metadata.tables["CompanionList"]
existing_comp = {r[0] for r in conn.execute(cl_tbl.select().with_only_columns(cl_tbl.c.companion))}
new_comp = [{"companion": c, "description": d} for c, d in sorted(companions.items())
            if c not in existing_comp]
if new_comp:
    conn.execute(insert(cl_tbl), new_comp)
logger.info(f"CompanionList: {len(new_comp)} added")

# ============ DATA TABLES ============
src = df["name"].astype(str).str.strip()

def bulk(table_name, rows, pk_cols):
    """Dedup on PK columns, then bulk insert."""
    if not rows:
        logger.info(f"{table_name}: 0 rows")
        return 0
    frame = pd.DataFrame(rows).drop_duplicates(subset=pk_cols, keep="first")
    n_dup = len(rows) - len(frame)
    if n_dup:
        dropped[f"{table_name}: PK duplicates"] = n_dup
    recs = frame.replace({np.nan: None}).to_dict("records")
    conn.execute(insert(db.metadata.tables[table_name]), recs)
    logger.info(f"{table_name}: {len(recs)} rows inserted ({n_dup} PK dups dropped)")
    return len(recs)

# --- Photometry ---
PHOT = [
    # mag, err, ref(col or const), band, telescope, regime
    ("g_P1", "gerr_P1", "ref_g_P1", "PAN-STARRS/PS1.g", "PS1", "optical"),
    ("r_P1", "rerr_P1", "ref_r_P1", "PAN-STARRS/PS1.r", "PS1", "optical"),
    ("i_P1", "ierr_P1", "ref_i_P1", "PAN-STARRS/PS1.i", "PS1", "optical"),
    ("z_P1", "zerr_P1", "ref_z_P1", "PAN-STARRS/PS1.z", "PS1", "optical"),
    ("y_P1", "yerr_P1", "ref_y_P1", "PAN-STARRS/PS1.y", "PS1", "optical"),
    ("BP_Gaia", "BPerr_Gaia", "ref_photom_Gaia", "GAIA/GAIA3.Gbp", "Gaia", "optical"),
    ("G_Gaia", "Gerr_Gaia", "ref_photom_Gaia", "GAIA/GAIA3.G", "Gaia", "optical"),
    ("RP_Gaia", "RPerr_Gaia", "ref_photom_Gaia", "GAIA/GAIA3.Grp", "Gaia", "optical"),
    ("J_2MASS", "Jerr_2MASS", "ref_J_2MASS", "2MASS/2MASS.J", "2MASS", "nir"),
    ("H_2MASS", "Herr_2MASS", "ref_H_2MASS", "2MASS/2MASS.H", "2MASS", "nir"),
    ("Ks_2MASS", "Kserr_2MASS", "ref_Ks_2MASS", "2MASS/2MASS.Ks", "2MASS", "nir"),
    ("Y_MKO", "Yerr_MKO", "ref_Y_MKO", "UKIRT/WFCAM.Y", None, "nir"),
    ("J_MKO", "Jerr_MKO", "ref_J_MKO", "MKO/NSFCam.J", None, "nir"),
    ("H_MKO", "Herr_MKO", "ref_H_MKO", "MKO/NSFCam.H", None, "nir"),
    ("K_MKO", "Kerr_MKO", "ref_K_MKO", "MKO/NSFCam.K", None, "nir"),
    ("Lp_MKO", "Lperr_MKO", "ref_Lp_MKO", "MKO/NSFCam.Lp", None, "infrared"),
    ("Mp_MKO", "Mperr_MKO", "ref_Mp_MKO", "MKO/NSFCam.Mp", None, "infrared"),
    ("W1", "W1err", "ref_W1", "WISE/WISE.W1", "WISE", "infrared"),
    ("W2", "W2err", "ref_W2", "WISE/WISE.W2", "WISE", "infrared"),
    ("W3", "W3err", "ref_W3", "WISE/WISE.W3", "WISE", "infrared"),
    ("W4", "W4err", "ref_W4", "WISE/WISE.W4", "WISE", "infrared"),
    ("ch1", "ch1err", "ref_Spitzer", "Spitzer/IRAC.I1", "Spitzer", "infrared"),
    ("ch2", "ch2err", "ref_Spitzer", "Spitzer/IRAC.I2", "Spitzer", "infrared"),
]
phot_rows = []
n_noref = n_upperlim = 0
for mag_c, err_c, ref_c, band, tel, regime in PHOT:
    mags = pd.to_numeric(df[mag_c], errors="coerce")
    errs = pd.to_numeric(df[err_c], errors="coerce")
    for i in np.where(mags.notna())[0]:
        ref = clean_ref(df[ref_c].iloc[i])
        if ref is None:
            n_noref += 1
            continue
        err = errs.iloc[i]
        comments = None
        if pd.isna(err):
            err = None
            comments = "upper limit"
            n_upperlim += 1
        elif err == -999:
            err = None
            comments = "photometry contaminated by brighter host star"
        phot_rows.append({"source": src.iloc[i], "band": band, "magnitude": float(mags.iloc[i]),
                          "magnitude_error": err, "telescope": tel, "regime": regime,
                          "comments": comments, "reference": ref})
dropped["Photometry: no resolvable reference"] = n_noref
bulk("Photometry", phot_rows, ["source", "band", "reference"])
logger.info(f"  (upper limits: {n_upperlim})")

# --- helper for measurement sets with adopted-formula merge ---
def gaia_ref(i):
    return "Gaia23" if pd.notna(df["sourceID_Gaia_DR3"].iloc[i]) else "Gaia18"

def gaia_comment(i):
    return "Gaia astrometry is for the primary star" if str(df["astrom_Gaia"].iloc[i]).strip() == "P" else None

# --- Parallaxes ---
plx_sets = [
    ("plx_lit", "plxerr_lit", lambda i: clean_ref(df["ref_plx_lit"].iloc[i]), None),
    ("plx_UKIRT", "plxerr_UKIRT", lambda i: clean_ref(df["ref_plx_UKIRT"].iloc[i]), None),
    ("plx_Gaia", "plxerr_Gaia", gaia_ref, gaia_comment),
    ("plx_simbad", "plxerr_simbad", lambda i: clean_ref(df["ref_plx_simbad"].iloc[i]), None),
]
plx_rows = {}
for val_c, err_c, ref_fn, com_fn in plx_sets:
    vals = pd.to_numeric(df[val_c], errors="coerce")
    errs = pd.to_numeric(df[err_c], errors="coerce")
    for i in np.where(vals.notna())[0]:
        ref = ref_fn(i)
        if ref is None:
            dropped["Parallaxes: no ref"] = dropped.get("Parallaxes: no ref", 0) + 1
            continue
        key = (src.iloc[i], ref)
        if key not in plx_rows:
            e = errs.iloc[i]
            plx_rows[key] = {"source": key[0], "parallax_mas": float(vals.iloc[i]),
                             "parallax_error": abs(float(e)) if pd.notna(e) else None,
                             "adopted": False, "comments": com_fn(i) if com_fn else None,
                             "reference": ref}
# adopted formula rows: mark matching row, or insert if from a set we don't carry
f_vals = pd.to_numeric(df["plx_formula"], errors="coerce")
f_errs = pd.to_numeric(df["plxerr_formula"], errors="coerce")
for i in np.where(f_vals.notna())[0]:
    ref = clean_ref(df["ref_plx_formula"].iloc[i])
    if ref is None:
        dropped["Parallaxes: adopted no ref"] = dropped.get("Parallaxes: adopted no ref", 0) + 1
        continue
    key = (src.iloc[i], ref)
    if key in plx_rows:
        plx_rows[key]["adopted"] = True
    else:
        e = f_errs.iloc[i]
        plx_rows[key] = {"source": key[0], "parallax_mas": float(f_vals.iloc[i]),
                         "parallax_error": abs(float(e)) if pd.notna(e) else None,
                         "adopted": True, "comments": None, "reference": ref}
bulk("Parallaxes", list(plx_rows.values()), ["source", "reference"])

# --- ProperMotions ---
pm_sets = [
    ("pmra_lit", "pmraerr_lit", "pmdec_lit", "pmdecerr_lit", lambda i: clean_ref(df["ref_pm_lit"].iloc[i]), None),
    ("pmra_UKIRT", "pmraerr_UKIRT", "pmdec_UKIRT", "pmdecerr_UKIRT", lambda i: clean_ref(df["ref_plx_UKIRT"].iloc[i]), None),
    ("pmra_Gaia", "pmraerr_Gaia", "pmdec_Gaia", "pmdecerr_Gaia", gaia_ref, gaia_comment),
    ("pmra_P1", "pmraerr_P1", "pmdec_P1", "pmdecerr_P1", lambda i: clean_ref(df["ref_pm_P1"].iloc[i]), None),
    ("pmra_catwise", "pmraerr_catwise", "pmdec_catwise", "pmdecerr_catwise", lambda i: "Maro21", None),
    ("pmra_simbad", "pmraerr_simbad", "pmdec_simbad", "pmdecerr_simbad", lambda i: clean_ref(df["ref_pm_simbad"].iloc[i]), None),
    ("pmra_P1_PV34", "pmraerr_P1_PV34", "pmdec_P1_PV34", "pmdecerr_P1_PV34", lambda i: clean_ref(df["ref_pm_P1_PV34"].iloc[i]), None),
]
pm_rows = {}
for ra_c, rae_c, de_c, dee_c, ref_fn, com_fn in pm_sets:
    ras = pd.to_numeric(df[ra_c], errors="coerce").replace([np.inf, -np.inf], np.nan)
    des = pd.to_numeric(df[de_c], errors="coerce").replace([np.inf, -np.inf], np.nan)
    raes = pd.to_numeric(df[rae_c], errors="coerce").replace([np.inf, -np.inf], np.nan)
    dees = pd.to_numeric(df[dee_c], errors="coerce").replace([np.inf, -np.inf], np.nan)
    for i in np.where(ras.notna() & des.notna())[0]:
        ref = ref_fn(i)
        if ref is None:
            dropped["ProperMotions: no ref"] = dropped.get("ProperMotions: no ref", 0) + 1
            continue
        key = (src.iloc[i], ref)
        if key not in pm_rows:
            pm_rows[key] = {"source": key[0], "pm_ra": float(ras.iloc[i]),
                            "pm_ra_error": abs(float(raes.iloc[i])) if pd.notna(raes.iloc[i]) else None,
                            "pm_dec": float(des.iloc[i]),
                            "pm_dec_error": abs(float(dees.iloc[i])) if pd.notna(dees.iloc[i]) else None,
                            "adopted": False, "comments": com_fn(i) if com_fn else None,
                            "reference": ref}
f_ra = pd.to_numeric(df["pmra_formula"], errors="coerce")
f_de = pd.to_numeric(df["pmdec_formula"], errors="coerce")
f_rae = pd.to_numeric(df["pmraerr_formula"], errors="coerce")
f_dee = pd.to_numeric(df["pmdecerr_formula"], errors="coerce")
for i in np.where(f_ra.notna() & f_de.notna())[0]:
    ref = clean_ref(df["ref_pm_formula"].iloc[i])
    if ref is None:
        dropped["ProperMotions: adopted no ref"] = dropped.get("ProperMotions: adopted no ref", 0) + 1
        continue
    key = (src.iloc[i], ref)
    if key in pm_rows:
        pm_rows[key]["adopted"] = True
    else:
        pm_rows[key] = {"source": key[0], "pm_ra": float(f_ra.iloc[i]),
                        "pm_ra_error": abs(float(f_rae.iloc[i])) if pd.notna(f_rae.iloc[i]) else None,
                        "pm_dec": float(f_de.iloc[i]),
                        "pm_dec_error": abs(float(f_dee.iloc[i])) if pd.notna(f_dee.iloc[i]) else None,
                        "adopted": True, "comments": None, "reference": ref}
bulk("ProperMotions", list(pm_rows.values()), ["source", "reference"])

# --- RadialVelocities ---
rv_sets = [
    ("rv_lit", "rverr_lit", lambda i: clean_ref(df["ref_rv_lit"].iloc[i])),
    ("rv_Gaia", "rverr_Gaia", lambda i: "Gaia23"),
]
rv_rows = {}
for val_c, err_c, ref_fn in rv_sets:
    vals = pd.to_numeric(df[val_c], errors="coerce")
    errs = pd.to_numeric(df[err_c], errors="coerce")
    for i in np.where(vals.notna())[0]:
        ref = ref_fn(i)
        if ref is None:
            dropped["RadialVelocities: no ref"] = dropped.get("RadialVelocities: no ref", 0) + 1
            continue
        key = (src.iloc[i], ref)
        if key not in rv_rows:
            e = errs.iloc[i]
            rv_rows[key] = {"source": key[0], "rv_kms": float(vals.iloc[i]),
                            "rv_error": abs(float(e)) if pd.notna(e) else None,
                            "adopted": False, "comments": None, "reference": ref}
f_vals = pd.to_numeric(df["rv_formula"], errors="coerce")
f_errs = pd.to_numeric(df["rverr_formula"], errors="coerce")
for i in np.where(f_vals.notna())[0]:
    ref = clean_ref(df["ref_rv_formula"].iloc[i])
    if ref is None:
        dropped["RadialVelocities: adopted no ref"] = dropped.get("RadialVelocities: adopted no ref", 0) + 1
        continue
    key = (src.iloc[i], ref)
    if key in rv_rows:
        rv_rows[key]["adopted"] = True
    else:
        e = f_errs.iloc[i]
        rv_rows[key] = {"source": key[0], "rv_kms": float(f_vals.iloc[i]),
                        "rv_error": abs(float(e)) if pd.notna(e) else None,
                        "adopted": True, "comments": None, "reference": ref}
bulk("RadialVelocities", list(rv_rows.values()), ["source", "reference"])

# --- SourceTypes ---
st_rows = []
for col, ref_col, label in [("spt_opt", "ref_spt_opt", "optical spectral type"),
                            ("spt_ir", "ref_spt_ir", "NIR spectral type")]:
    vals = df[col]
    for i in np.where(vals.notna())[0]:
        ref = clean_ref(df[ref_col].iloc[i])
        if ref is None:
            dropped["SourceTypes: no ref"] = dropped.get("SourceTypes: no ref", 0) + 1
            continue
        stype, unc = clean_spt(vals.iloc[i])
        comments = label + (f"; {unc}" if unc else "")
        st_rows.append({"source": src.iloc[i], "source_type": stype,
                        "comments": comments, "adopted": None, "reference": ref})
bulk("SourceTypes", st_rows, ["source", "source_type", "reference"])

# --- Associations (BANYAN, prob >= 0.8) ---
as_rows = []
for i in np.where(assoc_mask & df["banyan_sigma_max_hypo_young"].notna())[0]:
    com = df["banyan_sigma_input_params"].iloc[i]
    as_rows.append({"source": src.iloc[i],
                    "association": str(df["banyan_sigma_max_hypo_young"].iloc[i]).strip(),
                    "membership_probability": float(df["banyan_sigma_max_prob_young"].iloc[i]),
                    "comments": (f"BANYAN Sigma inputs: {com}" if pd.notna(com) else None),
                    "adopted": None, "reference": "UCS_24"})
bulk("Associations", as_rows, ["source", "association"])

# --- ModeledParameters (age + adopted distance) ---
mp_rows = []
ages = pd.to_numeric(df["age_singlevalue_gyr_formula"], errors="coerce")
for i in np.where(ages.notna())[0]:
    cat = df["age_category"].iloc[i]
    dist = df["age_distribution_gyr_formula"].iloc[i]
    com = "; ".join(x for x in [f"age_category: {cat}" if pd.notna(cat) else None,
                                f"age range (Gyr): {dist}" if pd.notna(dist) else None] if x)
    mp_rows.append({"source": src.iloc[i], "model": "UCS age assignment", "parameter": "age",
                    "value": float(ages.iloc[i]), "error": None, "unit": "Gyr",
                    "comments": com or None, "reference": "UCS_24"})
dists = pd.to_numeric(df["dist_formula"], errors="coerce")
dist_errs = pd.to_numeric(df["disterr_formula"], errors="coerce")
for i in np.where(dists.notna())[0]:
    srccom = df["dist_formula_source"].iloc[i]
    e = dist_errs.iloc[i]
    mp_rows.append({"source": src.iloc[i], "model": "UCS adopted distance", "parameter": "distance",
                    "value": float(dists.iloc[i]),
                    "error": abs(float(e)) if pd.notna(e) else None, "unit": "pc",
                    "comments": (f"distance source: {srccom}" if pd.notna(srccom) else None),
                    "reference": "UCS_24"})
bulk("ModeledParameters", mp_rows, ["source", "model", "parameter", "reference"])

# --- CompanionRelationships ---
cr_rows = []
seps = pd.to_numeric(df["sep_companion"], errors="coerce")
for i in np.where(df["has_higher_mass_companion"].notna())[0]:
    name, unc_com = clean_companion(df["has_higher_mass_companion"].iloc[i])
    if name is None:
        continue
    raw = str(df["has_higher_mass_companion"].iloc[i]).strip()
    other = raw if "/" in raw else None
    sep = seps.iloc[i]
    cr_rows.append({"source": src.iloc[i], "companion": name, "relationship": "host star",
                    "projected_separation_arcsec": float(sep) if pd.notna(sep) else None,
                    "comments": unc_com, "reference": "UCS_24", "other_companion_names": other})
for i in np.where(df["multiplesystem_resolved_in_this_table"].notna())[0]:
    s = str(df["multiplesystem_resolved_in_this_table"].iloc[i]).strip()
    if s == "N" or ":" not in s:
        continue
    name, refs_part = s.rsplit(":", 1)
    name = name.strip()
    ref = clean_ref(refs_part) or "UCS_24"
    cr_rows.append({"source": src.iloc[i], "companion": name,
                    "relationship": "resolved multiple-system component",
                    "projected_separation_arcsec": None, "comments": None,
                    "reference": ref, "other_companion_names": None})
bulk("CompanionRelationships", cr_rows, ["source", "companion"])

# --- Positions (observed-epoch survey positions) ---
def mjd_to_year(mjd):
    return 2000.0 + (mjd - 51544.5) / 365.25

def date_to_year(s):
    try:
        ts = pd.Timestamp(str(s))
        return ts.year + (ts.dayofyear - 1) / 365.25
    except (ValueError, TypeError):
        return None

pos_rows = {}
mjds = pd.to_numeric(df["epoch_mjd_P1"], errors="coerce")
POS_SETS = [
    ("ra_epoch_P1", "dec_epoch_P1",
     lambda i: clean_ref(df["ref_radec_P1"].iloc[i]),
     lambda i: mjd_to_year(mjds.iloc[i]) if pd.notna(mjds.iloc[i]) else None),
    ("ra_epoch_2mass", "dec_epoch_2mass",
     lambda i: "Cutr03",
     lambda i: date_to_year(df["epoch_2mass"].iloc[i])),
    ("ra_epoch_WISE", "dec_epoch_WISE",
     lambda i: clean_ref(df["ref_astrom_WISE"].iloc[i]),
     lambda i: 2015.405 if str(df["ref_astrom_WISE"].iloc[i]).startswith("Maro21") else 2010.5589),
    ("ra_epoch_Gaia", "dec_epoch_Gaia",
     gaia_ref,
     lambda i: 2016.0 if pd.notna(df["sourceID_Gaia_DR3"].iloc[i]) else 2015.5),
    ("ra_j2000_simbad", "dec_j2000_simbad",
     lambda i: clean_ref(df["ref_radec_j2000_simbad"].iloc[i]),
     lambda i: 2000.0),
]
for ra_c, de_c, ref_fn, ep_fn in POS_SETS:
    ras = pd.to_numeric(df[ra_c], errors="coerce")
    des = pd.to_numeric(df[de_c], errors="coerce")
    ok = ras.notna() & des.notna() & (ras >= 0) & (ras <= 360) & (des >= -90) & (des <= 90)
    for i in np.where(ok)[0]:
        ref = ref_fn(i)
        if ref is None:
            dropped["Positions: no ref"] = dropped.get("Positions: no ref", 0) + 1
            continue
        key = (src.iloc[i], ref)
        if key not in pos_rows:  # PK (source, reference) — first survey wins
            pos_rows[key] = {"source": key[0], "ra_deg": float(ras.iloc[i]),
                             "dec_deg": float(des.iloc[i]), "epoch_year": ep_fn(i),
                             "reference": ref}
bulk("Positions", list(pos_rows.values()), ["source", "reference"])

conn.commit()
logger.info("Transaction committed to sqlite")
logger.info(f"Dropped-row summary: {dropped}")

if SAVE_DB:
    db.save_database(directory="data/")
    logger.info("Database saved to data/")
else:
    logger.info("Dry run complete — NOT saved. Set SAVE_DB = True to write the database to JSON files.")
