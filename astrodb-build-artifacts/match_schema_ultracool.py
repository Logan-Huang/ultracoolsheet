# Generate the AstroDB schema match outputs (markdown + HTML) for the
# UltracoolSheet Main tab, mapping each column to the astrodb-template schema.
import datetime
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

PARSED_MD = "astrodb-build-artifacts/ultracool_main-parsed-data-table/ultracool_main-parsed-data-table.md"

# --- load parsed column info ---
cols = {}  # name -> (desc, units, dtype)
order = []
for line in open(PARSED_MD, encoding="utf-8"):
    m = re.match(r"\| `([^`]+)` \| (.*) \| (.*) \| (\w+) \|", line)
    if m:
        name, desc, units, dtype = m.groups()
        cols[name] = (desc.strip(), units.strip(), dtype.strip())
        order.append(name)
assert len(order) == 242, len(order)

H, M, L, U = "High", "Medium", "Low", "Unmatched"

# mapping: column -> (DB Table, DB Field, Confidence, Notes)
MAP = {}

def add(col, table, field, conf, notes):
    assert col in cols, col
    assert col not in MAP, col
    MAP[col] = (table, field, conf, notes)

# --- identifiers & core source info ---
add("name", "Sources", "source", H, "Primary identifier; first column, unique per object")
add("name_simbadable", "Names", "other_name", H, "SIMBAD-queryable alternate name")
add("ref_discovery", "Sources", "reference", H, "Discovery reference; all ref codes also populate Publications")
add("ra_j2000_formula", "Sources", "ra_deg", H, "Adopted RA (equinox J2000, epoch 2000.0)")
add("dec_j2000_formula", "Sources", "dec_deg", H, "Adopted Dec (equinox J2000, epoch 2000.0)")
add("source_j2000_formula", "Sources", "comments", M, "Provenance of adopted position (DR3/DR2, PS1, CatWISE, UKIDSS, SIMBAD)")
add("glon_j2000", None, None, U, "Derived galactic longitude; recomputable from ra/dec — suggest skip")
add("glat_j2000", None, None, U, "Derived galactic latitude; recomputable from ra/dec — suggest skip")
add("note", "Sources", "comments", H, "Miscellaneous per-object notes")
add("firstref_simbad", "Sources", "other_references", L, "First reference record from SIMBAD")

# --- alternate names ---
for c, n in [("designation_P1_formula", "Pan-STARRS1 DR2 designation"),
             ("designation_2mass", "2MASS designation"),
             ("designation_MKO", "MKO-catalog designation (ULAS/VHS/VIKING)"),
             ("designation_WISE", "CatWISE2020/AllWISE designation"),
             ("name_simbad", "SIMBAD main designation"),
             ("name_simpleDB", "SIMPLE archive name")]:
    add(c, "Names", "other_name", H, n)
add("identifiers_simbad", "Names", "other_name", H, "All SIMBAD identifiers; split on '|' → one Names row each")
add("sourceID_Gaia_DR3", "Names", "other_name", M, "Store as 'Gaia DR3 <id>'")
add("sourceID_Gaia_DR2", "Names", "other_name", M, "Store as 'Gaia DR2 <id>'")
add("gucds_shortname", "Names", "other_name", M, "Gaia UCD Survey shortname")

# --- flags / quality: unmatched, ask user ---
add("literature_flag", None, None, U, "Literature info flag (subd, lowg, YMG claims…); options: Sources.comments, row filtering, or skip")
add("ref_literature_flag", None, None, U, "References paired with literature_flag")
add("exoplanet", None, None, U, "Planetary-mass flag (Y/Y?/N?/N); options: Sources.comments or CompanionParameters, or skip")
add("Best21_vollim_sample", None, None, U, "Best et al. (2021) volume-limited sample membership flag; options: Sources.comments or skip")
add("Best24_vollim_sample", None, None, U, "Best et al. (2024) volume-limited sample membership flag; options: Sources.comments or skip")
add("nb_AllWISE", None, None, U, "PSF-fit component count (quality); suggest skip")
add("neigh_AllWISE", None, None, U, "Neighbor count within 8 arcsec (quality); suggest skip")
add("RUWE_Gaia", None, None, U, "Gaia astrometric quality statistic; suggest skip or Sources.comments")
add("nep_Gaia", None, None, U, "Gaia visibility periods used (quality); suggest skip")
add("flags_Gaia", None, None, U, "Gaia DR3 catalog flags (quality); suggest skip")
add("url_simpleDB", None, None, U, "Generic URL to SIMPLE archive page; options: Sources.comments or skip")

