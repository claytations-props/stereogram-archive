#!/usr/bin/env python3
"""Shared Phase 1 (schema v2) field derivations for the Stereograph Archive.

Every function here is mechanical and evidence-bound, per the Archive
Policy §4 source-fidelity rule: values are carried over verbatim,
extracted from the record's own statements (its title, its recorded
license, its Commons pins), or assigned by a stated rule from a
controlled list. Nothing here invents a date, place, creator, or
description. Used by tools/migrate_phase1.py (the one-time migration)
and tools/merge_batch.py (future batches), so both apply identical
rules. The rules are documented in docs/DATA_DICTIONARY.md (v2).
"""
import re

# Canonical key order of a v1 item object, as written in data.json.
V1_ORDER = ['title', 'place', 'year', 'sy', 'era', 'cats', 'blurb',
            'img', 'full', 'source', 'license', 'w', 'h', 'id', 'rect',
            'coll', 'vert', 'rot', 'range', 'f', 'depth', 'va', 'px',
            'cond']

# v2 fields, in record-file order after the v1 fields.
V2_ORDER = ['repository', 'collection_name', 'publisher', 'creator',
            'creator_dates', 'facets', 'publisher_series', 'date_edtf',
            'date_start', 'date_end', 'rights_uri', 'rights_basis',
            'license_url', 'source_page_id', 'source_revision_id',
            'source_sha1']

# Fields appended to each generated data.json item (subset of V2_ORDER;
# the full record lives in records/STA-####.json and catalog-v2.json).
GENERATED_EXTRA = ['repository', 'collection_name', 'publisher',
                   'creator', 'date_edtf', 'date_start', 'date_end',
                   'rights_uri']

# --- the coll split -------------------------------------------------------
# Rule per distinct v1 coll value, from the role the value itself names:
# a holding institution is a repository; the Dennis value names a
# collection held by NYPL; company names are publishers; "Getty Open
# Content" names an access program (no role cleanly evidenced in the
# record, so all three stay null); "Source unrecorded" is the unknown
# sentinel (all null).
COLL_SPLIT = {
    'Robert N. Dennis Collection': {
        'repository': 'New York Public Library',
        'collection_name': 'Robert N. Dennis Collection of Stereoscopic Views',
        'publisher': None},
    'Library of Congress': {
        'repository': 'Library of Congress',
        'collection_name': None, 'publisher': None},
    'Rijksmuseum': {
        'repository': 'Rijksmuseum',
        'collection_name': None, 'publisher': None},
    'The Metropolitan Museum of Art': {
        'repository': 'The Metropolitan Museum of Art',
        'collection_name': None, 'publisher': None},
    'National Archives': {
        'repository': 'National Archives',
        'collection_name': None, 'publisher': None},
    'Keystone View Company': {
        'repository': None, 'collection_name': None,
        'publisher': 'Keystone View Company'},
    'International Stereoscopic View Co.': {
        'repository': None, 'collection_name': None,
        'publisher': 'International Stereoscopic View Co.'},
    'Getty Open Content': {
        'repository': None, 'collection_name': None, 'publisher': None},
    'Source unrecorded': {
        'repository': None, 'collection_name': None, 'publisher': None},
}


def split_coll(coll):
    """(repository, collection_name, publisher) for a v1 coll value.
    Unknown values map to all-null rather than guessing a role."""
    m = COLL_SPLIT.get(coll)
    if m is None:
        return None, None, None
    return m['repository'], m['collection_name'], m['publisher']


# --- creator extraction from the record's own title -----------------------
_LIFE_TAIL = re.compile(
    r',\s*('
    r'\d{4}\s+or\s+\d{4}\s*[-\u2013\u2014]?\s*after\s+\d{4}'   # 1818 or 1824-after 1901
    r'|\d{4}\s*[-\u2013\u2014]\s*\d{4}'                        # 1833-1880
    r'|\d{4}\s*[-\u2013\u2014]'                                 # 1827- (open range)
    r'|b\.\s*\d{4}(?:\s+or\s+\d)?'                             # b. 1820 or 1
    r'|d\.\s*\d{4}'                                            # d. 1929
    r')\s*(?:\d+\s*)?$')


def _norm_range(s):
    return re.sub(r'\s*[-\u2013\u2014]\s*', '-', s.strip())


def attribution_tail(title):
    """The title's trailing 'by ...' attribution segment, or None."""
    i = title.lower().rfind(' by ')
    if i < 0:
        return None
    tail = title[i + 4:].strip()
    return tail or None


