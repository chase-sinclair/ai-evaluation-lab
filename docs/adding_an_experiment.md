# Adding an experiment

Create `experiments/<id>/experiment.yaml` and `experiment.py`. Config must satisfy
`ExperimentSpec` in `src/eval_lab/contracts.py`. The directory name must match the ID.
No central registry or runner edit is necessary; the CLI discovers the YAML file.
Experiment code is trusted executable Python, not untrusted downloaded configuration.

Export a small `Experiment` class with this interface:

```python
class Experiment:
    def __init__(self, spec, directory):
        self.spec, self.directory = spec, directory

    def load_cases(self):
        # Return list[TestCase]; IDs and dataset versions must match the config.
        ...

    def validate(self, cases):
        # Raise on invalid labels, schemas, controls, or grader versions.
        ...

    def build_request(self, case, condition):
        # Return ModelRequest; never copy ground truth into model inputs.
        ...

    def grade(self, case, response, *, request):
        # Return GradeResult, using a fixed deterministic grading rule.
        ...
```

Copy the tool-selection config as a starting point, but replace the research question,
dataset, conditions, and grader identifiers. Keep fixture and grading logic local.
Use relative imports (`from .grader import grade`) for neighboring files. Dataset paths
are experiment-relative. Any new loader must validate paths, provenance, versions, labels,
and splits. The runner adds generic ID/version checks and constructs all requests before
execution. Pure `build_request` functions make hashes reproducible.

Add adversarial grader tests and a tiny provider double for end-to-end checks. The
`test_second_experiment_without_runner_changes` test demonstrates text-output grading
using the same engine. The stock mock intentionally understands only the authored
tool-selection prompts; it is not a universal simulator. Multi-step execution is deferred.

For experiments outside the checkout, use `--experiments <directory>`. The installed
package supplies the engine; experiment modules/config/data remain in the checkout.