# --- multiplicity / companions ---
add("multiplesystem_unresolved_in_this_table", "Sources", "comments", L, "Unresolved-multiple flag with discovery refs; no dedicated field")
add("multiplesystem_resolved_in_this_table", "CompanionRelationships", "companion", M, "Wide-companion name + discovery ref; relationship='resolved multiple'")
add("has_higher_mass_companion", "CompanionRelationships", "companion", H, "Host-star name; relationship='companion of higher-mass star'")
add("sep_companion", "CompanionRelationships", "projected_separation_arcsec", H, "Separation from higher-mass companion; 0 = unresolved")

# --- age / youth ---
add("youth_evidence", "Sources", "comments", L, "Qualitative youth-evidence flag (lowg, YMG, SFR…)")
add("age_category", "Associations", "association", M, "Moving-group / age category (BPMG, TWA…); strip '!'/'?' suffixes; non-group entries need handling")
add("age_category_justification", "Associations", "comments", M, "Justification text for age_category")
add("age_singlevalue_gyr_formula", "ModeledParameters", "value", H, "parameter='age', unit='Gyr'")
add("age_distribution_gyr_formula", "ModeledParameters", "comments", L, "Age-range string for the age parameter row")

# --- Positions (multi-epoch, multi-survey) ---
pos = [
    ("ra_j2000_P1", "ra_deg", H, "PS1 position propagated to epoch 2000"),
    ("dec_j2000_P1", "dec_deg", H, "PS1 position propagated to epoch 2000"),
    ("ra_epoch_P1", "ra_deg", H, "PS1 observed-epoch position (epoch from epoch_mjd_P1)"),
    ("dec_epoch_P1", "dec_deg", H, "PS1 observed-epoch position"),
    ("epoch_mjd_P1", "epoch_year", H, "MJD → decimal year conversion required"),
    ("ref_radec_P1", "reference", H, "Reference for PS1 astrometry"),
    ("ra_epoch_2mass", "ra_deg", H, "2MASS observed-epoch position"),
    ("dec_epoch_2mass", "dec_deg", H, "2MASS observed-epoch position"),
    ("epoch_2mass", "epoch_year", M, "UT date string → decimal year conversion required"),
    ("ra_j2000_WISE", "ra_deg", H, "CatWISE/AllWISE position at epoch 2000"),
    ("dec_j2000_WISE", "dec_deg", H, "CatWISE/AllWISE position at epoch 2000"),
    ("ra_epoch_WISE", "ra_deg", H, "CatWISE epoch 2015.405 / AllWISE epoch 2010.5589"),
    ("dec_epoch_WISE", "dec_deg", H, "CatWISE epoch 2015.405 / AllWISE epoch 2010.5589"),
    ("ref_astrom_WISE", "reference", H, "Reference for WISE astrometry"),
    ("ra_j2000_Gaia", "ra_deg", H, "Gaia position at epoch 2000"),
    ("dec_J2000_Gaia", "dec_deg", H, "Gaia position at epoch 2000 (note capital J in column name)"),
    ("ra_epoch_Gaia", "ra_deg", H, "Gaia DR2 epoch 2015.5 / DR3 epoch 2016.0"),
    ("dec_epoch_Gaia", "dec_deg", H, "Gaia DR2 epoch 2015.5 / DR3 epoch 2016.0"),
    ("ra_j2000_simbad", "ra_deg", H, "SIMBAD J2000 position"),
    ("dec_j2000_simbad", "dec_deg", H, "SIMBAD J2000 position"),
    ("ref_radec_j2000_simbad", "reference", H, "Reference for SIMBAD coordinates"),
]
for c, f, conf, n in pos:
    add(c, "Positions", f, conf, n)
add("ra_20250703_formula", None, None, U, "Present-epoch RA; recomputable from J2000 position + PM — suggest skip")
add("dec_20250703_formula", None, None, U, "Present-epoch Dec; recomputable — suggest skip")
add("source_radec_20250703_formula", None, None, U, "Provenance of present-epoch coords; suggest skip with the above")
add("astrom_Gaia", "Parallaxes", "comments", L, "O=object / P=primary-star astrometry; carry into Gaia Parallaxes & ProperMotions comments")

