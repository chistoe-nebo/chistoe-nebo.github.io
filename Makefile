REMOTE_HOST=www.chistoe-nebo.info
REMOTE_FOLDER=src/output

all: build

serve:
	python poole.py --serve --port 8080

clean:
	find . -name "*.pyc" -delete

build: assets
	test -d ~/.cache/thumbnails || mkdir -p ~/.cache/thumbnails
	python -u poole.py --build | tee build.log
	grep -E '^(error|warning)' build.log || true
	cp input/.htaccess output/
	find output -type f -exec chmod 664 {} \;

assets:
	@echo "compiling /scripts.js ..."
	@cat `find js.d -type f -name '*.js' | sort` > input/scripts.js
	@echo "compiling /styles.css ..."
	@cat `find css.d -type f -name '*.css' | sort` > input/styles.css


deploy:
	hg push || true
	ssh static.umonkey.net ./bin/rebuild.sh chistoe-nebo.info

push-docs:
	hg addremove doc
	hg commit README.md TODO doc -m "Обновление документации"
	hg push

shell:
	ssh -t $(REMOTE_HOST) 'cd $(REMOTE_FOLDER); bash -i'

strip-images:
	find input -type f -name "*.jpg" -exec jpegoptim --strip-all {} \;
	find input -type f -name "*.png" -exec optipng -o7 {} \;

.PHONY: assets
