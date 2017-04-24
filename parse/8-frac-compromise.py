"""
Figure 8

How many hosting services would one have to compromise to get Y% of all distinct
(domains'|organizations') keys?

cut -f1,6 ../data/raw/results-certs-no-ca-041915.txt | python 8-frac-compromise.py

"""

import sys
sys.path.append('../utils')
from tqdm import *
from pkiutils import *
from collections import defaultdict

# Load mappings
cert_to_tph = load_cert_to_tph_map()
load_domain_to_org_map()
top_1k = set(load_alexa_top_n(1000))
top_1m = set(load_alexa_top_n(1000000))

# Just triple-check that we don't have any of these floating around
blacklist = ['unknown','Unknown','unknown.','Unknown.','']

host_to_1k_domains = defaultdict(set)
host_to_1m_domains = defaultdict(set)
host_to_all_domains = defaultdict(set)

# Generate the mapping of host to the set of all domains it hosts, for top 1k,
# top 1mil and all domains
for l in tqdm(sys.stdin):
  hash,san = l.strip().split("\t")
  if hash in cert_to_tph:
    hosts = cert_to_tph[hash]
  else: # host themselves
    hosts = set([])
  ds = deserialize(san)
  if not ds: # skip those weird certs with non-domain CN (e.g. CP-...)
    continue

  top_1k_domains = filter(lambda d: d in top_1k, ds)
  top_1m_domains = filter(lambda d: d in top_1m, ds)

  for host in hosts:
    if host:
      host = host.name
      if host and not host in blacklist:
        host_to_1k_domains[host].update(top_1k_domains)
        host_to_1m_domains[host].update(top_1m_domains)
        host_to_all_domains[host].update(ds)

# Given a mapping of hosts to domains, greedily determine at each point in time
# which hosting provider will provide the greatest number of unique domains not
# yet acquired
def greedy_compromise(outfile, host_to_domains):
  sys.stderr.write("Generating {}...\n".format(outfile))
  num_https = float(len(set(flatten([ds for (host,ds) in host_to_domains.iteritems()]))))
  with open(outfile,'w') as f:
    i = 1
    curr = set([])
    prev = 0
    curr_hosts = set([])
    hosts = sorted(host_to_domains.iteritems(), key=lambda (host,ds): len(ds), reverse=True)
    while len(curr) < num_https:
      best_so_far = 0
      prev_best = -1
      best_host = None
      for (host,ds) in hosts:
        if host in curr_hosts:
          continue
        if len(ds) < best_so_far:
          break
        if best_so_far == prev_best:
          break
        addition_would_be = len(ds - curr)
        best_so_far = max(addition_would_be,best_so_far)
        if best_so_far == addition_would_be:
          best_host = host
      prev_best = best_so_far
      curr_hosts.add(best_host)
      curr.update(host_to_domains[best_host])
      if (len(curr) - prev) == 1:
        break
      f.write("{0}\t{1}\t{2}\t{3}\n".format(i,best_host,len(curr),float(len(curr))/num_https))
      prev = len(curr)
      i+=1

    curr = len(curr)
    while curr < num_https:
      f.write("{0}\t{1}\t{2}\t{3}\n".format(i,"X",curr,float(curr)/num_https))
      curr += 1
      i += 1

# Generate results for each group
greedy_compromise('out/top-1k-compromise.tsv', host_to_1k_domains)
greedy_compromise('out/top-1m-compromise.tsv', host_to_1m_domains)
greedy_compromise('out/top-all-compromise.tsv', host_to_all_domains)