# --- Photometry ---
phot = [
    # (mag col, err col, ref col, SVO band, extra note)
    ("g_P1", "gerr_P1", "ref_g_P1", "PAN-STARRS/PS1.g", "-999 err = contaminated by host star"),
    ("r_P1", "rerr_P1", "ref_r_P1", "PAN-STARRS/PS1.r", "-999 err = contaminated"),
    ("i_P1", "ierr_P1", "ref_i_P1", "PAN-STARRS/PS1.i", "-999 err = contaminated"),
    ("z_P1", "zerr_P1", "ref_z_P1", "PAN-STARRS/PS1.z", "-999 err = contaminated"),
    ("y_P1", "yerr_P1", "ref_y_P1", "PAN-STARRS/PS1.y", "-999 err = contaminated"),
    ("BP_Gaia", "BPerr_Gaia", "ref_photom_Gaia", "GAIA/GAIA3.Gbp", ""),
    ("G_Gaia", "Gerr_Gaia", None, "GAIA/GAIA3.G", "reference = ref_photom_Gaia"),
    ("RP_Gaia", "RPerr_Gaia", None, "GAIA/GAIA3.Grp", "reference = ref_photom_Gaia"),
    ("J_2MASS", "Jerr_2MASS", "ref_J_2MASS", "2MASS/2MASS.J", "NaN err = upper limit"),
    ("H_2MASS", "Herr_2MASS", "ref_H_2MASS", "2MASS/2MASS.H", "NaN err = upper limit"),
    ("Ks_2MASS", "Kserr_2MASS", "ref_Ks_2MASS", "2MASS/2MASS.Ks", "NaN err = upper limit"),
    ("Y_MKO", "Yerr_MKO", "ref_Y_MKO", "UKIRT/WFCAM.Y", "confirm SVO ID — MKO Y mostly UKIDSS/VISTA"),
    ("J_MKO", "Jerr_MKO", "ref_J_MKO", "MKO/NSFCam.J", "MKO system"),
    ("H_MKO", "Herr_MKO", "ref_H_MKO", "MKO/NSFCam.H", "MKO system"),
    ("K_MKO", "Kerr_MKO", "ref_K_MKO", "MKO/NSFCam.K", "MKO system"),
    ("Lp_MKO", "Lperr_MKO", "ref_Lp_MKO", "MKO/NSFCam.Lp", "MKO system"),
    ("Mp_MKO", "Mperr_MKO", "ref_Mp_MKO", "MKO/NSFCam.Mp", "MKO system"),
    ("W1", "W1err", "ref_W1", "WISE/WISE.W1", "CatWISE preferred over AllWISE; NaN err = upper limit"),
    ("W2", "W2err", "ref_W2", "WISE/WISE.W2", "CatWISE preferred; NaN err = upper limit"),
    ("W3", "W3err", "ref_W3", "WISE/WISE.W3", "AllWISE; NaN err = upper limit"),
    ("W4", "W4err", "ref_W4", "WISE/WISE.W4", "AllWISE; NaN err = upper limit"),
    ("ch1", "ch1err", None, "Spitzer/IRAC.I1", "reference = ref_Spitzer"),
    ("ch2", "ch2err", None, "Spitzer/IRAC.I2", "reference = ref_Spitzer"),
]
for mag, err, ref, band, note in phot:
    conf = M if "confirm" in note else H
    add(mag, "Photometry", "magnitude", conf, f"band={band}" + (f"; {note}" if note else ""))
    add(err, "Photometry", "magnitude_error", conf, f"Uncertainty for band {band}")
    if ref:
        add(ref, "Photometry", "reference", H, f"Reference for {band}")
add("ref_Spitzer", "Photometry", "reference", H, "Reference for Spitzer/IRAC.I1 and I2")

# PS1 per-band quality columns
for b in "grizy":
    add(f"{b}_nphot_P1", "Photometry", "comments", L, f"Epoch count for PS1 {b}; quality info — or skip")
    add(f"{b}_src_P1", "Photometry", "comments", L, f"PS1 {b} photometry source code (C/R/W/X); quality info — or skip")
add("Cflg_2MASS", "Photometry", "comments", L, "2MASS contamination flag (cc_flg); quality info — or skip")
add("flag_WISE", "Photometry", "comments", L, "CatWISE/AllWISE contamination flags; quality info — or skip")
for b in ("W1", "W2", "W3", "W4"):
    add(f"chi2_{b}", None, None, U, f"Reduced chi^2 of {b} profile fit (quality); suggest skip")

