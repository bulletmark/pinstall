NAME = $(shell basename $(CURDIR))
PYNAME = $(subst -,_,$(NAME))

check:
	ruff .
	flake8 .
	mypy .
	pyright .
	vermin -v --exclude tomllib --no-tips -i */*.py */*/*.py

upload: build
	twine3 upload dist/*

build:
	rm -rf dist
	python3 -m build

doc:
	update-readme-usage -a

clean:
	@rm -vrf *.egg-info build/ dist/ __pycache__/ \
	    */__pycache__ */*/__pycache__
