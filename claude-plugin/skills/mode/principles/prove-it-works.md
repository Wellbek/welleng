# Prove it works

Apply when you finish a task, before you call it done.

Verify every output against the real thing: run the feature, read the actual value, inspect the diff.
Proxies such as file times, self-reports, cached output or "it compiles" do not count.
When a check fails, suspect the observation method before the system.

Script the check when you can, because a rerunnable check beats a one-time look.

Say where it ran.
Label a result with its platform and evidence tag, such as `[verified: Arch]` or "tested in container", and never claim a platform where it did not run.