# --- Parallaxes ---
plx = [
    ("plx_formula", "parallax_mas", H, "Adopted parallax → adopted=True"),
    ("plxerr_formula", "parallax_error", H, "Uncertainty in adopted parallax"),
    ("ref_plx_formula", "reference", H, "Reference for adopted parallax"),
    ("plx_lit", "parallax_mas", H, "Literature parallax (non-Gaia/PS1/UKIRT)"),
    ("plxerr_lit", "parallax_error", H, ""),
    ("ref_plx_lit", "reference", H, ""),
    ("plx_UKIRT", "parallax_mas", H, "Best et al. UKIRT program parallax"),
    ("plxerr_UKIRT", "parallax_error", H, ""),
    ("plx_Gaia", "parallax_mas", H, "Gaia DR2/DR3 parallax; reference from sourceID columns"),
    ("plxerr_Gaia", "parallax_error", H, ""),
    ("plx_simbad", "parallax_mas", H, "SIMBAD parallax"),
    ("plxerr_simbad", "parallax_error", H, ""),
    ("ref_plx_simbad", "reference", H, ""),
]
for c, f, conf, n in plx:
    add(c, "Parallaxes", f, conf, n)
add("ref_plx_UKIRT", "Parallaxes", "reference", H, "Also reference for UKIRT proper motion")

# --- ProperMotions ---
pm = [
    ("pmra_formula", "pm_ra", H, "Adopted PM → adopted=True"),
    ("pmraerr_formula", "pm_ra_error", H, ""),
    ("pmdec_formula", "pm_dec", H, "Adopted PM → adopted=True"),
    ("pmdecerr_formula", "pm_dec_error", H, ""),
    ("ref_pm_formula", "reference", H, "Reference for adopted PM"),
    ("pmra_lit", "pm_ra", H, "Literature PM"),
    ("pmraerr_lit", "pm_ra_error", H, ""),
    ("pmdec_lit", "pm_dec", H, ""),
    ("pmdecerr_lit", "pm_dec_error", H, ""),
    ("ref_pm_lit", "reference", H, ""),
    ("pmra_UKIRT", "pm_ra", H, "UKIRT program PM (ref = ref_plx_UKIRT)"),
    ("pmraerr_UKIRT", "pm_ra_error", H, ""),
    ("pmdec_UKIRT", "pm_dec", H, ""),
    ("pmdecerr_UKIRT", "pm_dec_error", H, ""),
    ("pmra_Gaia", "pm_ra", H, "Gaia PM; reference from sourceID columns"),
    ("pmraerr_Gaia", "pm_ra_error", H, ""),
    ("pmdec_Gaia", "pm_dec", H, ""),
    ("pmdecerr_Gaia", "pm_dec_error", H, ""),
    ("pmra_P1", "pm_ra", H, "'Inf' sentinel = contaminated astrometry, drop"),
    ("pmraerr_P1", "pm_ra_error", H, ""),
    ("pmdec_P1", "pm_dec", H, "'Inf' sentinel = contaminated, drop"),
    ("pmdecerr_P1", "pm_dec_error", H, ""),
    ("ref_pm_P1", "reference", H, ""),
    ("pmra_catwise", "pm_ra", H, "CatWISE2020 PM; reference='CatWISE2020'"),
    ("pmraerr_catwise", "pm_ra_error", H, ""),
    ("pmdec_catwise", "pm_dec", H, ""),
    ("pmdecerr_catwise", "pm_dec_error", H, ""),
    ("pmra_simbad", "pm_ra", H, "SIMBAD PM"),
    ("pmraerr_simbad", "pm_ra_error", H, ""),
    ("pmdec_simbad", "pm_dec", H, ""),
    ("pmdecerr_simbad", "pm_dec_error", H, ""),
    ("ref_pm_simbad", "reference", H, ""),
    ("pmra_P1_PV34", "pm_ra", H, "PS1 PV3.4 (unreleased processing version)"),
    ("pmraerr_P1_PV34", "pm_ra_error", H, ""),
    ("pmdec_P1_PV34", "pm_dec", H, ""),
    ("pmdecerr_P1_PV34", "pm_dec_error", H, ""),
    ("ref_pm_P1_PV34", "reference", H, ""),
]
for c, f, conf, n in pm:
    add(c, "ProperMotions", f, conf, n)
add("pm_lit", None, None, U, "Total PM amplitude; derivable from pm_ra/pm_dec — suggest skip")
add("pmerr_lit", None, None, U, "Uncertainty of derived total PM — suggest skip")
add("angle_lit", None, None, U, "PM position angle; no AstroDB field (Morphology.position_angle is source morphology) — suggest skip")
add("angleerr_lit", None, None, U, "Uncertainty of PM position angle — suggest skip")

# --- RadialVelocities ---
rv = [
    ("rv_formula", "rv_kms", H, "Adopted RV → adopted=True"),
    ("rverr_formula", "rv_error", H, ""),
    ("ref_rv_formula", "reference", H, ""),
    ("rv_lit", "rv_kms", H, "Literature RV"),
    ("rverr_lit", "rv_error", H, ""),
    ("ref_rv_lit", "reference", H, ""),
    ("rv_Gaia", "rv_kms", H, "Gaia DR3 RV; reference='Gaia DR3'"),
    ("rverr_Gaia", "rv_error", H, ""),
]
for c, f, conf, n in rv:
    add(c, "RadialVelocities", f, conf, n)

