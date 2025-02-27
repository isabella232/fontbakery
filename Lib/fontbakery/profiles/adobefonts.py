"""
Checks for Adobe Fonts (formerly known as Typekit).
"""
import unicodedata

from fontbakery.callable import check
from fontbakery.constants import (
    ALL_HANGUL_SYLLABLES_CODEPOINTS,
    MODERN_HANGUL_SYLLABLES_CODEPOINTS,
)
from fontbakery.fonts_profile import profile_factory
from fontbakery.message import Message, KEEP_ORIGINAL_MESSAGE
from fontbakery.profiles.fontwerk import FONTWERK_PROFILE_CHECKS
from fontbakery.profiles.googlefonts import GOOGLEFONTS_PROFILE_CHECKS
from fontbakery.profiles.notofonts import NOTOFONTS_PROFILE_CHECKS
from fontbakery.profiles.universal import UNIVERSAL_PROFILE_CHECKS
from fontbakery.section import Section
from fontbakery.status import PASS, FAIL, WARN, ERROR, SKIP
from fontbakery.utils import add_check_overrides

profile_imports = (
    (".", ("shared_conditions", "universal", "fontwerk", "googlefonts", "notofonts")),
)
profile = profile_factory(default_section=Section("Adobe Fonts"))

SET_EXPLICIT_CHECKS = {
    # This is the set of explict checks that will be invoked
    # when fontbakery is run with the 'check-adobefonts' subcommand.
    # The contents of this set were last updated on April 26, 2022.
    #
    # =======================================
    # From adobefonts.py (this file)
    "com.adobe.fonts/check/family/consistent_upm",
    "com.adobe.fonts/check/find_empty_letters",
    "com.adobe.fonts/check/nameid_1_win_english",
    #
    # =======================================
    # From cff.py
    "com.adobe.fonts/check/cff_call_depth",
    "com.adobe.fonts/check/cff2_call_depth",
    "com.adobe.fonts/check/cff_deprecated_operators",
    #
    # =======================================
    # From cmap.py
    "com.google.fonts/check/family/equal_unicode_encodings",
    "com.google.fonts/check/all_glyphs_have_codepoints",
    #
    # =======================================
    # From dsig.py
    # "com.google.fonts/check/dsig",  # PERMANENTLY_EXCLUDED
    #
    # =======================================
    # From fontwerk.py
    # "com.fontwerk/check/no_mac_entries",
    # "com.fontwerk/check/vendor_id",  # PERMANENTLY_EXCLUDED
    "com.fontwerk/check/weight_class_fvar",
    "com.fontwerk/check/inconsistencies_between_fvar_stat",
    # "com.fontwerk/check/style_linking",  # PERMANENTLY_EXCLUDED
    #
    # =======================================
    # From fvar.py
    "com.google.fonts/check/varfont/regular_wght_coord",
    "com.google.fonts/check/varfont/regular_wdth_coord",
    "com.google.fonts/check/varfont/regular_slnt_coord",
    "com.google.fonts/check/varfont/regular_ital_coord",
    "com.google.fonts/check/varfont/regular_opsz_coord",
    "com.google.fonts/check/varfont/bold_wght_coord",
    "com.google.fonts/check/varfont/wght_valid_range",
    "com.google.fonts/check/varfont/wdth_valid_range",
    "com.google.fonts/check/varfont/slnt_range",
    "com.adobe.fonts/check/varfont/valid_axis_nameid",
    "com.adobe.fonts/check/varfont/valid_subfamily_nameid",
    "com.adobe.fonts/check/varfont/valid_postscript_nameid",
    "com.adobe.fonts/check/varfont/valid_default_instance_nameids",
    "com.adobe.fonts/check/varfont/same_size_instance_records",
    "com.adobe.fonts/check/varfont/distinct_instance_records",
    #
    # =======================================
    # From gdef.py
    # "com.google.fonts/check/gdef_spacing_marks",
    # "com.google.fonts/check/gdef_mark_chars",
    # "com.google.fonts/check/gdef_non_mark_chars",
    #
    # =======================================
    # From glyf.py
    "com.google.fonts/check/glyf_unused_data",
    "com.google.fonts/check/points_out_of_bounds",
    "com.google.fonts/check/glyf_non_transformed_duplicate_components",
    #
    # =======================================
    # From googlefonts.py
    "com.google.fonts/check/aat",
    "com.google.fonts/check/fvar_name_entries",
    # "com.google.fonts/check/varfont_has_instances",
    # "com.google.fonts/check/varfont_weight_instances",  # weak rationale
    "com.google.fonts/check/varfont_duplicate_instance_names",
    #
    # =======================================
    # From gpos.py
    "com.google.fonts/check/gpos_kerning_info",
    #
    # =======================================
    # From head.py
    "com.google.fonts/check/family/equal_font_versions",
    "com.google.fonts/check/unitsperem",
    "com.google.fonts/check/font_version",
    #
    # =======================================
    # From hhea.py
    "com.google.fonts/check/linegaps",
    "com.google.fonts/check/maxadvancewidth",
    #
    # =======================================
    # From hmtx.py
    "com.google.fonts/check/whitespace_widths",
    #
    # =======================================
    # From kern.py
    "com.google.fonts/check/kern_table",
    #
    # =======================================
    # From layout.py
    "com.google.fonts/check/layout_valid_feature_tags",
    "com.google.fonts/check/layout_valid_script_tags",
    "com.google.fonts/check/layout_valid_language_tags",
    #
    # =======================================
    # From loca.py
    "com.google.fonts/check/loca/maxp_num_glyphs",
    #
    # =======================================
    # From name.py
    "com.adobe.fonts/check/name/empty_records",
    # "com.google.fonts/check/name/no_copyright_on_description",  # PERMANENTLY_EXCLUDED # noqa
    "com.google.fonts/check/monospace",
    "com.google.fonts/check/name/match_familyname_fullfont",
    "com.google.fonts/check/family_naming_recommendations",
    "com.adobe.fonts/check/name/postscript_vs_cff",
    "com.adobe.fonts/check/name/postscript_name_consistency",
    "com.adobe.fonts/check/family/max_4_fonts_per_family_name",
    #
    # =======================================
    # From notofonts.py
    "com.google.fonts/check/cmap/unexpected_subtables",
    # "com.google.fonts/check/unicode_range_bits",
    # "com.google.fonts/check/name/noto_manufacturer",  # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/name/noto_designer",  # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/name/noto_trademark",  # PERMANENTLY_EXCLUDED
    "com.google.fonts/check/cmap/format_12",
    # "com.google.fonts/check/os2/noto_vendor",  # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/hmtx/encoded_latin_digits",  # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/hmtx/comma_period",  # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/hmtx/whitespace_advances",  # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/cmap/alien_codepoints",
    #
    # =======================================
    # From os2.py
    "com.google.fonts/check/family/panose_proportion",
    "com.google.fonts/check/family/panose_familytype",
    # "com.google.fonts/check/xavgcharwidth",  # PERMANENTLY_EXCLUDED
    "com.adobe.fonts/check/fsselection_matches_macstyle",
    "com.adobe.fonts/check/family/bold_italic_unique_for_nameid1",
    "com.google.fonts/check/code_pages",
    #
    # =======================================
    # From post.py
    "com.google.fonts/check/family/underline_thickness",
    "com.google.fonts/check/post_table_version",
    #
    # =======================================
    # From stat.py
    "com.google.fonts/check/varfont/stat_axis_record_for_each_axis",
    "com.adobe.fonts/check/stat_has_axis_value_tables",
    #
    # =======================================
    # From universal.py
    "com.google.fonts/check/ots",
    "com.google.fonts/check/name/trailing_spaces",
    "com.google.fonts/check/family/win_ascent_and_descent",
    "com.google.fonts/check/os2_metrics_match_hhea",
    "com.google.fonts/check/fontbakery_version",
    "com.google.fonts/check/ttx-roundtrip",
    "com.google.fonts/check/family/single_directory",
    "com.google.fonts/check/mandatory_glyphs",
    "com.google.fonts/check/whitespace_glyphs",
    # "com.google.fonts/check/whitespace_glyphnames",  # PERMANENTLY_EXCLUDED
    # "com.google.fonts/check/whitespace_ink",  # PERMANENTLY_EXCLUDED
    "com.google.fonts/check/required_tables",
    "com.google.fonts/check/unwanted_tables",
    "com.google.fonts/check/valid_glyphnames",
    "com.google.fonts/check/unique_glyphnames",
    "com.google.fonts/check/family/vertical_metrics",
    "com.google.fonts/check/STAT_strings",
    "com.google.fonts/check/rupee",
    # "com.google.fonts/check/unreachable_glyphs",
    # "com.google.fonts/check/contour_count",
    # "com.google.fonts/check/cjk_chws_feature",
    "com.google.fonts/check/transformed_components",
    # "com.google.fonts/check/dotted_circle",
    "com.google.fonts/check/gpos7",
    "com.adobe.fonts/check/freetype_rasterizer",
    "com.adobe.fonts/check/sfnt_version",
}

