#!/usr/bin/env python3
"""Why 'Held for Document Update' collapsed: editorial errata, routing, and the
2021-05-07 IESG statement.

Input:  a local copy of https://www.rfc-editor.org/errata.json  (curl -L !)
Usage:  python3 2026-09-11-rfc-errata-hfdu.py [path/to/errata.json] > out.json
"""
import json, sys, collections

PATH = sys.argv[1] if len(sys.argv) > 1 else 'scratch/errata_live.json'

# RPC staff names seen as verifiers, plus the generic 'RFC Editor' identity.
RPC_NAMES = {'RFC Editor', 'Madison Church', 'Alice Russo', 'Sandy Ginoza',
             'Jean Mahoney', 'Megan Ferguson', 'Rebecca VanRheenen', 'Karen Moore'}
HFDU = 'Held for Document Update'


def year(rec):
    try:
        y = int((rec.get('submit_date') or '')[:4])
    except ValueError:
        return None
    return y if 1990 <= y <= 2026 else None


def handler(rec):
    v = (rec.get('verifier_name') or '').strip()
    if not v:
        return 'unnamed'
    return 'RPC' if v in RPC_NAMES else 'AD/other'


def rate(recs, status=HFDU):
    return (sum(1 for r in recs if r['errata_status_code'] == status) / len(recs)) if recs else None


def shares(recs):
    n = len(recs)
    c = collections.Counter(r['errata_status_code'] for r in recs)
    return {'n': n, **{k: (c[k] / n if n else None) for k in
                       ('Verified', HFDU, 'Rejected', 'Reported')}}


def main():
    raw = json.load(open(PATH))
    rows = [r for r in raw if year(r) is not None]
    for r in rows:
        r['_y'] = year(r)

    out = {'source': PATH, 'records_total': len(raw), 'records_usable': len(rows),
           'records_dropped_bad_date': len(raw) - len(rows)}

    # -- update_date is unusable as a disposition date -------------------------
    upd = collections.Counter((r.get('update_date') or '')[:10] for r in raw)
    top, topn = upd.most_common(1)[0]
    out['update_date_unusable'] = {
        'distinct_dates': len(upd), 'most_common_date': top,
        'most_common_count': topn, 'share_of_corpus': topn / len(raw)}

    def cohort(y):
        for lo, hi, lbl in ((0, 2009, '<=2009'), (2010, 2012, '2010-2012'),
                            (2013, 2015, '2013-2015'), (2016, 2018, '2016-2018'),
                            (2019, 2021, '2019-2021'), (2022, 9999, '2022-2026')):
            if lo <= y <= hi:
                return lbl

    # -- 1/2/3: the trend, then the two obvious confounds ----------------------
    out['by_cohort_all'] = {}
    out['by_cohort_adjudicated'] = {}
    out['by_cohort_adjudicated_by_type'] = {'Technical': {}, 'Editorial': {}}
    out['editorial_share_of_filings'] = {}
    for lbl in ('<=2009', '2010-2012', '2013-2015', '2016-2018', '2019-2021', '2022-2026'):
        g = [r for r in rows if cohort(r['_y']) == lbl]
        adj = [r for r in g if r['errata_status_code'] != 'Reported']
        out['by_cohort_all'][lbl] = shares(g)
        out['by_cohort_adjudicated'][lbl] = shares(adj)
        out['editorial_share_of_filings'][lbl] = \
            sum(1 for r in g if r['errata_type_code'] == 'Editorial') / len(g)
        for t in ('Technical', 'Editorial'):
            out['by_cohort_adjudicated_by_type'][t][lbl] = \
                shares([r for r in adj if r['errata_type_code'] == t])

    # -- 4: maturation bound. If EVERY still-pending editorial erratum of a
    #       year eventually became HFDU, what is the most the rate could be?
    out['editorial_hfdu_upper_bound'] = {}
    for y in range(2016, 2027):
        g = [r for r in rows if r['_y'] == y and r['errata_type_code'] == 'Editorial']
        if not g:
            continue
        rep = sum(1 for r in g if r['errata_status_code'] == 'Reported')
        hf = sum(1 for r in g if r['errata_status_code'] == HFDU)
        out['editorial_hfdu_upper_bound'][str(y)] = {
            'total': len(g), 'reported': rep, 'hfdu': hf,
            'observed_share_of_all': hf / len(g),
            'max_possible_share': (hf + rep) / len(g)}

    # -- 5: who dispositioned it, and what they chose -------------------------
    ed = [r for r in rows if r['errata_type_code'] == 'Editorial'
          and r['errata_status_code'] in ('Verified', HFDU)]
    out['editorial_disposition_by_year'] = {}
    for y in range(2014, 2027):
        g = [r for r in ed if r['_y'] == y]
        if not g:
            continue
        rpc = [r for r in g if handler(r) == 'RPC']
        ad = [r for r in g if handler(r) == 'AD/other']
        out['editorial_disposition_by_year'][str(y)] = {
            'n': len(g), 'rpc_share': len(rpc) / len(g),
            'hfdu_rate_rpc': rate(rpc), 'hfdu_rate_ad': rate(ad),
            'hfdu_rate_all': rate(g)}

    # -- 6: decomposition, pre- vs post-statement -----------------------------
    eras = {'2016-2020': lambda y: 2016 <= y <= 2020, '2021-2026': lambda y: y >= 2021}
    dec = {}
    for lbl, f in eras.items():
        g = [r for r in ed if f(r['_y'])]
        rpc = [r for r in g if handler(r) == 'RPC']
        ad = [r for r in g if handler(r) != 'RPC']
        dec[lbl] = {'n': len(g), 'rpc_share': len(rpc) / len(g),
                    'hfdu_rate_rpc': rate(rpc), 'hfdu_rate_ad': rate(ad),
                    'hfdu_rate_all': rate(g)}
    a, b = dec['2016-2020'], dec['2021-2026']
    drop = a['hfdu_rate_all'] - b['hfdu_rate_all']
    cf_routing = b['rpc_share'] * a['hfdu_rate_rpc'] + (1 - b['rpc_share']) * a['hfdu_rate_ad']
    cf_rates = a['rpc_share'] * b['hfdu_rate_rpc'] + (1 - a['rpc_share']) * b['hfdu_rate_ad']
    dec['decomposition'] = {
        'observed_drop_pts': drop,
        'counterfactual_new_routing_old_rates': cf_routing,
        'routing_explains_pts': a['hfdu_rate_all'] - cf_routing,
        'routing_explains_frac': (a['hfdu_rate_all'] - cf_routing) / drop,
        'counterfactual_old_routing_new_rates': cf_rates,
        'rates_explain_pts': a['hfdu_rate_all'] - cf_rates,
        'rates_explain_frac': (a['hfdu_rate_all'] - cf_rates) / drop,
        'note': 'The two shares need not sum to 1: routing and per-handler rates '
                'changed together and the decomposition is not additive.'}
    out['decomposition'] = dec
    json.dump(out, sys.stdout, indent=1, sort_keys=False)
    print()


if __name__ == '__main__':
    main()
