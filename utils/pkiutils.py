import sys,os
from tqdm import *
from tldextract import extract
from cPickle import dumps,loads
from collections import defaultdict

reload(sys)
sys.setdefaultencoding('utf8')

cwd = os.getcwd()
PROJECT_ROOT = cwd.split("release/")[0] + "release/"
DATASET_DIR = PROJECT_ROOT + 'data/'
RAW_DATA_DIR = DATASET_DIR + 'raw/'

domain_to_org = None

###############################################################################
# Helpers
###############################################################################
def deserialize(x,sep=','):
    """
    Convert string "[a,b,c..]" to array [a,b,c..]
    """

    if x == "[]" or x == "[None]":
        return []
    return x[1:-1].split(sep)

def flatten(l):
  return [item for sublist in l for item in sublist]

def set_of_strings_to_clean_string(s):
  return ("[" + str(s)[6:-3].replace("', '",",") + "]")

def load_alexa_top_n(n):
  """
  Load an array of the Alexa Top 1 N (N < 1 million), as of June 2015, sorted in
  decreasing order of popularity.
  """
  arr = []
  with open(RAW_DATA_DIR + 'top-1m.csv') as f:
    for l in f:
      domain = l.strip().split(",")[1]
      arr.append(domain)
      n -= 1
      if n <= 0:
        break
  return arr
###############################################################################

###############################################################################
# Parsing domain names
###############################################################################
def extract_domain(url):
  ex = extract(url)
  return ex.domain

def extract_tld_plus_one(url):
  ex = extract(url)
  return ex.domain + "." + ex.suffix
###############################################################################

###############################################################################
# Classes
###############################################################################
class HostingProvider:
  """
  Instances of this class represent a hosting provider, which is essentially
  just a (name, type) pair, where type identifies whether the name was resolved

   1. by rDNS (in which case name will be a typical DNS hostname like a.b.com)
   2. by looking up the Organization Name of the AS owning that IP addr (in
   which case name may be any artbirary string)

  """

  ASN = 'A'
  RDNS = 'R'
  def __init__(self, name, t):
    self.name = name
    self.t = t
  def __hash__(self):
    return (hash(self.name) ^ hash(self.t))
  def __eq__(self, other):
    return ((self.name == other.name) and (self.t == other.t))
  def __ne__(self, other):
    return ((self.name != other.name) or (self.t != other.t))

def print_hosting_provider_set(s):
  st = "(["
  for x in s:
    if x.t == HostingProvider.ASN:
      st += "{}({}),".format(x.t,x.name)
  st += "|"
  for x in s:
    if x.t == HostingProvider.RDNS:
      st += "{}({}),".format(x.t,x.name)
  st += "])"
  return st

class NotLoadedException(BaseException):
  pass
###############################################################################

###############################################################################
# Domain to organization mapping
###############################################################################
def load_domain_to_org_map():
  """
  Load mapping of each domaina to the index number of the domain organization
  that owns it, according to our domain collapsing methodology (see
  project/dataset-creation/).

  This mapping will return the same index number for
  two domains owned by the same domain organization, but otherwise the index
  numbers themselves were assigned to organizations arbitrarily.

  If the map does not have a value for a given domain, it means that we were not
  able to map this domain to an organization. In this case, we simply use the
  domain name itself to identify that "organization," as opposed to an index #
  """
  global domain_to_org
  domain_to_org = {}
  sys.stderr.write("Loading org list...\n")
  with open(DATASET_DIR + 'domain-to-org.txt') as f:
    for l in tqdm(f):
      domain,org = l.strip().split(" ")
      if domain in domain_to_org:
        print "[ERROR] domain mapped twice:",domain
        raise NotLoadedException()
      domain_to_org[domain] = int(org)
  return domain_to_org

def collapse_domain_to_org(domain):
  """
  Given a domain, return the corresponding domain organization.

  Domain organizations are represented by integers. Domains that we were not
  able to map to a corresponding organization are considered to be part of a
  single-domain organization, identified by the domain name itself rather than an
  integer.

  For example, if a.com is owned by A (say, org #1), but we do not have
  a mapping for b.com, then collapse_to_org(a.com) will return 1 and
  collapse_to_org(b.com) will return "b.com"
  """
  if not domain_to_org:
    print "[ERROR]: must run load_domain_to_org_map() before using this method"
    raise NotLoadedException()
  if domain in domain_to_org:
    return domain_to_org[domain]
  else:
    return domain

def collapse_domains_to_orgs(domains):
  """
  Return collapse_to_org(d) for all d in domains
  """
  if not domain_to_org:
    print "[ERROR]: must run load_domain_to_org_map() before using this method"
    raise
  s = set()
  for d in domains:
    if d in domain_to_org:
      s.add(domain_to_org[d])
    else:
      s.add(d)
  return s
###############################################################################

###############################################################################
# Third party hosting
###############################################################################
def load_cert_to_tph_map():
  """
  Load mapping of each certificate to the list of all third-party hosting
  providers we observed serving that certificate.

  Each provider is an instance of the HostingProvider class (above), which
  specifies whether the provider was identified via rDNS or AS number.
  """

  with open(DATASET_DIR + 'cert-to-hosts.pkl') as f:
    sys.stderr.write("Loading third party hosting services list...\n")
    cert_to_hosts = loads(f.read())
    return cert_to_hosts

def load_equiv_as_mapping():
  """
  Returns a mapping of hosting provider to an "equivalent" AS that represents
  the same entity. The choice of collapsing into ASes rather than the other way
  around (collapsing to rDNS) was arbitrary.
  """

  host_to_equiv_as = {}
  with open(DATASET_DIR + 'equiv-as.txt') as f:
    for l in f:
      equiv_as,hosts = l.strip().split("[")
      equiv_as = equiv_as.strip()
      hosts = deserialize("["+hosts)
      for host in hosts:
        host_to_equiv_as[host] = equiv_as
  return host_to_equiv_as






ca_keywords = ["360 ov server","addtrust","aetna","alphassl","apple","auscert","aws","bayerische","buypass","certigna","certinomis","certum","cisco","comodo","comtrust","crazy","cybertrust","deutsche telekom","digicert","digi-sign","dod","domeny","entrust","equifax","eseentialssl","europeanssl","gandi","geotrust","globalsign","globessl","go daddy","google","incommon","infocert","intel","intermediate certificate","kagoya","keynectis","microsoft","multicert","netlock","network solutions","positivessl","quovadis","rapidssl","register.com","secom","securetrust","servision","ssl.com","starfield","startcom","swisscom","swisssign","symantec","tc trustcenter","telesec","terena","thawte","trustsign","trustwave","usertrust","verisign","verizon","vodafone","wosign"]

def get_issuer(issuer_common_name):
    if not issuer_common_name:
      return issuer_common_name

    issuer_common_name = issuer_common_name.lower()

    for a in ca_keywords:
        if(a in issuer_common_name):
            return a
    return issuer_common_name
