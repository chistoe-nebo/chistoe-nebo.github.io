REMOTE_HOST=www.chistoe-nebo.info
REMOTE_FOLDER=src/output

all: build

serve:
	python poole.py --serve --port 8080

clean:
	find . -name "*.pyc" -delete

build:
	test -d ~/.cache/thumbnails || mkdir -p ~/.cache/thumbnails
	python -u poole.py --build | tee build.log
	#find css.d -type f | sort | xargs cat | csstidy - --silent=true --template=default --merge_selectors=0 output/assets/screen.css
	#find css.d -type f | sort | xargs cat > output/assets/screen.css
	find js.d/leaflet.js -type f | sort | xargs cat > tmp.js && yui-compressor -o output/assets/leaflet.js tmp.js; rm -f tmp.js
	find js.d/scripts.js -type f | sort | xargs cat > tmp.js && yui-compressor -o output/assets/scripts.js tmp.js; rm -f tmp.js
	grep -E '^(error|warning)' build.log || true
	cp input/.htaccess output/

deploy: clean build
	-hg push
	#rsync -e ssh -avz -c --delete -h output/ $(REMOTE_HOST):$(REMOTE_FOLDER)/
	ssh $(REMOTE_HOST) ./refresh

push-docs:
	hg addremove doc
	hg commit README.md TODO doc -m "Обновление документации"
	hg push

shell:
	ssh -t $(REMOTE_HOST) 'cd $(REMOTE_FOLDER); bash -i'

strip-images:
	find input -type f -name "*.jpg" -exec jpegoptim --strip-all {} \;
	find input -type f -name "*.png" -exec optipng -o7 {} \;
