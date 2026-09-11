#!/usr/bin/env python3
"""Who is left waiting in the RFC errata queue?

Question: an erratum in the "Reported" state has been submitted and not yet
adjudicated by anyone. How old is that queue, and is it evenly distributed
across the two errata types?

Prior art: McQuistin et al., "Errare humanum est: What do RFC Errata say about
Internet Standards?" (2023) reports that 14.2% of errata sit unverified and
buckets status by the *publication year of the RFC*. This script buckets by the
*submission date of the erratum*, which is what determines how long the queue
has actually been waiting, and splits the residual by errata type.

Input: https://www.rfc-editor.org/api/v1/errata.json  (note: /errata.json 302s
there; a plain curl without -L yields an empty file.)

Usage: python3 2026-09-11-rfc-errata-residual.py errata.json [--asof YYYY-MM-DD]
"""
import json, sys, datetime, collections, statistics

CUTOFF = datetime.date(2021, 5, 7)   # IESG statement delegating editorial triage to the RPC


def parse_submit(s, asof):
    try:
        v = datetime.date(*map(int, s.split('-')))
    except Exception:
        return None
    # one record carries submit_date 9999-04-13; drop anything in the future
    return v if v <= asof else None


def main():
    path = sys.argv[1]
    asof = datetime.date.today()
    if '--asof' in sys.argv:
        asof = datetime.date(*map(int, sys.argv[sys.argv.index('--asof') + 1].split('-')))

    raw = json.load(open(path))
    rows = [x for x in raw if parse_submit(x['submit_date'], asof)]
    dropped = len(raw) - len(rows)

    age = lambda x: (asof - parse_submit(x['submit_date'], asof)).days / 365.25
    reported = [x for x in rows if x['errata_status_code'] == 'Reported']
    ages = sorted(age(x) for x in reported)

    out = {
        'asof': asof.isoformat(),
        'source': 'https://www.rfc-editor.org/api/v1/errata.json',
        'n_total': len(raw),
        'n_usable': len(rows),
        'n_dropped_bad_submit_date': dropped,
        'status_counts': dict(collections.Counter(x['errata_status_code'] for x in rows)),
        'queue': {
            'n': len(reported),
            'median_age_years': round(statistics.median(ages), 2),
            'max_age_years': round(max(ages), 2),
            'share_technical': round(
                sum(1 for x in reported if x['errata_type_code'] == 'Technical') / len(reported), 4),
            'at_least_years': {str(t): sum(1 for a in ages if a >= t) for t in (1, 2, 3, 5, 10, 15)},
            'top_docs': collections.Counter(x['doc-id'] for x in reported).most_common(12),
        },
    }

    # Residual by submission year, split by type. Comparing the two types *within*
    # a year is the age-controlled comparison: both have had exactly as long to be
    # adjudicated. Comparing across years is not, and is only read as a gradient.
    by_year = collections.defaultdict(list)
    for x in rows:
        by_year[parse_submit(x['submit_date'], asof).year].append(x)
    resid = []
    for y in sorted(by_year):
        g = by_year[y]
        cell = {'year': y, 'n': len(g)}
        for typ, key in (('Technical', 'tech'), ('Editorial', 'edit')):
            sub = [x for x in g if x['errata_type_code'] == typ]
            cell['n_' + key] = len(sub)
            cell['residual_' + key] = (
                round(sum(1 for x in sub if x['errata_status_code'] == 'Reported') / len(sub), 4)
                if sub else None)
        resid.append(cell)
    out['residual_by_submit_year'] = resid

    # The concrete, cheapest-to-clear list: editorial errata submitted before the
    # 2021 IESG statement that are still unadjudicated. Editorial triage sits with
    # the RPC and does not require an Area Director.
    stranded = sorted((x for x in reported
                       if x['errata_type_code'] == 'Editorial'
                       and parse_submit(x['submit_date'], asof) < CUTOFF),
                      key=lambda x: x['submit_date'])
    out['stranded_editorial_pre_policy'] = {
        'policy_date': CUTOFF.isoformat(),
        'n': len(stranded),
        'age_years_min': round(min(age(x) for x in stranded), 2),
        'age_years_max': round(max(age(x) for x in stranded), 2),
        'items': [{'errata_id': x['errata_id'], 'doc': x['doc-id'],
                   'section': x['section'], 'submit_date': x['submit_date'],
                   'submitter': x['submitter_name']} for x in stranded],
    }

    # NEGATIVE RESULT, kept deliberately. The attempt to attribute the recent
    # technical/editorial divergence to the 2021 statement does not survive:
    # the aggregate pre/post split reverses, because the post group is dominated
    # by errata still legitimately in flight.
    pre = [x for x in rows if x['errata_type_code'] == 'Editorial'
           and parse_submit(x['submit_date'], asof) < CUTOFF]
    post = [x for x in rows if x['errata_type_code'] == 'Editorial'
            and parse_submit(x['submit_date'], asof) >= CUTOFF]
    out['policy_attribution_attempt'] = {
        'verdict': 'NOT CONFIRMED',
        'editorial_residual_pre': round(sum(1 for x in pre if x['errata_status_code'] == 'Reported') / len(pre), 4),
        'editorial_residual_post': round(sum(1 for x in post if x['errata_status_code'] == 'Reported') / len(post), 4),
        'why_not': 'The post-policy group still contains errata legitimately in '
                   'flight, so its residual is inflated; and per-year, the 2014 and '
                   '2015 editorial residuals are already as low as every post-policy '
                   'year. There is no age gradient in the editorial series to invert.',
    }
    json.dump(out, sys.stdout, indent=1)
    print()


if __name__ == '__main__':
    main()
