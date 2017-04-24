FIGURES = \
	2-certs-per-org \
	3-orgs-per-cert \
	4-hosts-per-cert \
	5-num-3ph-used \
	7-trust-agg \
	8-frac-compromise

all: $(addprefix figures/, $(addsuffix .eps, $(FIGURES)))

figures/%.eps: %.plot
	gnuplot $< > $@

clean:
	rm figures/*.eps
