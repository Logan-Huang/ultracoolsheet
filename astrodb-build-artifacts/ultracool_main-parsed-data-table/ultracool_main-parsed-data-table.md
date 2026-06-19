# Column Information: ultracool_main.csv

**File:** `ultracool_main.csv`
**Format:** csv
**Reader:** astropy
**Rows:** 3890
**Columns:** 242

| Column | Description | Units | Type |
|--------|-------------|-------|------|
| `name` | Unique object name (normally taken from the object's first publication) | — | str |
| `name_simbadable` | SIMBAD-able name (which is true for most values in the name field, but not all) | — | str |
| `ref_discovery` | Reference of discovery of the object as an ultracool dwarf. References with the "-phot" suffix means the objects was selected in photometric catalog as an ultracool object/candidate but without confirmation by spectroscopy or medium-band photometry. | — | str |
| `ra_j2000_formula` | Final adopted Right Ascension (equinox=2000, epoch=2000); preference order is ra_j2000_DR3/DR2 (includes both objects detected in DR3 and companions' host stars when their separations are < 1 arcsec or there are no other coordinates available for the companion), ra_j2000_PS1 (only if object is detected in PS1), ra_j2000_CatWISE (only if the object is detected and has measured proper motion in CatWISE), ra_j2000_UKIDSS (only if the object is detected and has measured proper motion in UKIDSS), and finally ra_j2000_SIMBAD (with hyperlink to the coordinates reference). For ra_j2000_UKIDSS and ra_j2000_P1, the epoch 2000 coordinates given here were computed by us from the observing epoch and the proper motions reported in those catalogs. (These proper motions are not necessarily the same as the best possible proper motions, given in {pmra_formula, pmdec_formula}.) | deg | float64 |
| `dec_j2000_formula` | Final adopted Declination (equinox=2000, epoch=2000); follows the same preference order as ra_j2000_formula | deg | float64 |
| `source_j2000_formula` | Source of the RA and Dec given in ra_j2000_formula and dec_j2000_formula: DR3/DR2, CatWISE, UKIDSS, PS1, or SIMBAD (with hyperlink to the SIMBAD coordinates reference) | — | str |
| `glon_j2000` | Galactic longitude calculated from ra_j2000_formula and dec_j2000_formula | deg | float64 |
| `glat_j2000` | Galactic latitude calculated from ra_j2000_formula and dec_j2000_formula | deg | float64 |
| `literature_flag` | Flags with target info from the literature - see below for details | — | str |
| `ref_literature_flag` | References for flags with target info from the literature | — | str |
| `exoplanet` | Is this a companion that is planetary-mass (<~ 13 Mjup)? Y = general consensus is yes or very likely; Y? = possible but not confirmed; N? = possible but not likely; N = no evidence. Binary and triple systems have the same designations, joined by plus symbols (e.g., 2M 1207A+b has the designation "N+Y"). | — | str |
| `multiplesystem_unresolved_in_this_table` | Known multiple (binary, triple, or more) system with integrated-light (unresolved) properties listed in this tab [see Binaries and Triples+ tabs for more details]. If it is a multiple, this is set to "Y: ref_code(s)" where the reference(s) given refer to the discovery that the system is a multiple. If it is more than a binary, then it is set to "Y: ref_code(s) \| triple/quad: ref_code(s)" where the information after the "\|" indicates what type of higher order multiple it is and the discovery of that higher order multiplicity. A value of "N" indicates that the system is not known to be a small-separation multiple. Resolved (large-separation) multiples are indicated in the next columns. | — | str |
| `multiplesystem_resolved_in_this_table` | Component of a multiple system where at least one other ultracool dwarf component is listed as a separate object in this tab. If there is a resolved companion, this is set to "name: ref_code(s)", where name is the name of the wide companion as it appears in this sheet, and the reference(s) given refer to the discovery that this object and the other named object are a bound pair. | — | str |
| `has_higher_mass_companion` | Known to have a higher mass companion (i.e., a host star that does *not* have its own entry in the sheet). Sometimes more than one name is given for the higher mass companion; if so, they are separated with "/". A "?" indicates uncertain companionship. | — | str |
| `sep_companion` | Separation of the higher mass companion if one exists; set to zero for unresolved pairs. | arcsec | float64 |
| `youth_evidence` | If this is not set to "N", then the object has evidence for being young (<=300 Myr), with the string indicating the origin of the youth information: "dynmass" = young age derived from a dynamical mass measurement "lowg" = object has low-gravity spectral features "primary" = young age adopted from host star "SFR" = member of star-forming region (note: Sco-Cen is not labeled as SFR, but rather as YMG here) "Xray" = youth based on X-ray emission "YMG" = member of young moving group or stellar association | — | str |
| `age_category` | Category assigned to the object regarding its age estimate, based on the approach described in Sanghi et al. (2023, ApJ, in press). In brief: * BANYAN Sigma is used with the UCS astrometry to assess moving group membership. Objects with >=90% membership probability are assigned to the group, with the string used in BANYAN Sigma (BPMG = beta Pic moving group, etc.) and a "!" appended to the string if full 6-d kinematic information is available (parallax, proper motion & RV). Objects with membership probability of 80-90% are assigned to the group, with a "?" appended, which is also appended for objects whose >=90% memberships rely on photometric distances or whose spectroscopic gravities are in conflict with such membership (FLD-G objects in <100 Myr moving groups). * Objects with field membership assigned by BANYAN Sigma but with low-gravity spectra are assigned to the age category corresponding to their gravity classification. * If there is an age estimate for the object on the basis of it belonging to the stellar multiple (i.e. it's a companion to a higher mass star or in a binary system), then the name of the object is given here. For these cases, we also list SFR/YMG information if relevant, so that this information is tracked (e.g. age_category can be used to select all objects in specific SFR/YMG), which such information separated by a semi-colon. (For such semi-colon delimited entries, it's the first item in the list that is adopted as the age.) * If there is ancillary age information in the literature in the flag column, this is considered as well, which can lead to the outcome which is in accord with the BANYAN Sigma information or in discord (which can lead to a "?" designation or not, based on a judgment call - see age_category_justification text below for more details). * Finally, all the strings in this column (ignoring the ? and ! suffixes) correspond to entries in the AgeValues tab, which gives the associated ages, uncertainties & references. | — | str |
| `age_category_justification` | Justification for the assigned age_category value. * "UCS+BANYAN" means assignment based on our BANYAN Sigma calculations using the UltracoolSheet astrometry. (For objects that are placed in YMGs using old-objects photometric distances but whose memberships are not upheld using young-object photometric distances, these are assigned field membership and flagged with "UCS_24(dphot)" to highlight the inconsistency in the photometric distances.) * Citations are provided for objects with other memberships or spectroscopic gravities. * "system_age" is listed for objects with individual age determinations (which are tabulated & cited in the AgeValues tab). * "UCS_24" means we needed to make a judgment call to reconcile multiple pieces of info (or no info at all). * Note that for objects in star-forming regions (esp. USCO), we often defer to the literature membership even when not fully supported by the BANYAN Sigma results, since we did not do a complete examination of the literature associated with objects in these regions. A more careful look at membership for these objects is warranted, beyond our large-scale analysis here. | — | str |
| `age_singlevalue_gyr_formula` | Representative (median/average) age for object in Gyr, identical to age_gyr in the AgeValues tab. | Gyr | float64 |
| `age_distribution_gyr_formula` | Age range for object in Gyr, based on info in AgeValues tab. Cells with with +/- notation (e.g. "4(+1/-1)") are normal age distributions. Cells with just a hyphen are uniform distributions. | Gyr | str |
| `designation_P1_formula` | Pan-STARRS1 3π Survey DR2 designation, auto-generated from the PS1 DR2 coordinates. (Some objects with a designation were detected by Pan-STARRS1 but the photometry is of insufficient quality to appear in this table; see Best et al. 2018). | — | str |
| `ra_j2000_P1` | Computed RA (equinox=2000, epoch=2000) using Pan-STARRS1 epoch astrometry and proper motions | deg | float64 |
| `dec_j2000_P1` | Computed Dec (equinox=2000, epoch=2000) using Pan-STARRS1 epoch astrometry and proper motions | deg | float64 |
| `ra_epoch_P1` | RA from Pan-STARRS1 (equinox=2000, epoch=epoch_mjd_P1) | deg | float64 |
| `dec_epoch_P1` | Dec from Pan-STARRS1 (equinox=2000, epoch=epoch_mjd_P1) | deg | float64 |
| `epoch_mjd_P1` | Epoch of the Pan-STARRS1 astrometry in MJD | days | float64 |
| `ref_radec_P1` | Reference of Pan-STARRS1 astrometry | — | str |
| `g_P1` | g-band photometry from Pan-STARRS1 | mag | float64 |
| `gerr_P1` | Uncertainty in g-band photometry from Pan-STARRS1. A value of -999 denotes robust PS1 detection for a companion but contaminated/unreliable photometry due to the brighter host star. | mag | float64 |
| `g_nphot_P1` | Number of epochs used to calculate g-band photometry from Pan-STARRS1 | — | float64 |
| `g_src_P1` | Source of g-band photometry from Pan-STARRS1: chip (C; default), recalculated chip (R), or forced warp (W). This field matches the Vizier catalog (J/ApJS/234/1/dwarfs) field "n_PS1gmag" for the Best et al. (2018) table. (X) indicates photometry was replaced with NaN by hand due to obvious contamination from a nearby object. | — | str |
| `ref_g_P1` | Reference for Pan-STARRS1 g-band photometry | — | str |
| `r_P1` | r-band photometry from Pan-STARRS1 | mag | float64 |
| `rerr_P1` | Uncertainty in r-band photometry from Pan-STARRS1. A value of -999 denotes robust PS1 detection for a companion but contaminated/unreliable photometry due to the brighter host star. | mag | float64 |
| `r_nphot_P1` | Number of epochs used to calculate r-band photometry from Pan-STARRS1 | — | float64 |
| `r_src_P1` | Source of r-band photometry from Pan-STARRS1: chip (C; default), recalculated chip (R), or forced warp (W). This field matches the Vizier catalog (J/ApJS/234/1/dwarfs) field "n_PS1gmag" for the Best et al. (2018) table. (X) indicates photometry was replaced with NaN by hand due to obvious contamination from a nearby object. | — | str |
| `ref_r_P1` | Reference for Pan-STARRS1 r-band photometry | — | str |
| `i_P1` | i-band photometry from Pan-STARRS1 | mag | float64 |
| `ierr_P1` | Uncertainty in i-band photometry from Pan-STARRS1. A value of -999 denotes robust PS1 detection for a companion but contaminated/unreliable photometry due to the brighter host star. | mag | float64 |
| `i_nphot_P1` | Number of epochs used to calculate i-band photometry from Pan-STARRS1 | — | float64 |
| `i_src_P1` | Source of i-band photometry from Pan-STARRS1: chip (C; default), recalculated chip (R), or forced warp (W). This field matches the Vizier catalog (J/ApJS/234/1/dwarfs) field "n_PS1gmag" for the Best et al. (2018) table. (X) indicates photometry was replaced with NaN by hand due to obvious contamination from a nearby object. | — | str |
| `ref_i_P1` | Reference for Pan-STARRS1 i-band photometry | — | str |
| `z_P1` | z-band photometry from Pan-STARRS1 | mag | float64 |
| `zerr_P1` | Uncertainty in z-band photometry from Pan-STARRS1. A value of -999 denotes robust PS1 detection for a companion but contaminated/unreliable photometry due to the brighter host star. | mag | float64 |
| `z_nphot_P1` | Number of epochs used to calculate z-band photometry from Pan-STARRS1 | — | float64 |
| `z_src_P1` | Source of z-band photometry from Pan-STARRS1: chip (C; default), recalculated chip (R), or forced warp (W). This field matches the Vizier catalog (J/ApJS/234/1/dwarfs) field "n_PS1gmag" for the Best et al. (2018) table. (X) indicates photometry was replaced with NaN by hand due to obvious contamination from a nearby object. | — | str |
| `ref_z_P1` | Reference for Pan-STARRS1 z-band photometry | — | str |
| `y_P1` | y-band photometry from Pan-STARRS1 | mag | float64 |
| `yerr_P1` | Uncertainty in y-band photometry from Pan-STARRS1. A value of -999 denotes robust PS1 detection for a companion but contaminated/unreliable photometry due to the brighter host star. | mag | float64 |
| `y_nphot_P1` | Number of epochs used to calculate y-band photometry from Pan-STARRS1 | — | float64 |
| `y_src_P1` | Source of y-band photometry from Pan-STARRS1: chip (C; default), recalculated chip (R), or forced warp (W). This field matches the Vizier catalog (J/ApJS/234/1/dwarfs) field "n_PS1gmag" for the Best et al. (2018) table. (X) indicates photometry was replaced with NaN by hand due to obvious contamination from a nearby object. | — | str |
| `ref_y_P1` | Reference for Pan-STARRS1 y-band photometry | — | str |
| `BP_Gaia` | BP-band photometry from Gaia for the Object itself (if available) | mag | float64 |
| `BPerr_Gaia` | Uncertainty in BP_Gaia | mag | float64 |
| `G_Gaia` | G-band photometry from Gaia for the Object itself (if available) | mag | float64 |
| `Gerr_Gaia` | Uncertainty in G_Gaia | mag | float64 |
| `RP_Gaia` | RP-band photometry from Gaia for the Object itself (if available) | mag | float64 |
| `RPerr_Gaia` | Uncertainty in RP_Gaia | mag | float64 |
| `ref_photom_Gaia` | source of the Gaia photometry: DR2 or EDR3 | — | str |
| `designation_2mass` | 2MASS designation | — | str |
| `ra_epoch_2mass` | RA from 2MASS (equinox=2000, epoch=epoch_2mass) | deg | float64 |
| `dec_epoch_2mass` | Dec from 2MASS (equinox=2000, epoch=epoch_2mass) | deg | float64 |
| `epoch_2mass` | Epoch of 2MASS astrometry | UT | str |
| `J_2MASS` | J-band photometry from 2MASS | mag | float64 |
| `Jerr_2MASS` | Uncertainty in J-band photometry from 2MASS. NaN indicates that J_2MASS is an upper limit. | mag | float64 |
| `ref_J_2MASS` | Reference for 2MASS J-band photometry | — | str |
| `H_2MASS` | H-band photometry from 2MASS | mag | float64 |
| `Herr_2MASS` | Uncertainty in H-band photometry from 2MASS. NaN indicates that H_2MASS is an upper limit. | mag | float64 |
| `ref_H_2MASS` | Reference for 2MASS H-band photometry | — | str |
| `Ks_2MASS` | Ks-band photometry from 2MASS. Contains a handful of Ks magnitudes from instruments other than the 2MASS cameras. | mag | float64 |
| `Kserr_2MASS` | Uncertainty in Ks-band photometry from 2MASS. NaN indicates that Ks_2MASS is an upper limit. Contains a handful of Ks magnitude uncertainties from instruments other than the 2MASS cameras. | mag | float64 |
| `ref_Ks_2MASS` | Reference for 2MASS Ks-band photometry | — | str |
| `Cflg_2MASS` | Contamination and confusion flag (cc_flg) for 2MASS photometry | — | str |
| `designation_MKO` | designation from catalog of MKO photometry (e.g., ULAS, VHS, VIKING) | — | str |
| `Y_MKO` | Y-band photometry in MKO system | mag | float64 |
| `Yerr_MKO` | Uncertainty in Y-band photometry in MKO system. NaN indicates that Y_MKO is an upper limit. | mag | float64 |
| `ref_Y_MKO` | Reference for Y-band photometry in MKO system | — | str |
| `J_MKO` | J-band photometry in MKO system | mag | float64 |
| `Jerr_MKO` | Uncertainty in J-band photometry in MKO system. NaN indicates that J_MKO is an upper limit. | mag | float64 |
| `ref_J_MKO` | Reference for J-band photometry in MKO system | — | str |
| `H_MKO` | H-band photometry in MKO system | mag | float64 |
| `Herr_MKO` | Uncertainty in H-band photometry in MKO system. NaN indicates that H_MKO is an upper limit. | mag | float64 |
| `ref_H_MKO` | Reference for H-band photometry in MKO system | — | str |
| `K_MKO` | K-band photometry in MKO system | mag | float64 |
| `Kerr_MKO` | Uncertainty in K-band photometry in MKO system. NaN indicates that K_MKO is an upper limit. | mag | float64 |
| `ref_K_MKO` | Reference for K-band photometry in MKO system | — | str |
| `Lp_MKO` | L'-band photometry in MKO system | mag | float64 |
| `Lperr_MKO` | Uncertainty in L'-band photometry in MKO system. NaN indicates that Lp_MKO is an upper limit. | mag | float64 |
| `ref_Lp_MKO` | Reference for L'-band photometry in MKO system | — | str |
| `Mp_MKO` | M'-band photometry in MKO system | mag | float64 |
| `Mperr_MKO` | Uncertainty in M'-band photometry in MKO system. NaN indicates that Mp_MKO is an upper limit. | mag | float64 |
| `ref_Mp_MKO` | Reference for M'-band photometry in MKO system | — | str |
| `designation_WISE` | CatWISE2020 designation if available, else AllWISE designation | — | str |
| `ra_j2000_WISE` | RA from CatWISE (equinox=2000, epoch=2000) if available, calculated from ra_epoch_WISE and pmra_catwise, else AllWISE J2000 RA. | deg | float64 |
| `dec_j2000_WISE` | Dec from CatWISE (equinox=2000, epoch=2000) if available, calculated from dec_epoch_WISE and pmdec_catwise, else AllWISE J2000 Dec. | deg | float64 |
| `ra_epoch_WISE` | RA from CatWISE (equinox=2000, epoch=2015.405 = MJD 57170.00) if available, else AllWISE (equinox=2000, epoch=2010.5589 = MJD 55400.0). Same as the CatWISE or AllWISE "ra_pm" fields. | deg | float64 |
| `dec_epoch_WISE` | Dec from CatWISE (equinox=2000, epoch=2015.405 = MJD 57170.00) if available, else AllWISE (equinox=2000, epoch=2010.5589 = MJD 55400.0). Same as the CatWISE or AllWISE "dec_pm" fields. | deg | float64 |
| `ref_astrom_WISE` | Reference for WISE designations and coordinates | — | str |
| `W1` | W1-band photometry from CatWISE (w1mpro) if available, else AllWISE | mag | float64 |
| `W1err` | Uncertainty in W1-band photometry. NaN indicates that W1 is an upper limit. | mag | float64 |
| `chi2_W1` | Reduced chi^2 for W1 profile-fit photometry | — | float64 |
| `ref_W1` | Reference for W1 photometry | — | str |
| `W2` | W2-band photometry from CatWISE (w2mpro) if available, else AllWISE | mag | float64 |
| `W2err` | Uncertainty in W2-band photometry. NaN indicates that W2 is an upper limit. | mag | float64 |
| `chi2_W2` | Reduced chi^2 for W2 profile-fit photometry | — | float64 |
| `ref_W2` | Reference for W2 photometry | — | str |
| `W3` | W3-band photometry from AllWISE | mag | float64 |
| `W3err` | Uncertainty in W3-band photometry. NaN indicates that W3 is an upper limit. | mag | float64 |
| `chi2_W3` | Reduced chi^2 for W3 profile-fit photometry | — | float64 |
| `ref_W3` | Reference for W3 photometry | — | str |
| `W4` | W4-band photometry from AllWISE | mag | float64 |
| `W4err` | Uncertainty in W4-band photometry. NaN indicates that W4 is an upper limit. | mag | float64 |
| `chi2_W4` | Reduced chi^2 for W4 profile-fit photometry | — | float64 |
| `ref_W4` | Reference for W4 photometry | — | str |
| `flag_WISE` | Combined contamination flags from CatWISE (ab_flags) and AllWISE (cc_flags) for photometry. The combined flags have two characters if detected only in CatWISE, or four characters if detected in AllWISE, corresponding to the W1/W2/W3/W4 bands. Each flag is drawn from the same source as the photometry, i.e., the first two characters (for W1 and W2, respectively) are from CatWISE if available, else AllWISE. The third and fourth characters (for W3 and W4, respectively) are only from AllWISE. | — | str |
| `nb_AllWISE` | Number of PSF components used simultaneously in the profile-fitting (nb) for AllWISE photometry | — | float64 |
| `neigh_AllWISE` | Number of other AllWISE objects detected within 8" of the object's AllWISE position. | — | float64 |
| `ch1` | Spitzer [3.6]-band photometry | mag | float64 |
| `ch1err` | Uncertainty in Spitzer [3.6]-band photometry | mag | float64 |
| `ch2` | Spitzer [4.5]-band photometry | mag | float64 |
| `ch2err` | Uncertainty in Spitzer [4.5]-band photometry | mag | float64 |
| `ref_Spitzer` | Reference for Spitzer photometry | — | str |
| `plx_formula` | Final adopted parallax; preference order is plx_DR3/DR2, then the most precise of [plx_lit, plx_UKIRT, plx_P1], excluding plx_P1 measurements with plx_P1/eplx_P1 < 5 | mas | float64 |
| `plxerr_formula` | Uncertainty in plx_formula | mas | float64 |
| `ref_plx_formula` | Reference for adopted parallax | — | str |
| `pmra_formula` | Final adopted RA proper motion; same preference order as plx_formula but using the most precise total proper motion error (quadrature sum of proper motion errors in RA and Dec), and thus not necessarily from the same source as plx_formula if a more precise proper motion is known | mas/yr | float64 |
| `pmraerr_formula` | Uncertainty in pmra_formula | mas/yr | float64 |
| `pmdec_formula` | FInal adopted Dec proper motion; same preference order as plx_formula but using the most precise total proper motion error (quadrature sum of proper motion errors in RA and Dec), and thus not necessarily from the same source as plx_formula if a more precise proper motion is known | mas/yr | float64 |
| `pmdecerr_formula` | Uncertainty in pmdec_formula | mas/yr | float64 |
| `ref_pm_formula` | Reference for adopted proper motion | — | str |
| `rv_formula` | Final adopted RV, chosen between rv_lit and rv_gaia using whichever value is more precise (lower rverr). Some literature RVs are excluded from consideration here. To be included, either the RV error needs to be < 40 km/s or abs(RV) < 500 km/s. This is to filter out some extremely low S/N measurements, including spurious SDSS RVs. | km/s | float64 |
| `rverr_formula` | Uncertainty in rv_formula | km/s | float64 |
| `ref_rv_formula` | Reference for adopted RV | — | str |
| `plx_lit` | Selected parallax from the literature (other than Gaia, Best20, and PS1), usually the most precise one available | mas | float64 |
| `plxerr_lit` | Uncertainty in plx_lit | mas | float64 |
| `ref_plx_lit` | Reference for plx_lit | — | str |
| `pmra_lit` | Selected RA proper motion from the literature (other than Gaia, Best20, PS1, and CatWISE), usually the most precise one available. If nothing else is available, RA proper motion from Best18/PS1 is here (duplicating the pmra_P1 value). | mas/yr | float64 |
| `pmraerr_lit` | Uncertainty in pmra_lit | mas/yr | float64 |
| `pmdec_lit` | Selected Decl proper motion from the literature corresponding to pmra_lit | mas/yr | float64 |
| `pmdecerr_lit` | Uncertainty in pmdec_lit | mas/yr | float64 |
| `pm_lit` | Total proper motion amplitude corresponding to (pmra_lit, pmdec_lit) | mas/yr | float64 |
| `pmerr_lit` | Uncertainty in pm_lit | mas/yr | float64 |
| `angle_lit` | Proper motion position angle corresponding to (pmra_lit, pmdec_lit) | deg | float64 |
| `angleerr_lit` | Uncertainty in angle_lit | deg | float64 |
| `ref_pm_lit` | Reference for literature proper motion | — | str |
| `rv_lit` | Selected RV from the literature - often simply the same as the RV listed in the *_simbad columns, but not always. | km/s | float64 |
| `rverr_lit` | Uncertainty in rv_lit | km/s | float64 |
| `ref_rv_lit` | Reference for literature RV. If the reference is Gaia, then it comes from another Gaia measurement in the same physically bound system that does not appear in the *_gaia columns. This is typically the primary star of a companion, where we list the companion's own Gaia information in the *_gaia columns. | — | str |
| `plx_UKIRT` | Parallax from Best et al.'s UKIRT program | mas | float64 |
| `plxerr_UKIRT` | Uncertainty in plx_UKIRT | mas | float64 |
| `pmra_UKIRT` | RA proper motion from Best et al.'s UKIRT program | mas/yr | float64 |
| `pmraerr_UKIRT` | Uncertainty in pmra_UKIRT | mas/yr | float64 |
| `pmdec_UKIRT` | Dec proper motion from Best et al.'s UKIRT program | mas/yr | float64 |
| `pmdecerr_UKIRT` | Uncertainty in pmdec_UKIRT | mas/yr | float64 |
| `ref_plx_UKIRT` | Reference for parallax and proper motion from Best et al.'s UKIRT program (so far from one paper, Best et al. 2020) | — | str |
| `astrom_Gaia` | (O) Gaia astrometry is for the Object itself; (P) the object is a companion and the Gaia astrometry is for the Primary star | — | str |
| `ra_j2000_Gaia` | RA from Gaia (equinox=2000, epoch=2000) | deg | float64 |
| `dec_J2000_Gaia` | Dec from Gaia (equinox=2000, epoch=2000) | deg | float64 |
| `ra_epoch_Gaia` | RA from Gaia (equinox=2000, epoch=X), where X=2015.5 for DR2 (if sourceID_Gaia_DR3 = null) and X=2016.0 for DR3 otherwise | deg | float64 |
| `dec_epoch_Gaia` | Dec from Gaia (equinox=2000, epoch=X), where X=2015.5 for DR2 (if sourceID_Gaia_DR3 = null) and X=2016.0 for DR3 otherwise | deg | float64 |
| `plx_Gaia` | Parallax from Gaia | mas | float64 |
| `plxerr_Gaia` | Uncertainty in plx_Gaia | mas | float64 |
| `pmra_Gaia` | RA proper motion from Gaia | mas/yr | float64 |
| `pmraerr_Gaia` | Uncertainty in pmra_Gaia | mas/yr | float64 |
| `pmdec_Gaia` | Dec proper motion from Gaia | mas/yr | float64 |
| `pmdecerr_Gaia` | Uncertainty in pmdec_Gaia | mas/yr | float64 |
| `RUWE_Gaia` | Renormalized Unit Weight Error for Gaia | — | float64 |
| `nep_Gaia` | visibility_periods_used (i.e., number of epochs) in Gaia solution | — | float64 |
| `rv_Gaia` | Radial velocity reported in Gaia DR3 | km/s | float64 |
| `rverr_Gaia` | Uncertainty in the radial velocity reported in Gaia DR3 | km/s | float64 |
| `flags_Gaia` | Summary of some of the flags provided in the main DR3 catalog, using 1 or 2 characters for each flag. The presence of the following characters has the following meanings: Q = in_qso_candidates; G = in_galaxy_candidates; Mx = non_single_star flag, where x = 1 to 7; P = has_epoch_photometry; R = has_epoch_rv. (All of these are available in Vizier I/355/gaiadr3 catalog.) | — | str |
| `sourceID_Gaia_DR3` | unique source ID in Gaia DR3 (if null, then the reported astrometry is from Gaia DR2) | — | float64 |
| `sourceID_Gaia_DR2` | unique source ID in Gaia DR2 (if astrometry was available for the sourceID_Gaia_DR3 object in DR2) | — | float64 |
| `pmra_P1` | RA proper motion from Pan-STARRS1. Most values are re-calculations based on individual PS1 epochs, 2MASS, and Gaia DR1 (Best18). "Inf" indicates that the values were removed by hand due to astrometry clearly contaminated by a nearby object. | mas/yr | float64 |
| `pmraerr_P1` | Uncertainty in pmra_P1 | mas/yr | float64 |
| `pmdec_P1` | Dec proper motion from Pan-STARRS1. Most values are re-calculations based on individual PS1 epochs, 2MASS, and Gaia DR1 (Best18). "Inf" indicates that the values were removed by hand due to astrometry clearly contaminated by a nearby object. | mas/yr | float64 |
| `pmdecerr_P1` | Uncertainty in pmdec_P1 | mas/yr | float64 |
| `ref_pm_P1` | Reference for Pan-STARRS1 proper motion | — | str |
| `pmra_catwise` | RA proper motion from CatWISE | mas/yr | float64 |
| `pmraerr_catwise` | Uncertainty in pmra_catwise | mas/yr | float64 |
| `pmdec_catwise` | Dec proper motion from CatWISE | mas/yr | float64 |
| `pmdecerr_catwise` | Uncertainty in pmdec_catwise | mas/yr | float64 |
| `grav_opt` | Optical gravity classification: beta, gamma, delta for increasingly low gravity | — | str |
| `ref_grav_opt` | Reference for grav_opt | — | str |
| `grav_ir` | NIR gravity classification: FLD-G, INT-G, VL-G; or beta, gamma, delta | — | str |
| `ref_grav_ir` | Reference for grav_ir | — | str |
| `spt_opt` | Optical spectral type classification (uncertainties are assumed to be 0.5 subtypes, an appended ":" implies an uncertainty of 1 subtype, and an appended "::" implies an uncertainty of 2 subtype) | — | str |
| `ref_spt_opt` | Reference for spt_opt | — | str |
| `spt_ir` | NIR spectral type classification (uncertainties are assumed to be 0.5 subtypes, an appended ":" implies an uncertainty of 1 subtype, and an appended "::" implies an uncertainty of 2 subtype) | — | str |
| `ref_spt_ir` | Reference for spt_ir | — | str |
| `sptnum_opt_formula` | Numerical optical spectral type (M6=6, L0=10, T0=20; negative numbers indicate subdwarfs) | — | float64 |
| `sptnum_ir_formula` | Numerical NIR spectral type (M6=6, L0=10, T0=20; negative numbers indicate subdwarfs) | — | float64 |
| `sptnum_formula` | Adopted numerical spectral type (when both optical and NIR types are available, chooses optical types for M and L dwarfs and NIR types for T dwarfs) | — | float64 |
| `sptnumabs_formula` | Absolute value of adopted numerical spectral type (i.e., removes the negative sign distinguishing subdwarf spectral types) | — | float64 |
| `dist_plx_formula` | Adopted parallactic distance (=1000/plx_formula) | pc | float64 |
| `disterr_plx_formula` | Uncertainty in dist_plx_formula | pc | float64 |
| `sptnum_photdist_formula` | Numerical spectral type used in the calculation of photometric distances (needed to correctly handle binaries and triples) | — | float64 |
| `dist_J_2MASS_formula` | Distance computed using Dupuy & Liu (2012, for field objects) or Sanghi et al. (2023, for young objects) SpT vs. absolute J_2MASS magnitude polynomial with sptnum_photdist_formula. For binaries, the primary's resolved spectral type (sptnum_pri) and apparent magnitude (J_2MASS_pri_formula), if both are available, are used to calculate this distance. If both are not available, binaries have NaN reported here. | pc | float64 |
| `disterr_J_2MASS_formula` | Uncertainty in dist_J_2MASS_formula, using the piecewise RMS from Dupuy & Liu (2012) or the RMS from Sanghi et al. (2023). | pc | float64 |
| `dist_J_MKO_formula` | Distance computed using Dupuy & Liu (2012, for field objects) or Sanghi et al. (2023, for young objects) SpT vs. absolute J_MKO magnitude polynomial with sptnum_photdist_formula. For binaries, the primary's resolved spectral type (sptnum_pri) and apparent magnitude (J_MKO_pri_formula), if both are available, are used to calculate this distance. If both are not available, binaries have NaN reported here. | pc | float64 |
| `disterr_J_MKO_formula` | Uncertainty in dist_J_MKO_formula, using the piecewise RMS from Dupuy & Liu (2012) or the RMS from Sanghi et al. (2023). | pc | float64 |
| `dist_Ks_2MASS_formula` | Distance computed using Dupuy & Liu (2012, for field objects) or Sanghi et al. (2023, for young objects) SpT vs. absolute Ks_2MASS magnitude polynomial with sptnum_photdist_formula. For binaries, the primary's resolved spectral type (sptnum_pri) and apparent magnitude (Ks_2MASS_pri_formula), if both are available, are used to calculate this distance. If both are not available, binaries have NaN reported here. | pc | float64 |
| `disterr_Ks_2MASS_formula` | Uncertainty in dist_Ks_2MASS_formula, using the piecewise RMS from Dupuy & Liu (2012) or the RMS from Sanghi et al. (2023). | pc | float64 |
| `dist_K_MKO_formula` | Distance computed using Dupuy & Liu (2012, for field objects) or Sanghi et al. (2023, for young objects) SpT vs. absolute K_MKO magnitude polynomial with sptnum_photdist_formula. For binaries, the primary's resolved spectral type (sptnum_pri) and apparent magnitude (K_MKO_pri_formula), if both are available, are used to calculate this distance. If both are not available, binaries have NaN reported here. | pc | float64 |
| `disterr_K_MKO_formula` | Uncertainty in dist_K_MKO_formula, using the piecewise RMS from Dupuy & Liu (2012) or the RMS from Sanghi et al. (2023). | pc | float64 |
| `dist_W2_formula` | Distance computed using SpT vs. absolute W2 magnitude polynomial with sptnum_photdist_formula. (For binaries, this is always NaN.) The polynomials are from Feeser & Best (2022b, for field objects with CatWISE photometry); Dupuy & Liu (2012, for field objects with AllWISE photometry); or Sanghi et al. (2023, for young objects). | pc | float64 |
| `disterr_W2_formula` | Uncertainty in dist_J_W2_formula, using the piecewise RMS from Feeser & Best (2022b) or Dupuy & Liu (2012), or the RMS from Sanghi et al. (2023). | pc | float64 |
| `dist_formula` | Adopted distance. Preference order = plx, W2, K (if sptnumabs_formula<24.5), J (if sptnumabs_formula>=24.5); if both 2MASS and MKO photometry are available in K or J band, use 2MASS. Photometric distances of binaries use the resolved photometry for the primary component. | pc | float64 |
| `disterr_formula` | Uncertainty in dist_formula | pc | float64 |
| `dist_formula_source` | Source of the values in the dist_formula and disterr_formula columns; color is the same as those columns. If the distance was computed using a SpT vs. photometry polynomial for young objects, then "_young" is appended. If there is no distance given in dist_formula, then "null_no_phot" indicates no photometry available in any of the bands used in in the dist_*_formula columns; "null_no_spt" indicates no spectral type available to compute a photometric distance, and "null_binary_no_spt" indicates no resolved spectral type available for the primary of a binary system. | — | str |
| `note` | Miscellaneous notes for an object. Sometimes replicates information from other columns (e.g., data for binaries). | — | str |
| `Best21_vollim_sample` | Indicates objects that are members of the 25 pc volume-limited sample of L0-T8 dwarfs from Best et al. (2021). Single and binary members of the sample can be identified using the multiplesystem_unresolved_in_this_table column. | — | str |
| `Best24_vollim_sample` | Indicates objects that are members of the 25 pc volume-limited sample of L0-Y2 dwarfs from Best et al. (2024). Single and binary members of the sample can be identified using the multiplesystem_unresolved_in_this_table column. | — | str |
| `name_simbad` | Main designation used by SIMBAD for this object. | — | str |
| `ra_j2000_simbad` | RA from SIMBAD (equinox=2000, epoch=2000) | deg | float64 |
| `dec_j2000_simbad` | Dec from SIMBAD (equinox=2000, epoch=2000) | deg | float64 |
| `ref_radec_j2000_simbad` | Reference for SIMBAD J2000 coordinates | — | str |
| `pmra_simbad` | RA proper motion from SIMBAD | mas/yr | float64 |
| `pmraerr_simbad` | Uncertainty in pmra_simbad | mas/yr | float64 |
| `pmdec_simbad` | Dec proper motion from SIMBAD | mas/yr | float64 |
| `pmdecerr_simbad` | Uncertainty in pmdec_simbad | mas/yr | float64 |
| `ref_pm_simbad` | Reference for SIMBAD proper motion | — | str |
| `plx_simbad` | parallax from SIMBAD | mas | float64 |
| `plxerr_simbad` | Uncertainty in plx_simbad | mas | float64 |
| `ref_plx_simbad` | Reference for SIMBAD parallax | — | str |
| `identifiers_simbad` | All identifiers from SIMBAD (separated by "\|") | — | str |
| `firstref_simbad` | The first reference record from SIMBAD | — | str |
| `pmra_P1_PV34` | RA proper motion from Pan-STARRS1 processing version PV3.4 (final 3pi Survey version, unreleased) | mas/yr | float64 |
| `pmraerr_P1_PV34` | Uncertainty in pmra_P1_PV34 | mas/yr | float64 |
| `pmdec_P1_PV34` | Dec proper motion from Pan-STARRS1 processing version PV3.4 (final 3pi Survey version, unreleased) | mas/yr | float64 |
| `pmdecerr_P1_PV34` | Uncertainty in pmdec_P1_PV34 | mas/yr | float64 |
| `ref_pm_P1_PV34` | Reference of P1_PV34 proper motion | — | str |
| `banyan_sigma_results` | BANYAN Sigma query results (only hypothesis with >0.1% probabilities are listed) (2023 Oct 10 version) | — | str |
| `banyan_sigma_max_hypo_young` | The BANYAN Sigma hypothesis with the maximum probability (YMG only) (2023 Oct 10 version) | — | str |
| `banyan_sigma_max_prob_young` | Probability of banyan_sigma_max_hypo_young (2023 Oct 10 version) | — | float64 |
| `banyan_sigma_input_params` | Input parameters of the BANYAN Sigma results, with "pm" for proper motion, "trig-plx" for trigonometric parallax, "phot-plx" for photometry-based parallax (converted from photometric distance), and "rv" for radial velocity (2023 Oct 10 version) | — | str |
| `name_simpleDB` | source name used by https://simple-bd-archive.org/ | — | str |
| `url_simpleDB` | URL pointing to the object's page in https://simple-bd-archive.org/ | — | str |
| `ra_20250703_formula` | Present-epoch (2025-07-03) Right Ascension, equinox 2000; computed from ra_j2000_formula and pmra_formula (assumes zero proper motion if pmra_formula is NaN) | deg | float64 |
| `dec_20250703_formula` | Present-epoch (2025-07-03) Declination, equinox 2000; computed from dec_j2000_formula and pmdec_formula (assumes zero proper motion if pmdec_formula is NaN) | deg | float64 |
| `source_radec_20250703_formula` | Source of the astrometry used to compute the present-epoch (2025-07-03) coordinates | — | str |
| `gucds_shortname` | Unique shortname used in the Gaia UCD Survey collaboration (https://gucds.inaf.it) list for the object. The cross-matching with that catalog was done with input from Ricky Smart. | — | str |

## Notes

- Descriptions and units were extracted from the README tab of the UltracoolSheet workbook (v2.1.0), which documents every Main-tab column.
- Source spreadsheet: The UltracoolSheet (Best et al.), Main tab — complete-data objects only.
- 3 columns have no description; 105 columns have no units (most are dimensionless flags, names, or reference strings).
- Cells with no data contain the string 'null' or NaN per UltracoolSheet conventions.