# --- SourceTypes ---
st = [
    ("spt_opt", "source_type", H, "Optical spectral type; ':'/'::'' suffix = 1/2-subtype uncertainty → comments"),
    ("ref_spt_opt", "reference", H, ""),
    ("spt_ir", "source_type", H, "NIR spectral type → comments='NIR'"),
    ("ref_spt_ir", "reference", H, ""),
    ("grav_opt", "source_type", M, "Optical gravity class (beta/gamma/delta); store as classification with comments, or fold into SpT comments"),
    ("ref_grav_opt", "reference", M, ""),
    ("grav_ir", "source_type", M, "NIR gravity class (FLD-G/INT-G/VL-G)"),
    ("ref_grav_ir", "reference", M, ""),
]
for c, f, conf, n in st:
    add(c, "SourceTypes", f, conf, n)
for c in ("sptnum_opt_formula", "sptnum_ir_formula", "sptnum_formula",
          "sptnumabs_formula", "sptnum_photdist_formula"):
    add(c, None, None, U, "Derived numerical SpT encoding; recomputable from spt_opt/spt_ir — suggest skip")

# --- Associations (BANYAN) ---
add("banyan_sigma_max_hypo_young", "Associations", "association", M, "Highest-probability BANYAN Sigma YMG hypothesis")
add("banyan_sigma_max_prob_young", "Associations", "membership_probability", H, "Probability of the BANYAN hypothesis")
add("banyan_sigma_results", "Associations", "comments", L, "Full BANYAN Sigma results string")
add("banyan_sigma_input_params", "Associations", "comments", L, "Inputs used for BANYAN Sigma")

# --- ModeledParameters (distances) ---
add("dist_plx_formula", None, None, U, "=1000/plx_formula; derivable from ingested parallax — suggest skip")
add("disterr_plx_formula", None, None, U, "Uncertainty of derived parallactic distance — suggest skip")
dist = [
    ("dist_J_2MASS_formula", "value", "SpT–M(J_2MASS) polynomial (Dupuy & Liu 2012 / Sanghi+23)"),
    ("disterr_J_2MASS_formula", "error", ""),
    ("dist_J_MKO_formula", "value", "SpT–M(J_MKO) polynomial"),
    ("disterr_J_MKO_formula", "error", ""),
    ("dist_Ks_2MASS_formula", "value", "SpT–M(Ks_2MASS) polynomial"),
    ("disterr_Ks_2MASS_formula", "error", ""),
    ("dist_K_MKO_formula", "value", "SpT–M(K_MKO) polynomial"),
    ("disterr_K_MKO_formula", "error", ""),
    ("dist_W2_formula", "value", "SpT–M(W2) polynomial (Feeser & Best 2022b / DL12 / Sanghi+23)"),
    ("disterr_W2_formula", "error", ""),
    ("dist_formula", "value", "Adopted distance; parameter='distance', unit='pc'"),
    ("disterr_formula", "error", ""),
]
for c, f, n in dist:
    note = (n + "; " if n else "") + "parameter='photometric distance', unit='pc'" \
        if c != "dist_formula" and c != "disterr_formula" else \
        (n if n else "Uncertainty of adopted distance")
    add(c, "ModeledParameters", f, M, note)
add("dist_formula_source", "ModeledParameters", "comments", L, "Provenance of adopted distance")

# --- verify full coverage ---
missing = [c for c in order if c not in MAP]
assert not missing, missing

# --- counts ---
counts = {H: 0, M: 0, L: 0, U: 0}
for c in order:
    counts[MAP[c][2]] += 1
print("Confidence counts:", counts)

today = "2026-06-12"

# --- markdown output ---
md = f"""# AstroDB Schema Match: ultracool_main.csv

**Source:** `ultracool_main.csv` (UltracoolSheet Main tab) · {today}
**Columns:** {len(order)} — 🟢 High: {counts[H]} · 🟡 Medium: {counts[M]} · 🔴 Low: {counts[L]} · ⚪ Unmatched: {counts[U]}

| Column | Description | Units | Type | DB Table | DB Field | Confidence | Notes |
|---|---|---|---|---|---|---|---|
"""
for c in order:
    desc, units, dtype = cols[c]
    short = desc if len(desc) <= 110 else desc[:107] + "..."
    t, f, conf, n = MAP[c]
    badge = {"High": "🟢 High", "Medium": "🟡 Medium", "Low": "🔴 Low", "Unmatched": "⚪ Unmatched"}[conf]
    md += f"| `{c}` | {short} | {units} | {dtype} | {('→ ' + t) if t else '—'} | {('`' + f + '`') if f else '—'} | {badge} | {n} |\n"

