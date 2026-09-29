# Pull Requests And Commit Messages

Use this file for commit messages and pull request titles and bodies. The PR
body becomes the squash-merge commit message, so the two media use the same
voice: neutral, compact, and useful in `git log`.

## Write The Title

- Use an imperative sentence of at most 72 characters.
- Name the outcome, not the activity or implementation inventory.
- Use an optional `[scope]` prefix. Do not add `feat:`, `fix:`, or another
  conventional-commit prefix.
- Remove adjectives, authoring-tool or agent-provider names, emoji, and trailing
  punctuation.

Prefer `Reject malformed boxed answers` over
`feat(math): add robust boxed-answer parsing support`.

## Write The Body

- Treat the body as a permanent changelog entry. It must make sense to a
  competent reader who was not part of the authoring session and may encounter
  it months later. This follows the Linux kernel's guidance for
  [describing changes](https://docs.kernel.org/process/submitting-patches.html#describe-your-changes).
- Use as many words as the review-relevant information needs and no more. Most
  bodies are a few plain paragraphs with no headings; benchmarks, reproduction
  details, or compatibility constraints may justify more.
- Lead with the behavior that changes. Follow with the reason or constraint that
  shaped it.
- Keep concrete symptoms, measured results, baselines, and caveats when they
  explain the change or affect the review decision. State them once and link
  detailed evidence when the full record belongs elsewhere.
- End with `Fixes #NNNN` or `Part of #NNNN` when applicable.
- Put extended raw benchmark output and research history in an issue or source
  artifact and link it. Keep the reproduction detail and result summary
  needed to evaluate the change.

The body must stand alone, but it does not need to reproduce the diff. Delete:

- file-by-file or symbol-by-symbol inventories visible in the diff;
- lists of tests and assertions;
- `Testing`, `Validation`, `Verification`, `What`, `Changes`, or `Summary`
  scaffolds;
- claims framed as verdicts, such as `why this is correct`, `cleaner`, or
  `provably`, when a measured result or explicit technical choice says more;
- boldface, all-caps emphasis, checkboxes, emoji, and attribution or session
  trailers;
- filler openers such as `This PR`, `In this change`, or `Summary of changes`.

Use a list, table, or diagram only when it conveys steps, data, or a relationship
that is hard to express in prose. Do not add section headings to a normal PR
body. Markdown is not a completeness signal.

## Compress an implementation report

Keep the trigger, resulting behavior, and any relevant constraint:

```text
Title: Reject malformed boxed answers

Score an answer as zero when its last boxed marker is empty or has unbalanced
braces. Previously, extraction could fall back to an earlier correct answer,
accepting a malformed final response.
```

The diff shows helper names and test cases. Linked artifacts can hold longer
reproduction details.

## Check The Exact Payload

Before committing or calling `gh pr create` or `gh pr edit`:

1. Read the exact title and body that the command will receive, not the notes
   used to draft them.
2. Count the title characters. Inspect the body length as a signal, not a gate:
   shorten text that narrates the diff, but retain evidence and caveats a future
   reader needs.
3. Apply [ai-writing-donts.md](ai-writing-donts.md). Delete every sentence that
   does not add behavior, motivation, evidence, a caveat, or an issue link.
4. Check that the title, opening sentence, and issue link agree with the actual
   branch scope.
5. After creating or editing the PR, fetch the published text with
   `gh pr view --json title,body` and correct any text added or altered by the
   publishing tool.

Use `printf %s '<title>' | wc -m` for the title. Inspect the body file itself
after drafting it.
