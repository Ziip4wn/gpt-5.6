.PHONY: install demo test eval clean

install:
	python -m pip install -e .

demo:
	python -m gpt_harness ask "Calcule 12 * (3 + 2)"

test:
	python -m unittest discover -s tests -v

eval:
	python -m gpt_harness eval scenarios/demo.json

clean:
	python -c "from pathlib import Path; import shutil; [shutil.rmtree(p) for p in Path('.').rglob('__pycache__')]"

