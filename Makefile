.PHONY: cog

cog: .travis.yml
	cog.py -r .travis.yml