CHECKS_IN_THIS_FILE = [
    "com.adobe.fonts/check/family/consistent_upm",
    "com.adobe.fonts/check/find_empty_letters",
    "com.adobe.fonts/check/nameid_1_win_english",
]

SET_IMPORTED_CHECKS = set(
    UNIVERSAL_PROFILE_CHECKS
    + FONTWERK_PROFILE_CHECKS
    + GOOGLEFONTS_PROFILE_CHECKS
    + NOTOFONTS_PROFILE_CHECKS
)

ADOBEFONTS_PROFILE_CHECKS = [
    c for c in CHECKS_IN_THIS_FILE if c in SET_EXPLICIT_CHECKS
] + [c for c in SET_IMPORTED_CHECKS if c in SET_EXPLICIT_CHECKS]

OVERRIDDEN_CHECKS = [
    "com.google.fonts/check/whitespace_glyphs",
    "com.google.fonts/check/valid_glyphnames",
    "com.google.fonts/check/family/win_ascent_and_descent",
    "com.google.fonts/check/os2_metrics_match_hhea",
    "com.adobe.fonts/check/freetype_rasterizer",
    "com.google.fonts/check/fontbakery_version",
]


@check(
    id="com.adobe.fonts/check/family/consistent_upm",
    rationale="""
        While not required by the OpenType spec, we (Adobe) expect that a group
        of fonts designed & produced as a family have consistent units per em.
    """,
    proposal="https://github.com/googlefonts/fontbakery/pull/2372",
)
def com_adobe_fonts_check_family_consistent_upm(ttFonts):
    """Fonts have consistent Units Per Em?"""
    upm_set = set()
    for ttFont in ttFonts:
        upm_set.add(ttFont["head"].unitsPerEm)
    if len(upm_set) > 1:
        yield FAIL, Message(
            "inconsistent-upem",
            f"Fonts have different units per em: {sorted(upm_set)}.",
        )
    else:
        yield PASS, "Fonts have consistent units per em."


