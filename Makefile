NAME = $(shell basename $(CURDIR))
PYNAME = $(subst -,_,$(NAME))

all:
	@echo "Type sudo make install|uninstall"
	@echo "or make sdist|upload|check|clean"

install:
	pip3 install -U --root-user-action=ignore .
	make clean

uninstall:
	pip3 uninstall --root-user-action=ignore $(NAME)

sdist:
	rm -rf dist
	python3 setup.py sdist bdist_wheel

upload: sdist
	twine3 upload --skip-existing dist/*

check:
	ruff .
	vermin --no-tips -i $(PYNAME)/*.py $(PYNAME)/*/*.py setup.py
	python3 setup.py check

doc:
	update-readme-usage -a

clean:
	@rm -vrf *.egg-info build/ dist/ __pycache__/ \
	    */__pycache__ */*/__pycache__
