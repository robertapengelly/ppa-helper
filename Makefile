all: ppa-helper

clean:
	rm -rf ppa-helper
	find . -name "*.pyc" -delete
	find . -name "*.class" -delete

PREFIX		?=	/usr/local
BINDIR		?=	$(PREFIX)/bin
PYTHON		?=	/usr/bin/env python

install: ppa-helper
	install -d $(DESTDIR)$(BINDIR)
	install -m 755 bin/ppa-helper $(DESTDIR)$(BINDIR)

tar: ppa-helper.tar.gz

ppa-helper: ppa_helper/*.py
	mkdir -p zip
	for d in ppa_helper ; do \
		mkdir -p zip/$$d ;\
		cp -pPR $$d/*.py zip/$$d/ ;\
	done
	touch -t 200001010101 zip/ppa_helper/*.py
	cp __main__.py zip/
	cd zip ; zip -q ../ppa-helper ppa_helper/*.py __main__.py
	rm -rf zip
	echo '#!$(PYTHON)' > ppa-helper
	cat ppa-helper.zip >> ppa-helper
	rm ppa-helper.zip
	chmod a+x ppa-helper
	rm -rf bin
	mkdir bin
	mv ppa-helper bin/

ppa-helper.tar.gz: ppa-helper README.md
	@tar -czf ppa-helper-1.1.tar.gz --transform "s|^|ppa-helper/|" --owner 0 --group 0 \
		--exclude '*.DS_Store' \
		--exclude '*.kate-swp' \
		--exclude '*.pyc' \
		--exclude '*.pyo' \
		--exclude '*~' \
		--exclude '__pycache__' \
		--exclude '.git' \
		--exclude 'testdata' \
		--exclude 'docs/_build' \
		-- \
		bin ppa_helper README.md Makefile setup.py