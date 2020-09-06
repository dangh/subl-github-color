all: install build

install:
	@echo "Installing ${PROJECT}....."
	@pipenv install;

build:
	@echo "Building color schemes....."
	@pipenv run python build.py

dev:
	@pipenv run python build.py --dev
	@echo "Watch color schemes....."
	@fswatch color_schemes/*.yml | xargs -n1 -I{} pipenv run python build.py --dev

clean:
	@echo "Clean dev schemes....."
	@rm '$(HOME)/Library/Application Support/Sublime Text/Packages/User/GitHub-dev.sublime-color-scheme'
	@rm '$(HOME)/Library/Application Support/Sublime Text/Packages/User/OneDarkPro-dev.sublime-color-scheme'
