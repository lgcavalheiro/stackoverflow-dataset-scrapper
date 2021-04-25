SCRAPPER = scrapper.py
PROF = scrapper.prof
OPTS = --page-limit=32 --save-csv --page-size=100

no-opts-run:
	python3 $(SCRAPPER)

run:
	python3 $(SCRAPPER) $(OPTS)

profile:
	python3 -m cProfile -o $(PROF) $(SCRAPPER) $(OPTS)

view_profile:
	snakeviz $(PROF)