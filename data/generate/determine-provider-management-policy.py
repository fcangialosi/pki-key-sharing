"""

Looks at the set of issuing CAs for all certs hosted by a given provider and
makes a decision whether each provider exhibits centralized or decentralized
(self) management.

After running this script, run determine-cert-management-policy.py to then use
this data to determine whether each certificate is centraized/decentralized.

cut -f1,3,6,7,10,13,25,27,30 ../raw/results-certs-no-ca-041915.txt | python determine-provider-management-policy.py

"""

import sys
sys.path.append('../../utils')
from tqdm import *
from as2ISP import *
from pkiutils import *
from generate_cdf import *
from collections import defaultdict

as2ISP = AS2ISP(os.path.abspath("../"))

cnt = 0

rdns_issuers = {}
as_issuers = {}
equiv_as_issuers = {}

rdns_mgmt = {}
as_mgmt = {}

host_to_equiv_as = load_equiv_as_mapping()
collapsible = host_to_equiv_as.values()
collapsed_rdns = defaultdict(set)
collapsed_asns = defaultdict(set)

## Count the certificates' issuer common name depending on their RDNS and ASNs
for l in tqdm(sys.stdin):
    hash, isca, dn, is_cn, notafter, lastdate, rdns, rv_status, asn = l.strip().split("\t")
    dns = deserialize(dn)
    rdns = deserialize(rdns)

    lastdate = lastdate.split(" ")[0].replace("-","")
    if not lastdate:
        lastdate = notafter.split(" ")[0].replace("-","")

    asns = []
    for x in deserialize(asn):
        f = x.split("/")[0]
        asns.extend(f.split("+"))
    asns = set(asns)


    if( len(dns) == 0):
        continue

    if(isca == "True"):
        continue

    is_cn = get_issuer(is_cn)

    if (len(rdns) != 0):
        for rdn in rdns:
            if(rdn != "None" and rdn != "Unknown" and rdn not in dns):
                if rdn in host_to_equiv_as:
                    equiv_as = host_to_equiv_as[rdn]
                    collapsed_rdns[equiv_as].add(rdn)
                if(rdn not in rdns_issuers):
                    rdns_issuers[rdn] = {}
                rdns_issuers[rdn][is_cn] = rdns_issuers[rdn].get(is_cn, 0) + 1

    else: ## We need to see ASN
        for asnum in asns:
            asname = as2ISP.getISP(lastdate, asnum)[0]
            if asname in host_to_equiv_as:
                equiv_as = host_to_equiv_as[asname]
                collapsed_asns[equiv_as].add(asnum)
            if asname in collapsible:
                collapsed_asns[asname].add(asnum)
            if(asnum not in as_issuers):
                as_issuers[asnum] = {}
            as_issuers[asnum][is_cn] = as_issuers[asnum].get(is_cn, 0) + 1

for parent in collapsed_rdns:
    totals = defaultdict(int)
    for rdn in collapsed_rdns[parent]:
        for is_cn in rdns_issuers[rdn]:
            totals[is_cn] += rdns_issuers[rdn][is_cn]
    for asnum in collapsed_asns[parent]:
        for is_cn in as_issuers[asnum]:
            totals[is_cn] += as_issuers[asnum][is_cn]
    for rdn in collapsed_rdns[parent]:
        for is_cn in totals:
            rdns_issuers[rdn][is_cn] = totals[is_cn]
    for asnum in collapsed_asns[parent]:
        for is_cn in totals:
            as_issuers[asnum][is_cn] = totals[is_cn]

### Identifying whether they are performing central management or not

for rdn in rdns_issuers:
    all_num = sum(map(lambda v: rdns_issuers[rdn][v], rdns_issuers[rdn]))
    max_num = max(rdns_issuers[rdn].values())

    if(all_num <= max_num * 2):
        mgmt = "centralized"
    else:
        mgmt = "decentralized"

    rdns_mgmt[rdn] = [mgmt, all_num, max_num * 1.0 / all_num]

for asn in as_issuers:
    all_num = sum(map(lambda v: as_issuers[asn][v], as_issuers[asn]))
    max_num = max(as_issuers[asn].values())

    if(all_num <= max_num * 2):
        mgmt = "centralized"
    else:
        mgmt = "decentralized"

    as_mgmt[asn] = [mgmt, all_num, max_num * 1.0 / all_num]


### record

w = open("../rdns-management.tsv", "w")
for rdn in rdns_mgmt:
    w.write("%s\n" % "\t".join([rdn] + map(str, rdns_mgmt[rdn])))

w = open("../asn-management.tsv", "w")
for asn in as_mgmt:
    w.write("%s\n" % "\t".join([asn] + map(str, as_mgmt[asn])))
