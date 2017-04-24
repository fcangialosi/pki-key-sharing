OUTFILES = \
	certs-per-org.txt \
	orgs-per-cert.txt \
	hosts-per-cert.txt \
	3ph-by-company.txt \
	3ph-by-domain.txt \
	3ph-by-top-company.txt \
	orgs-per-host.txt \
	top-1k-compromise.tsv \
	top-1m-compromise.tsv \
	top-all-compromise.tsv 

all: $(addprefix out/, $(OUTFILES))

out/certs-per-org.txt: 2-certs-per-org.py
	cut -f1,6 ../data/raw/results-certs-no-ca-041915.tsv | python 2-certs-per-org.py > out/certs-per-org.txt

out/orgs-per-cert.txt: 3-orgs-per-cert.py
	cut -f1,6 ../data/raw/results-certs-no-ca-041915.tsv | python 3-orgs-per-cert.py > out/orgs-per-cert.txt

out/hosts-per-cert.txt: 4-hosts-per-cert.py
	cut -f1,6 ../data/raw/results-certs-no-ca-041915.tsv | python 4-hosts-per-cert.py > out/hosts-per-cert.txt

out/3ph-by-company.txt out/3ph-by-domain.txt out/3ph-by-top-company.txt: 5-num-3ph-used.py 
	cut -f1,6 ../data/raw/results-certs-no-ca-041915.tsv | python 5-num-3ph-used.py

out/orgs-per-host.txt: 7-trust-agg.py
	cut -f1,6,25 ../data/raw/results-certs-no-ca-041915.tsv | python 7-trust-agg.py 

out/top-1k-compromise.tsv out/top-1m-compromise.tsv out/top-all-compromise.tsv: 8-frac-compromise.py
	cut -f1,6 ../data/raw/results-certs-no-ca-041915.tsv | python 8-frac-compromise.py

clean:
	rm out/*.txt
