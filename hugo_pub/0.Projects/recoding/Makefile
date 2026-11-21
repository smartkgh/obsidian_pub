# recoding — 개발 태스크 (canonical: `make test`)
PY := .venv/bin/python

.PHONY: test lint doctor compare once clean

test:            ## 테스트 (stdlib unittest)
	$(PY) run_tests.py

lint:            ## 구문 검사 (py_compile)
	$(PY) -m compileall -q core adapters tools main.py run_tests.py tests

doctor:          ## 환경 점검
	$(PY) main.py doctor

compare:         ## 엔진 A/B 비교 (apple vs whisper)
	$(PY) tools/compare_engines.py

once:            ## 신규 녹음 처리
	$(PY) main.py once
