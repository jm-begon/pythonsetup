
all: clean in test

clean:
	python setup.py clean
	rm -f .DS_Store

in: inplace

inplace:
	python setup.py build_ext --inplace

doc: inplace
	$(MAKE) -C doc html

clean-doc:
	rm -rf doc/_*

cython:
	find main -name "*.pyx" -exec cython {} \;

test:
	nosetests main -sv --with-coverage