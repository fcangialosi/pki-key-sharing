"""

Develop set of possible candidate domains that represent the same organization
as each AS name. Actual set is then pruned manually.

cut -f 1,6 ../raw/results-certs-no-ca-041915.txt | python generate-asn-domain-candidates.py

"""

import sys
sys.path.append('../../utils')
from tqdm import *
from pkiutils import *

keyword_to_asn = {}
keyword_to_domains = {}
with open('../manual/asn_keywords') as f:
  for l in f:
    asn,keyword = l.strip().split("\t")
    keyword_to_asn[keyword] = asn
    keyword_to_domains[keyword] = set()

all_domains = set()
for l in tqdm(sys.stdin):
  hash,ds = l.strip().split("\t")
  ds = deserialize(ds)
  all_domains.update(ds)

for domain in all_domains:
  for keyword in keyword_to_domains.keys():
    if keyword in domain:
      keyword_to_domains[keyword].add(domain)

for keyword in keyword_to_domains:
  print "{} {}".format(
      keyword_to_asn[keyword],
      set_of_strings_to_clean_string(keyword_to_domains[keyword])
  )

