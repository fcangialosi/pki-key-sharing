"""
Figure 2

How many certificates does each organization own?

cut -f1,6 ../../results-certs-no-ca-041915.tsv | python 2-certs-per-org.py

"""

import sys
sys.path.append('../utils')
from tqdm import *
from pkiutils import *
from collections import defaultdict

# Load mappings
load_domain_to_org_map()

org_to_certs = defaultdict(int)
for l in tqdm(sys.stdin):
  hash,san = l.strip().split("\t")
  ds = deserialize(san)
  if not ds: # skip those weird certs with non-domain CN (e.g. CP-...)
    continue
  os = collapse_domains_to_orgs(ds)
  for org in os:
    org_to_certs[org]+=1

ncerts_to_freq = defaultdict(int)
for org in org_to_certs:
  cnt = org_to_certs[org]
  ncerts_to_freq[cnt]+=1

print "# freq certs-per-org"
for ncerts in sorted(ncerts_to_freq.keys()):
  print ncerts_to_freq[ncerts], ncerts
