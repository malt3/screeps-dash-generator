Screeps.docset:
	rm -rf ./public
	cp -r ../screeps-docs/public ./
	python3 fixup-links.py --path public/
	cp dashing.json public/
	cd public && ~/go/bin/dashing build Screeps
	cp icon@2x.png public/Screeps.docset/icon.png
	mv public/Screeps.docset ./
Screeps.tgz: Screeps.docset
	tar --exclude='.DS_Store' -cvzf Screeps.tgz Screeps.docset
.PHONY: clean all
all: Screeps.docset Screeps.tgz
clean:
	rm -rf ./Screeps.docset ./Screeps.tgz ./public