with open("tmp/schema-match-result.md", "w", encoding="utf-8") as fh:
    fh.write(md)

# --- HTML output ---
ROWBG = {"High": "#f0fff0", "Medium": "#fffbea", "Low": "#fff3f0", "Unmatched": "#f5f5f5"}
BADGE = {"High": "🟢 High", "Medium": "🟡 Medium", "Low": "🔴 Low", "Unmatched": "⚪ Unmatched"}

rows_html = []
for c in order:
    desc, units, dtype = cols[c]
    short = desc if len(desc) <= 140 else desc[:137] + "..."
    t, f, conf, n = MAP[c]
    rows_html.append(
        f'<tr style="background:{ROWBG[conf]}">'
        f'<td><code class="input">{c}</code></td>'
        f'<td>{short}</td><td style="text-align:center">{units}</td>'
        f'<td class="db-table">{("→ " + t) if t else "—"}</td>'
        f'<td>{("<code class=field>" + f + "</code>") if f else "—"}</td>'
        f'<td style="text-align:center">{BADGE[conf]}</td>'
        f'<td class="notes">{n}</td></tr>')

filters = [
    ("PAN-STARRS/PS1.g", "em.opt", "4866", "1180"),
    ("PAN-STARRS/PS1.r", "em.opt", "6215", "1400"),
    ("PAN-STARRS/PS1.i", "em.opt", "7545", "1290"),
    ("PAN-STARRS/PS1.z", "em.opt", "8679", "1040"),
    ("PAN-STARRS/PS1.y", "em.opt", "9633", "630"),
    ("GAIA/GAIA3.Gbp", "em.opt", "5110", "2333"),
    ("GAIA/GAIA3.G", "em.opt", "6218", "4053"),
    ("GAIA/GAIA3.Grp", "em.opt.R", "7769", "2842"),
    ("2MASS/2MASS.J", "em.IR.J", "12350", "1624"),
    ("2MASS/2MASS.H", "em.IR.H", "16620", "2509"),
    ("2MASS/2MASS.Ks", "em.IR.K", "21590", "2619"),
    ("UKIRT/WFCAM.Y ⚠", "em.IR.NIR", "10310", "1020"),
    ("MKO/NSFCam.J", "em.IR.J", "12500", "1600"),
    ("MKO/NSFCam.H", "em.IR.H", "16350", "2900"),
    ("MKO/NSFCam.K", "em.IR.K", "22000", "3400"),
    ("MKO/NSFCam.Lp", "em.IR.3-4um", "37700", "7000"),
    ("MKO/NSFCam.Mp", "em.IR.4-8um", "46800", "2400"),
    ("WISE/WISE.W1", "em.IR.3-4um", "33526", "6626"),
    ("WISE/WISE.W2", "em.IR.4-8um", "46028", "10423"),
    ("WISE/WISE.W3", "em.IR.8-15um", "115608", "55069"),
    ("WISE/WISE.W4", "em.IR.15-30um", "220883", "41013"),
    ("Spitzer/IRAC.I1", "em.IR.3-4um", "35500", "7430"),
    ("Spitzer/IRAC.I2", "em.IR.4-8um", "44930", "10100"),
]
filt_rows = "".join(
    f"<tr><td><code class=field>{b}</code></td><td>{u}</td><td>{w}</td><td>{wd}</td></tr>"
    for b, u, w, wd in filters)

unk = '<em style="color:#aaa">unknown — fill in</em>'
params_rows = "".join(
    f"<tr><td><code class=field>{p}</code></td><td>{d}</td></tr>" for p, d in [
        ("age", "Age of the source in Gyr"),
        ("distance", "Adopted distance in pc"),
        ("photometric distance", "Distance from SpT–absolute magnitude polynomials, in pc"),
    ])

assoc_rows = "".join(
    f"<tr><td><code class=field>{a}</code></td><td>YMG / association</td><td>{unk}</td></tr>"
    for a in ["(unique values of age_category and banyan_sigma_max_hypo_young — "
              "e.g. BPMG, TWA, ABDMG, ARG, CAR, COL, THA, USCO, HYA, PLE …)"])