def _quick_and_dirty_glyph_is_empty(font, glyph_name):
    """
    This is meant to be a quick-and-dirty test to see if a glyph is empty.
    Ideally we'd use the glyph_has_ink() method for this, but for a family of
    large CJK CFF fonts with tens of thousands of glyphs each, it's too slow.

    Caveat Utilitor:
    If this method returns True, the glyph is definitely empty.
    If this method returns False, the glyph *might* still be empty.
    """
    if "glyf" in font:
        glyph = font["glyf"][glyph_name]
        if not glyph.isComposite():
            if glyph.numberOfContours == 0:
                return True
        return False

    if "CFF2" in font:
        top_dict = font["CFF2"].cff.topDictIndex[0]
    else:
        top_dict = font["CFF "].cff.topDictIndex[0]
    char_strings = top_dict.CharStrings
    char_string = char_strings[glyph_name]
    if len(char_string.bytecode) <= 1:
        return True
    return False


@check(
    id="com.adobe.fonts/check/find_empty_letters",
    rationale="""
        Font language, script, and character set tagging approaches typically have an
        underlying assumption that letters (i.e. characters with Unicode general
        category 'Ll', 'Lm', 'Lo', 'Lt', or 'Lu', which includes CJK ideographs and
        Hangul syllables) with entries in the 'cmap' table have glyphs with ink (with
        a few exceptions, notably the four Hangul "filler" characters: U+115F, U+1160,
        U+3164, U+FFA0).

        This check is intended to identify fonts in which such letters have been mapped
        to empty glyphs (typically done as a form of subsetting). Letters with empty
        glyphs should have their entries removed from the 'cmap' table, even if the
        empty glyphs are left in place (e.g. for CID consistency).

        The check will yield only a WARN if the blank glyph maps to a character in the
        range of Korean hangul syllable code-points, which are known to be used by font
        designers as a workaround to undesired behavior from InDesign's Korean IME
        (Input Method Editor).
        More details available at https://github.com/googlefonts/fontbakery/issues/2894
    """,
    proposal="https://github.com/googlefonts/fontbakery/pull/2460",
)
def com_adobe_fonts_check_find_empty_letters(ttFont):
    """Letters in font have glyphs that are not empty?"""
    cmap = ttFont.getBestCmap()
    blank_ok_set = ALL_HANGUL_SYLLABLES_CODEPOINTS - MODERN_HANGUL_SYLLABLES_CODEPOINTS
    num_blank_hangul_glyphs = 0
    passed = True

    # http://unicode.org/reports/tr44/#General_Category_Values
    letter_categories = {
        "Ll",
        "Lm",
        "Lo",
        "Lt",
        "Lu",
    }
    invisible_letters = {
        # Hangul filler chars (category='Lo')
        0x115F,
        0x1160,
        0x3164,
        0xFFA0,
    }
    for unicode_val, glyph_name in cmap.items():
        category = unicodedata.category(chr(unicode_val))
        glyph_is_empty = _quick_and_dirty_glyph_is_empty(ttFont, glyph_name)

        if glyph_is_empty and unicode_val in blank_ok_set:
            num_blank_hangul_glyphs += 1
            passed = False

        elif (
            glyph_is_empty
            and (category in letter_categories)
            and (unicode_val not in invisible_letters)
        ):
            yield FAIL, Message(
                "empty-letter",
                f"U+{unicode_val:04X} should be visible, "
                f"but its glyph ({glyph_name!r}) is empty.",
            )
            passed = False

    if passed:
        yield PASS, "No empty glyphs for letters found."

    elif num_blank_hangul_glyphs:
        yield WARN, Message(
            "empty-hangul-letter",
            f"Found {num_blank_hangul_glyphs} empty hangul glyph(s).",
        )


