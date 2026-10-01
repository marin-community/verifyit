# Framework integration artifacts

verifyit provides grading modes and reusable clients. Installing the package
does not deploy changes to SkyRL, Harbor, Evalchemy or lm-eval-harness.
Each framework must opt in and supply its runtime dependencies and task assets.

Source inventories, coverage reports, exported patches and replay receipts are
campaign artifacts outside the package. In the local `verifier-unification`
campaign checkout, `artifacts/reports/docs/unification/` retains the full
coverage report and source mappings; `artifacts/reports/tools/unification/`
retains their generators. Framework patch bundles live under `artifacts/`.
The move manifests record original paths and SHA256 hashes. Raw execution
receipts remain under the campaign's `evidence/` directory.

The artifacts are available in the local campaign checkout. Public downloads
are not configured; request the bundle to reproduce its source comparisons. Package tests
cover the maintained grading APIs; historical campaign counts do not establish
validation of later client changes or complete dataset execution.