def extract_creator(title):
    """(creator, creator_dates) mechanically extracted from the title's
    'by <name>' attribution. The name is the exact string as printed;
    life dates as printed are returned separately. (None, None) when
    the title carries no attribution."""
    tail = attribution_tail(title)
    if tail is None:
        return None, None
    dates = None
    name = tail
    m = _LIFE_TAIL.search(tail)
    if m:
        dates = re.sub(r'\s+', ' ', m.group(1)).strip()
        name = tail[:m.start()].rstrip(', ').strip()
        # Source-title artifact: the life range sometimes appears twice
        # ("Stoddard, Seneca Ray, 1844-1917 , 1844-1917"); when the name
        # still ends with the same range, it is the duplicate, not part
        # of the name.
        m2 = re.search(r',\s*(\d{4}\s*[-\u2013\u2014]\s*\d{4})\s*$', name)
        if m2 and _norm_range(m2.group(1)) == _norm_range(dates):
            name = name[:m2.start()].rstrip(', ').strip()
    else:
        # A trailing bare numeral in the title is a file disambiguator
        # ("... 2"), not part of a name that otherwise has no digits.
        m3 = re.search(r'\s+(\d)$', name)
        if m3 and not re.search(r'\d', name[:m3.start()]):
            name = name[:m3.start()].strip()
    return (name or None), dates


# --- the generalized date guard -------------------------------------------
def life_forms(title):
    """Life-date forms stated in the title's attribution, as a list of
    (kind, values) where kind is 'range' | 'b.' | 'd.' | 'or-after' and
    values are the year strings involved."""
    tail = attribution_tail(title)
    if not tail:
        return []
    forms = []
    m = re.search(r'(\d{4})\s+or\s+(\d{4})\s*[-\u2013\u2014]?\s*after\s+(\d{4})', tail)
    if m:
        forms.append(('or-after', (m.group(1), m.group(2), m.group(3))))
        return forms
    m = re.search(r'(\d{4})\s*[-\u2013\u2014]\s*(\d{4})', tail)
    if m:
        forms.append(('range', (m.group(1), m.group(2))))
    else:
        mo = re.search(r'(\d{4})\s*[-\u2013\u2014]\s*$', tail)
        if mo:
            forms.append(('range-open', (mo.group(1),)))
    mb = re.search(r'\bb\.\s*(\d{4})', tail)
    if mb:
        forms.append(('b.', (mb.group(1),)))
    md = re.search(r'\bd\.\s*(\d{4})', tail)
    if md:
        forms.append(('d.', (md.group(1),)))
    return forms


def year_matches_life(year, forms):
    """True when a v1 year string is exactly one of the life forms:
    the full range, a b./d. year, or the first year of an or-after form."""
    y = year.replace('c. ', '').strip()
    for kind, vals in forms:
        if kind == 'range' and y == f'{vals[0]}\u2013{vals[1]}':
            return True
        if kind == 'range-open' and y == vals[0]:
            return True
        if kind in ('b.', 'd.') and y == vals[0]:
            return True
        if kind == 'or-after' and y == vals[0]:
            return True
    return False


_MONTHS = (r'Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|'
           r'Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|'
           r'Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?')


def explicit_view_year(title):
    """A real date stated by the view's own statement in the title,
    outside the attribution: 'July 24, 1875' or '(Apr. 23, (18)79)'.
    Returns the 4-digit year as an int, or None."""
    m = re.search(rf'(?:{_MONTHS})\.?\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+(\d{{4}})',
                  title)
    if m:
        return int(m.group(1))
    m = re.search(r'\((\d{2})\)(\d{2})', title)
    if m:
        return int(m.group(1) + m.group(2))
    return None


def era_of(sy, year):
    if year == 'Undated':
        return 'undated'
    return 'early' if sy < 1870 else ('mid' if sy < 1900 else 'late')


def apply_date_guard(entry):
    """Generalized life-date guard for newly ingested entries (the
    sweep's guard, completed with the forms it missed). Mutates the
    entry's year/sy/era when its year is only a creator life form;
    rescues a real view date stated in the title when one exists.
    Returns a list of human-readable log lines (possibly empty)."""
    logs = []
    year = entry.get('year', '')
    if year == 'Undated':
        return logs
    forms = life_forms(entry.get('title', ''))
    if not forms or not year_matches_life(year, forms):
        return logs
    view = explicit_view_year(entry['title'])
    if view is not None and str(view) != year:
        entry['year'] = str(view)
        entry['sy'] = view
        entry['era'] = era_of(view, entry['year'])
        logs.append(f"date guard: year '{year}' is the creator's life dates; "
                    f"the title states the view date {view}, which replaces it")
    else:
        entry['year'] = 'Undated'
        entry['sy'] = 1900
        entry['era'] = 'undated'
        logs.append(f"date guard: year '{year}' is only the creator's life "
                    f"dates in the title; marked Undated")
    return logs


