.PHONY: lint

# Runs the shape checks this repository specifies against its own templates, so
# the spec cannot drift from the implementation that enforces it. Consuming
# projects vendor scripts/pcs_lint.py and make it a dependency of their existing
# lint target rather than a target of its own — see "Designing a check that
# survives" in TOOLING.md.
lint:
	python3 scripts/pcs_lint.py --selftest
	python3 scripts/pcs_lint.py templates \
	    --index index.template.md --index domain_index.template.md
