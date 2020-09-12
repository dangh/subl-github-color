all: install build

install:; cd build; pipenv install

dev:; cd build; pipenv run dev

build:; cd build; pipenv run build

clean:; cd build; pipenv run clean

.PHONY: all build clean