# --- EDTF normalization -----------------------------------------------------
def edtf_from_year(year):
    """(date_edtf, date_start, date_end) normalized from a v1 display
    year string that states real evidence. Conventions (documented in
    docs/DATA_DICTIONARY.md): 'c. YYYY' -> 'YYYY~' with a +-5 span;
    a work range 'YYYY-YYYY' -> the EDTF interval with exact bounds;
    'c. YYYY-YYYY' -> 'YYYY~/YYYY~' with the +-5 applied to the outer
    bounds; a decade 'YYY0s' -> 'YYY X'; the century forms '1800s' /
    '1900s' (used by legacy passes for a whole century) -> '18XX' /
    '19XX'; 'Undated' -> (None, None, None). Raises ValueError on a
    shape it does not recognize, so unknown forms fail loudly."""
    y = year.strip()
    if y == 'Undated':
        return None, None, None
    m = re.fullmatch(r'c\. (\d{4})', y)
    if m:
        v = int(m.group(1))
        return f'{v}~', v - 5, v + 5
    m = re.fullmatch(r'(\d{4})', y)
    if m:
        v = int(m.group(1))
        return str(v), v, v
    m = re.fullmatch(r'c\. (\d{4})\u2013(\d{4})', y)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return f'{a}~/{b}~', a - 5, b + 5
    m = re.fullmatch(r'(\d{4})\u2013(\d{4})', y)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return f'{a}/{b}', a, b
    if y == '1800s':
        return '18XX', 1800, 1899
    if y == '1900s':
        return '19XX', 1900, 1999
    m = re.fullmatch(r'(\d{3}0)s', y)
    if m:
        v = int(m.group(1))
        return f'{m.group(1)[:3]}X', v, v + 9
    if y == 'Date uncertain, 1800s\u20131920s':
        return '18XX/19XX', 1800, 1929
    raise ValueError(f'unrecognized year shape: {year!r}')


# --- rights -----------------------------------------------------------------
_RIGHTS_BASIS = {
    'Public domain': (
        'https://rightsstatements.org/vocab/NoC-US/1.0/',
        'Source record marks the work public domain (Wikimedia Commons '
        'license short name: Public domain). Rights URI assigned by '
        'rule: RightsStatements.org No Copyright - United States '
        '(NoC-US).'),
    'CC0': (
        None,  # filled from the recorded deed URL
        'Source record carries a CC0 dedication (Wikimedia Commons '
        'license short name: CC0). Rights URI is the CC0 deed URL '
        'recorded from the source page.'),
    'No restrictions': (
        None,  # deliberately null; see basis
        "Source record is marked 'No restrictions' (Wikimedia Commons "
        'license short name): a no-known-copyright-restrictions '
        'statement (Flickr Commons usage terms; the exact URL is in '
        'license_url). No RightsStatements.org URI was assigned, '
        'because that label is not a public-domain determination.'),
}
CC0_DEED = 'https://creativecommons.org/publicdomain/zero/1.0/'


def rights_for(license_label, license_url):
    """(rights_uri, rights_basis) for a recorded license label and the
    exact license URL from the source page (possibly None)."""
    rule = _RIGHTS_BASIS.get(license_label)
    if rule is None:
        return None, ('License label not covered by the Phase 1 rights '
                      'rules; no rights URI assigned.')
    uri, basis = rule
    if license_label == 'CC0':
        uri = license_url or CC0_DEED
    return uri, basis


# --- record assembly --------------------------------------------------------
def build_v2_record(entry, pins=None, publisher_series=None):
    """Assemble a complete v2 record (ordered dict) from a v1 entry.
    pins: optional dict with license_url, source_page_id,
    source_revision_id, source_sha1 (from the fixity manifest and/or
    the Commons API). Display fields are taken from the entry as-is;
    callers apply any authorized corrections BEFORE calling this."""
    pins = pins or {}
    rec = {}
    for k in V1_ORDER:
        rec[k] = entry[k]
    repo, coll_name, publisher = split_coll(entry['coll'])
    rec['repository'] = repo
    rec['collection_name'] = coll_name
    rec['publisher'] = publisher
    creator, creator_dates = extract_creator(entry['title'])
    rec['creator'] = creator
    rec['creator_dates'] = creator_dates
    rec['facets'] = list(entry['cats'])
    rec['publisher_series'] = publisher_series
    edtf, start, end = edtf_from_year(entry['year'])
    rec['date_edtf'] = edtf
    rec['date_start'] = start
    rec['date_end'] = end
    license_url = pins.get('license_url')
    uri, basis = rights_for(entry['license'], license_url)
    rec['rights_uri'] = uri
    rec['rights_basis'] = basis
    rec['license_url'] = license_url
    rec['source_page_id'] = pins.get('source_page_id')
    rec['source_revision_id'] = pins.get('source_revision_id')
    rec['source_sha1'] = pins.get('source_sha1')
    return rec


def generated_item(rec):
    """The data.json item for a v2 record: the v1 fields in canonical
    order plus the appended Phase 1 fields."""
    out = {}
    for k in V1_ORDER:
        out[k] = rec[k]
    for k in GENERATED_EXTRA:
        out[k] = rec[k]
    return out
