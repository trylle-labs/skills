# Inline pull request reviews

Use this workflow when an automation needs to submit native comments anchored to changed lines,
or manage the resulting comment conversations.

## Inspect the pull request

Read the pull request, its diff, and current status before preparing comments:

```bash
try pr view NUMBER -R OWNER/NAME --json
try pr diff NUMBER -R OWNER/NAME --json
try pr status NUMBER -R OWNER/NAME --json
try pr review --help
```

Use the current `headSha` from `try pr view` as the review commit. Re-read the pull request if the
head branch changes while the review is being prepared.

## Prepare inline comments

Create a JSON array with one object per comment:

```json
[
  {
    "path": "src/lib.rs",
    "line": 42,
    "side": "RIGHT",
    "body": "Return this error instead of swallowing it."
  }
]
```

Each object must contain only:

- `path`: repository-relative file path.
- `line`: positive line number on the selected side of the diff.
- `side`: `RIGHT` for the new file or `LEFT` for the old file.
- `body`: non-empty comment text.

## Submit the review

Submit the comments atomically with one review decision and the exact PR head commit SHA:

```bash
try pr review NUMBER -R OWNER/NAME \
  --request-changes \
  --body "Inline findings" \
  --commit-id "$PR_HEAD_SHA" \
  --comments-file review-comments.json \
  --json
```

Exactly one of `--approve`, `--request-changes`, or `--comment` is required. `--commit-id` is
required whenever `--comments` or `--comments-file` is present; omitting it is an error.

Use `--comments` for an inline JSON value or `--comments-file -` to read the array from stdin.
`--body-file -` and `--comments-file -` cannot both consume stdin in the same command.

After submission, re-read the pull request and its inline comments:

```bash
try pr view NUMBER -R OWNER/NAME --json
try pr review-comments NUMBER -R OWNER/NAME --json
```

## Resolve or reopen conversations

Inspect the comments and the leaf command help before changing a conversation:

```bash
try pr review-comments NUMBER -R OWNER/NAME --json
try pr review-comments NUMBER resolve --help
try pr review-comments NUMBER unresolve --help
```

Then resolve or reopen the exact comment ID:

```bash
try pr review-comments NUMBER -R OWNER/NAME --json resolve COMMENT_ID
try pr review-comments NUMBER -R OWNER/NAME --json unresolve COMMENT_ID
```

Re-list the comments after either mutation to verify the conversation state.