tel_rows = "".join(
    f"<tr><td><code class=field>{t}</code></td><td>{d}</td></tr>" for t, d in [
        ("Pan-STARRS1", "1.8 m survey telescope, Haleakala"),
        ("Gaia", "ESA astrometry mission"),
        ("2MASS", "Two Micron All Sky Survey"),
        ("WISE", "Wide-field Infrared Survey Explorer"),
        ("Spitzer", "Spitzer Space Telescope (IRAC)"),
        ("UKIRT", "UK Infrared Telescope (MKO photometry / UKIDSS)"),
    ])

regime_rows = "".join(
    f"<tr><td><code class=field>{r}</code></td><td>{d}</td></tr>" for r, d in [
        ("optical", "PS1 grizy, Gaia G/BP/RP"),
        ("nir", "2MASS JHKs, MKO YJHK"),
        ("mir", "WISE W1–W4, Spitzer ch1/ch2, MKO L'M'"),
    ])

unmatched_lis = "".join(
    f'<li><code class="input">{c}</code> — {MAP[c][3]}</li>'
    for c in order if MAP[c][2] == U)

conv_rows = "".join(f"<tr><td><code class=input>{c}</code></td>"
                    f'<td style="color:#c0392b">{iu}</td>'
                    f"<td><code class=field>{f}</code></td>"
                    f'<td style="color:#27ae60">{ru}</td><td>{fm}</td></tr>'
    for c, iu, f, ru, fm in [
        ("epoch_mjd_P1", "MJD (days)", "Positions.epoch_year", "decimal year", "2000.0 + (MJD − 51544.5) / 365.25"),
        ("epoch_2mass", "UT date string", "Positions.epoch_year", "decimal year", "parse date → year + day_of_year/365.25"),
    ])

ing_notes = [
    "Each photometry band column becomes one row per source in <b>Photometry</b> — 23 band columns → up to 23 rows per object.",
    "Multiple astrometry sources (formula/lit/UKIRT/Gaia/P1/CatWISE/SIMBAD/PV3.4) each become separate rows in Parallaxes/ProperMotions/RadialVelocities; set <code class=field>adopted=True</code> only for the <code class=input>*_formula</code> rows.",
    "Several RA/Dec column pairs map to <b>Positions</b>; only <code class=input>ra_j2000_formula</code>/<code class=input>dec_j2000_formula</code> go to <b>Sources</b> (epoch_year=2000.0, equinox='J2000').",
    "Sentinel values must be cleaned before ingest: 'null' strings, NaN-as-upper-limit in photometry errors, −999 in PS1 errors, 'Inf' in PS1 proper motions.",
    "All <code class=input>ref_*</code> codes must exist in <b>Publications</b> before any data-table insert (FK constraint). The References tab of the workbook maps ref codes → ADS bibcodes — ingest it into Publications first.",
    "Multi-reference cells separated with ';' or '|' need splitting; AstroDB reference fields hold a single Publications key.",
    "Gaia rows have no per-row ref column — derive reference ('GaiaDR2'/'GaiaDR3') from <code class=input>sourceID_Gaia_DR3</code>/<code class=input>sourceID_Gaia_DR2</code>.",
    "Insert order: Publications → Telescopes/Instruments/PhotometryFilters/lookup lists → Sources → Names/Positions/data tables.",
    "Spectral-type uncertainty suffixes (':' and '::') and gravity-class strings need parsing into SourceTypes.comments.",
    "<code class=input>age_category</code> mixes YMG names with system-age entries (object names) — only group-like values should create Associations rows.",
]
ing_lis = "".join(f"<li>{x}</li>" for x in ing_notes)

