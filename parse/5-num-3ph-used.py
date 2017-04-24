"""
Figure 5
The prevalence of key sharing.
How many website admins choose to host HTTPS content on 3rd party hosting services?

cut -f1,6 ../data/raw/results-certs-no-ca.txt | python 5.py

"""

import sys
sys.path.append('../utils')
from tqdm import *
from pkiutils import *
from collections import defaultdict

# Load mappings
cert_to_tph = load_cert_to_tph_map()
load_domain_to_org_map()
host_to_equiv_as = load_equiv_as_mapping()
alexa_top_10k = load_alexa_top_n(10000)
alexa_top_10k_orgs = collapse_domains_to_orgs(alexa_top_10k)

# Parse certificates, collecting all hosts used by each domain and each
# organization across all of their certificates
domain_to_hosts = defaultdict(set)
org_to_hosts = defaultdict(set)
for l in tqdm(sys.stdin):
  hash,san = l.strip().split("\t")
  if hash in cert_to_tph:
    hosts = cert_to_tph[hash]
  else:
    hosts = set([])
  ds = deserialize(san)
  if not ds: # skip those weird certs with non-domain CN (e.g. CP-...)
    continue
  cs = collapse_domains_to_orgs(ds)
  hosts = collapse_domains_to_orgs([x.name for x in hosts])
  for d in ds:
    domain_to_hosts[d].update(hosts)
  for c in cs:
    org_to_hosts[c].update(hosts)

# For each domain d, remove any org or AS owning d from its list of hosts,
# as we only want *third*-party hosting provideres for this plot
for d in tqdm(domain_to_hosts):
  hosts = domain_to_hosts[d]
  first_party_hosts = set([collapse_domain_to_org(d)])
  if d in host_to_equiv_as:
    first_party_hosts.add(host_to_equiv_as[d])
  domain_to_hosts[d] = hosts - first_party_hosts
  print d,domain_to_hosts[d]

# For each org o, ... (see above)
for o in tqdm(org_to_hosts):
  hosts = org_to_hosts[o]
  first_party_hosts = set([o])
  if o in host_to_equiv_as:
    first_party_hosts.add(host_to_equiv_as[o])
  org_to_hosts[o] = hosts - first_party_hosts

# Build a histogram of number of hosting services used for:
# domains, orgs, and top 10k orgs
domain_hosting_freq = defaultdict(int)
for d in domain_to_hosts:
  num_hosting_services_used = len(domain_to_hosts[d])
  domain_hosting_freq[num_hosting_services_used]+=1
org_hosting_freq = defaultdict(int)
for o in org_to_hosts:
  num_hosting_services_used = len(org_to_hosts[o])
  org_hosting_freq[num_hosting_services_used]+=1
top_org_hosting_freq = defaultdict(int)
for o in org_to_hosts:
  if o in alexa_top_10k_orgs:
    num_hosting_services_used = len(org_to_hosts[o])
    top_org_hosting_freq[num_hosting_services_used]+=1

# Calculate CDF based on histograms and write to file
curr = 0
total_domains = float(sum([y for (x,y) in domain_hosting_freq.iteritems()]))
with open('out/3ph-by-domain.txt','w') as f:
  for (num_hosting_services_used,num_domains) in sorted(domain_hosting_freq.iteritems(), key=lambda (x,y): x, reverse=False):
    curr += (num_domains/total_domains)
    f.write("{0} {1} {2}\n".format(num_hosting_services_used,num_domains,curr))
curr = 0
total_companies = float(sum([y for (x,y) in org_hosting_freq.iteritems()]))
with open('out/3ph-by-company.txt','w') as f:
  for (num_hosting_services_used,num_web_admins) in sorted(org_hosting_freq.iteritems(), key=lambda (x,y): x, reverse=False):
    curr += (num_web_admins/total_companies)
    f.write("{0} {1} {2}\n".format(num_hosting_services_used,num_web_admins,curr))
curr = 0
total_top_companies = float(sum([y for (x,y) in top_org_hosting_freq.iteritems()]))
with open('out/3ph-by-top-company.txt','w') as f:
  for (num_hosting_services_used,num_web_admins) in sorted(top_org_hosting_freq.iteritems(), key=lambda (x,y): x, reverse=False):
    curr += (num_web_admins/total_top_companies)
    f.write("{0} {1} {2}\n".format(num_hosting_services_used,num_web_admins,curr))
