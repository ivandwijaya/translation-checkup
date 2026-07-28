PORT ?= 8766

serve:
	@PORT=$(PORT) python3 serve.py
