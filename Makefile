.PHONY: setup test run demo eval lint

setup:
	python tasks.py setup

test:
	python tasks.py test

run:
	python tasks.py run

demo:
	python tasks.py demo

eval:
	python tasks.py eval

lint:
	python tasks.py lint
