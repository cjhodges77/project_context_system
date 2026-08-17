.PHONY: lint

# Runs the shape checks this repository specifies against its own templates, so
# the spec cannot drift from the implementation that enforces it. Consuming
# projects vendor scripts/pcs_lint.py and make it a dependency of their existing
# lint target rather than a target of its own — see "Designing a check that
# survives" in TOOLING.md.
#
# Templates are fragments, not a bundle: their links point at names no file here
# carries, and no index routes them. Resolution and coverage need a whole corpus,
# so they are exercised against synthetic bundles in --selftest instead, which
# also mutation-proves each one red. The inert-code-span check is local to a line
# and stays on — it is what keeps the templates from teaching a dead link.
lint:
	python3 scripts/pcs_lint.py --selftest
	python3 scripts/pcs_lint.py templates --no-resolve --no-coverage \
	    --index index.template.md --index domain_index.template.md
