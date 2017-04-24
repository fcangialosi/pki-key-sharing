"""

Generate the mapping of each cert to a set of HostingProvider instances that
represent third party providers hosting that certificate, labeled according to
whether their identity was determined via rDNS or AS Org Name lookup.

cut -f1,6,25 ../raw/results-certs-no-ca-041915.txt | generate-cert-to-hosts.py

"""
import sys
sys.path.append('../../utils')
from tqdm import *
from pkiutils import *
from collections import defaultdict

host_to_equiv_as = load_equiv_as_mapping()

cert_to_hosts = {}

# TODO SOMEHOW GENERATE THE LIST OF ALL-TPH.TSV
with open('../raw/all-tph.tsv') as f:
  for l in tqdm(f):
    hash,hosting = l.strip().split("\t")
    hosting = deserialize(hosting)
    cert_to_hosts[hash] = set([x.strip() for x in hosting])

for l in tqdm(sys.stdin):
  hash,san,rdns = l.strip().split("\t")
  if hash in cert_to_hosts:
    hosts = cert_to_hosts[hash]
  else:
    hosts = set([])
  ds = deserialize(san)
  if not ds: # skip those weird certs with non-domain CN (e.g. CP-...)
    continue
  cn = ds[0]

  blacklist = set([cn,"None","none","Unknown","unknown"])
  rdns = set([x.strip() for x in deserialize(rdns)]) - blacklist
  asns = (hosts - rdns) - blacklist

  hosting_providers = set([])
  for asn in asns:
    curr = asn
    if asn in host_to_equiv_as:
      curr = host_to_equiv_as[asn]
    hosting_providers.add(HostingProvider(curr,HostingProvider.ASN))
  for rdn in rdns:
    curr = extract_tld_plus_one(rdn)
    if curr in host_to_equiv_as:
      hosting_providers.add(
          HostingProvider(host_to_equiv_as[curr], HostingProvider.ASN))
    else:
      hosting_providers.add(HostingProvider(curr, HostingProvider.RDNS))

  cert_to_hosts[hash] = hosting_providers

for cert in cert_to_hosts:
    rdns = ",".join(map(lambda h : h if type(h) is str else h.name, filter((lambda h : (type(h) is str) or h.t == HostingProvider.RDNS), cert_to_hosts[cert])))
    asns = ",".join(map(lambda h : h.name, filter((lambda h : (not type(h) is str) and h.t == HostingProvider.ASN), cert_to_hosts[cert])))
    print cert, rdns, asns
#with open('../cert-to-hosts.pkl','w') as f:
#  f.write(dumps(cert_to_hosts))