@check(
    id="com.adobe.fonts/check/nameid_1_win_english",
    rationale="""
        While not required by the OpenType spec, Adobe Fonts' pipeline requires
        every font to support at least nameID 1 (Font Family name) for platformID 3
        (Windows), encodingID 1 (Unicode), and languageID 1033/0x409 (US-English).
    """,
    proposal="https://github.com/googlefonts/fontbakery/issues/3714",
)
def com_adobe_fonts_check_nameid_1_win_english(ttFont, has_name_table):
    """Font has a good nameID 1, Windows/Unicode/US-English `name` table record?"""
    if not has_name_table:
        return FAIL, Message("name-table-not-found", "Font has no 'name' table.")

    nameid_1 = ttFont["name"].getName(1, 3, 1, 0x409)

    if nameid_1 is None:
        return FAIL, Message(
            "nameid-1-not-found",
            "Windows nameID 1 US-English record not found.",
        )

    try:
        nameid_1_unistr = nameid_1.toUnicode()
    except UnicodeDecodeError:
        return ERROR, Message(
            "nameid-1-decoding-error",
            "Windows nameID 1 US-English record could not be decoded.",
        )

    if not nameid_1_unistr.strip():
        return FAIL, Message(
            "nameid-1-empty",
            "Windows nameID 1 US-English record is empty.",
        )

    return PASS, "Font contains a good Windows nameID 1 US-English record."


profile.auto_register(
    globals(),
    filter_func=lambda _, checkid, __: checkid
    not in SET_IMPORTED_CHECKS - SET_EXPLICIT_CHECKS,
)


profile.check_log_override(
    # From universal.py
    "com.google.fonts/check/whitespace_glyphs",
    overrides=(("missing-whitespace-glyph-0x00A0", WARN, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "For Adobe, this is not as severe"
        " as assessed in the original check for 0x00A0."
    ),
)


profile.check_log_override(
    # From universal.py
    "com.google.fonts/check/valid_glyphnames",
    overrides=(("found-invalid-names", WARN, KEEP_ORIGINAL_MESSAGE),),
)


profile.check_log_override(
    # From universal.py
    "com.google.fonts/check/family/win_ascent_and_descent",
    overrides=(
        ("ascent", WARN, KEEP_ORIGINAL_MESSAGE),
        ("descent", WARN, KEEP_ORIGINAL_MESSAGE),
    ),
)


profile.check_log_override(
    # From universal.py
    "com.google.fonts/check/os2_metrics_match_hhea",
    overrides=(
        ("ascender", WARN, KEEP_ORIGINAL_MESSAGE),
        ("descender", WARN, KEEP_ORIGINAL_MESSAGE),
    ),
)


profile.check_log_override(
    # From universal.py
    "com.adobe.fonts/check/freetype_rasterizer",
    overrides=(("freetype-not-installed", ERROR, KEEP_ORIGINAL_MESSAGE),),
    reason="For Adobe, this check is very important and should never be skipped.",
)


profile.check_log_override(
    # From universal.py
    "com.google.fonts/check/fontbakery_version",
    overrides=(("connection-error", SKIP, KEEP_ORIGINAL_MESSAGE),),
    reason=(
        "For Adobe, users shouldn't be bothered with a failed check"
        " if their internet connection isn't functional.",
    ),
)


ADOBEFONTS_PROFILE_CHECKS = add_check_overrides(
    ADOBEFONTS_PROFILE_CHECKS, profile.profile_tag, OVERRIDDEN_CHECKS
)

profile.test_expected_checks(ADOBEFONTS_PROFILE_CHECKS, exclusive=True)
