"""
Figure 3

How many unique organizations appear on each certificate?

cut -f1,6 ../../results-certs-no-ca-041915.tsv | python 3-orgs-per-cert.py

"""

import sys
sys.path.append('../utils')
from tqdm import *
from pkiutils import *
from collections import defaultdict

# Load mappings
load_domain_to_org_map()

norgs_to_freq = defaultdict(int)
for l in tqdm(sys.stdin):
  hash,san = l.strip().split("\t")
  ds = deserialize(san)
  if not ds: # skip those weird certs with non-domain CN (e.g. CP-...)
    continue
  os = collapse_domains_to_orgs(ds)
  norgs_to_freq[len(os)]+=1

print "# freq orgs-per-cert"
for norgs in sorted(norgs_to_freq.keys()):
  print norgs_to_freq[norgs], norgs
