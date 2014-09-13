all: build

serve:
	python poole.py --serve --port 8080

clean:
	rm -rf output/* 2>/dev/null
	find . -name "*.pyc" -delete

build: clean
	test -d output || mkdir output
	test -d ~/.cache/thumbnails || mkdir -p ~/.cache/thumbnails
	python -u poole.py --build | tee build.log
	grep -E '^(error|warning)' build.log || true
