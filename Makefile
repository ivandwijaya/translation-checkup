PORT ?= 8766

serve:
	@echo "POE viewer → http://localhost:$(PORT)/"
	@python3 -m http.server $(PORT)
