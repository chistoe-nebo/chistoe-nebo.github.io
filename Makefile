REMOTE=magazin.chistoe-nebo.org

all: build

serve:
	python poole.py --serve --port 8080

clean:
	find . -name "*.pyc" -delete

build:
	test -d output || mkdir output
	test -d ~/.cache/thumbnails || mkdir -p ~/.cache/thumbnails
	python -u poole.py --build | tee build.log
	find css.d -type f | sort | xargs cat | csstidy - --silent=true --template=highest --merge_selectors=0 output/assets/screen.css
	find js.d/leaflet.js -type f | sort | xargs cat > output/assets/leaflet.js
	grep -E '^(error|warning)' build.log || true
	cp input/.htaccess output/

deploy: clean build
	rsync -e ssh -avz -c --delete -h output/ $(REMOTE):nebo-welcome/

deploy-dev: clean build
	-hg push
	ssh nebo_welcome@doh.umonkey.net ./refresh

push-docs:
	hg addremove doc
	hg commit README.md TODO doc -m "Обновление документации"
	hg push

shell:
	ssh -t $(REMOTE) 'cd nebo-welcome; bash -i'

strip-images:
	for fn in `find input -name "*.jpg"`; do convert $$fn -strip tmp.jpg; mv -f tmp.jpg $$fn; done
