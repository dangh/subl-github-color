all: install build

install:; pipenv install

dev:; pipenv run dev

build:; pipenv run build

clean:; pipenv run clean

.PHONY: all build clean
