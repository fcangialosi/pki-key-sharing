"""
Figure 7
Trust aggregation

How many keys have third-parties aggregated and at how small of a subset of
them?

cut -f1,6,25 ../data/raw/results-certs-no-ca-041915.tsv | python 7-trust-agg.py

"""

import sys
sys.path.append('../utils')
from tqdm import *
from pkiutils import *
from collections import defaultdict

cert_to_tph = load_cert_to_tph_map()
load_domain_to_org_map()
host_to_equiv_as = load_equiv_as_mapping()

host_to_domains = defaultdict(set)
host_to_companies = defaultdict(set)
for l in tqdm(sys.stdin):
  hash,san,rdns = l.strip().split("\t")
  if hash in cert_to_tph:
    hosts = cert_to_tph[hash]
  else: # host themselves
    hosts = set([])
  ds = set(deserialize(san))
  if not ds: # skip those weird certs with non-domain CN (e.g. CP-...)
    continue

  same_org_ds = defaultdict(set)
  same_org_cs = defaultdict(set)

  for host in hosts:
    if host.t == HostingProvider.ASN:
      for d in ds:
        ex = extract_tld_plus_one(d)
        if ex in host_to_equiv_as and host_to_equiv_as[ex] == host.name:
          c = collapse_domain_to_org(d)
          same_org_ds[host].add(d)
          same_org_cs[host].add(c)
    elif host.t == HostingProvider.RDNS:
      for d in ds:
        ex = extract_tld_plus_one(d)
        if ex == host.name or (ex in host_to_equiv_as and host_to_equiv_as[ex] == host.name):
          c = collapse_domain_to_org(d)
          same_org_ds[host].add(d)
          same_org_cs[host].add(c)
  cs = collapse_domains_to_orgs(ds)

  for host in hosts:
    host_to_domains[host].update(ds-same_org_ds[host])
    host_to_companies[host].update(cs-same_org_cs[host])

with open('out/orgs-per-host.txt','w') as f:
  sorted_host_company_pairs = sorted(host_to_companies.iteritems(), key=lambda (host,cs): len(cs), reverse=True)
  for (host,cs) in sorted_host_company_pairs:
    f.write("{}\t{}\t{}\n".format(host.name,len(cs),len(host_to_domains[host])))

top_fraction = 0.01
total_hosts = len(sorted_host_company_pairs)
top_company_pairs = sorted_host_company_pairs[:int(total_hosts*top_fraction)]
orgs_from_top_companies = map(lambda (host,cs) : cs, top_company_pairs)
orgs_from_all_companies = map(lambda (host,cs) : cs, sorted_host_company_pairs)
top_orgs_combined = set().union(*orgs_from_top_companies)
all_orgs_combined = set().union(*orgs_from_all_companies)
fraction_of_orgs = (float(len(top_orgs_combined)) / len(all_orgs_combined))
print "Top {}% of providers hold keys for {}% of all organizations".format(
    int(top_fraction*100),
    int(fraction_of_orgs*100))
