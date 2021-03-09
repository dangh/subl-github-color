all: install build

install:
	python3 -m pip install -r requirements.txt --user

dev:
	make build
	@echo Watching files for changes...
	fswatch *.yml | xargs -I{} python3 build.py --dev {}

build:
	@echo Generating color schemes...
	python3 build.py --dev

clean:
	@echo Clean dev color schemes...
	rm ~/Library/Application\ Support/Sublime\ Text/Packages/User/{GitHub,OneDarkPro}-dev.sublime-color-scheme

.PHONY: all build clean
