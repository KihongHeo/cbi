TRIAL := $(shell cat options.txt | wc -l)

all:
	@echo "# inputs: $(TRIAL)"
	@mkdir -p build
	@mkdir -p share
	@cp ../jpegtran build/sanity
	@../../sampler-1.6.2/tools/extract-section .debug_site_info build/sanity > share/sanity.sites
	@rm -rf data
	../../cbiexp-0.6//bin/make-runs $(TRIAL)
	./check_and_generate.sh
clean:
	rm -rf data
	rm -f build/*
	cd analysis && make clean && rm -f *.txt *.xml && cd ..
