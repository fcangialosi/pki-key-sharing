"""
Figure 4

How many unique third-party hosting services host each certificate?

cut -f1,6 ../../results-certs-no-ca-041915.tsv | python 4-hosts-per-cert.py

"""

import sys
sys.path.append('../utils')
from tqdm import *
from pkiutils import *
from collections import defaultdict

cert_to_hosts = load_cert_to_tph_map()

nhosts_to_freq = defaultdict(int)
for l in tqdm(sys.stdin):
  hash,san = l.strip().split("\t")
  if hash in cert_to_hosts:
    hosts = cert_to_hosts[hash]
  else: # host themselves
    hosts = set([])
  ds = deserialize(san)
  if not ds: # skip those weird certs with non-domain CN (e.g. CP-...)
    continue

  nhosts_to_freq[len(hosts)]+=1

print "# freq hosts-per-cert"
for nhosts in sorted(nhosts_to_freq.keys()):
  print nhosts_to_freq[nhosts], nhosts
