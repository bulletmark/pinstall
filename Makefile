NAME = $(shell basename $(CURDIR))
PYNAME = $(subst -,_,$(NAME))

check:
	ruff check $(NAME)/*.py $(NAME)/*/*.py
	flake8 $(NAME)/*.py $(NAME)/*/*.py
	mypy $(NAME)/*.py $(NAME)/*/*.py
	pyright $(NAME)/*.py $(NAME)/*/*.py
	vermin -vv --exclude importlib.metadata --exclude tomllib \
		--no-tips -i $(NAME)/*.py $(NAME)/*/*.py

upload: build
	twine3 upload dist/*

build:
	rm -rf dist
	python3 -m build

doc:
	update-readme-usage

clean:
	@rm -vrf *.egg-info build/ dist/ __pycache__/ \
	    */__pycache__ */*/__pycache__
