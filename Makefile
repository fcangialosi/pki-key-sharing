all: parse plot
.PHONY: parse plot

parse:
	$(MAKE) -w -C parse/

plot:
	$(MAKE) -w -C plot/