html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>AstroDB Schema Match — ultracool_main.csv</title>
<style>
body        {{ font-family: sans-serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; }}
table       {{ border-collapse: collapse; width: 100%; font-size: 0.9rem; }}
th, td      {{ padding: 8px 12px; border: 1px solid #ddd; vertical-align: top; }}
code.input  {{ background: #e8edf2; border-radius: 4px; padding: 2px 6px; font-family: monospace; }}
code.field  {{ background: #e8f4e8; border-radius: 4px; padding: 2px 6px; font-family: monospace; }}
.db-table   {{ font-weight: 600; }}
.notes      {{ font-size: 0.82rem; color: #555; }}
thead th    {{ background: #2c3e50; color: #fff; position: sticky; top: 0; }}
.lk th      {{ background: #f0a500; color: #fff; position: static; }}
.cv th      {{ background: #2980b9; color: #fff; position: static; }}
</style></head><body>
<h1>AstroDB Schema Match</h1>
<p>Source: <code class="input">ultracool_main.csv</code> (UltracoolSheet v2.1.0, Main tab — 3890 rows × 242 columns) · {today}</p>
<p><b>Legend:</b> <code class="input">blue-gray chip</code> = input column ·
<code class="field">green chip</code> = AstroDB field · row color = confidence
(<span style="background:#f0fff0">&nbsp;High&nbsp;</span> /
<span style="background:#fffbea">&nbsp;Medium&nbsp;</span> /
<span style="background:#fff3f0">&nbsp;Low&nbsp;</span> /
<span style="background:#f5f5f5">&nbsp;Unmatched&nbsp;</span>) ·
🟢 {counts[H]} · 🟡 {counts[M]} · 🔴 {counts[L]} · ⚪ {counts[U]}</p>
<table><thead><tr><th>Input Column</th><th>Description</th><th>Units</th>
<th>DB Table</th><th>DB Field</th><th>Confidence</th><th>Notes</th></tr></thead>
<tbody>{"".join(rows_html)}</tbody></table>

<h2>Lookup Table Checklist</h2>
<p>The following lookup tables need entries added before ingestion. Rows in data tables
reference these by foreign key — inserting a row that references a missing lookup value will fail.</p>

<h3>PhotometryFilters</h3>
<table class="lk"><thead><tr><th>band (SVO filter ID)</th><th>ucd</th>
<th>effective_wavelength_angstroms</th><th>width_angstroms</th></tr></thead>
<tbody>{filt_rows}</tbody></table>
<p class="notes">Wavelengths are approximate — verify against
<a href="https://svo2.cab.inta-csic.es/theory/fps3/">SVO FPS</a>.
⚠ <code class="input">Y_MKO</code>: the UltracoolSheet aggregates MKO-system Y from
UKIDSS/VHS/VIKING — confirm whether <code class="field">UKIRT/WFCAM.Y</code> (or
<code class="field">Paranal/VISTA.Y</code>) is the right SVO ID.
2MASS, WISE, and Gaia filters ship with the astrodb template and may only need verification.</p>

<h3>ParameterList</h3>
<table class="lk"><thead><tr><th>parameter</th><th>description</th></tr></thead>
<tbody>{params_rows}</tbody></table>

<h3>CompanionList</h3>
<table class="lk"><thead><tr><th>companion</th><th>description</th></tr></thead>
<tbody><tr><td>(unique values of <code class="input">has_higher_mass_companion</code> and
<code class="input">multiplesystem_resolved_in_this_table</code> — populated from data at ingest time)</td>
<td>{unk}</td></tr></tbody></table>

<h3>AssociationList</h3>
<table class="lk"><thead><tr><th>association</th><th>association_type</th><th>reference</th></tr></thead>
<tbody>{assoc_rows}</tbody></table>

<h3>SourceTypeList</h3>
<table class="lk"><thead><tr><th>source_type</th><th>comments</th></tr></thead>
<tbody><tr><td>(unique spectral types from <code class="input">spt_opt</code>/<code class="input">spt_ir</code>:
M6–M9.5, L0–L9.5, T0–T9.5, Y0–Y2, plus subdwarf 'sd' prefixes and gravity classes)</td>
<td>{unk}</td></tr></tbody></table>

<h3>Telescopes</h3>
<table class="lk"><thead><tr><th>telescope</th><th>description</th></tr></thead>
<tbody>{tel_rows}</tbody></table>

<h3>RegimeList</h3>
<table class="lk"><thead><tr><th>regime</th><th>description</th></tr></thead>
<tbody>{regime_rows}</tbody></table>

<h2>Unit Conversions</h2>
<p>These columns require conversion before ingestion — the DB field expects different units
than the source data provides.</p>
<table class="cv"><thead><tr><th>Column</th><th>Input Units</th><th>DB Field</th>
<th>Required Units</th><th>Conversion Formula</th></tr></thead>
<tbody>{conv_rows}</tbody></table>

<h2>Unmatched Columns</h2>
<ul>{unmatched_lis}</ul>

<h2>Ingestion Notes</h2>
<ul>{ing_lis}</ul>
</body></html>"""

with open("tmp/schema-match-result.html", "w", encoding="utf-8") as fh:
    fh.write(html)

# update sidecar
with open("tmp/astrodb-parse-result.json") as fh:
    sidecar = json.load(fh)
sidecar["match_md"] = "tmp/schema-match-result.md"
sidecar["match_html"] = "tmp/schema-match-result.html"
with open("tmp/astrodb-parse-result.json", "w") as fh:
    json.dump(sidecar, fh)

print("Wrote tmp/schema-match-result.md and tmp/schema-match-result.html")
