# Workflow

The `welleng` plugin ships a workflow layer for rigorous engineering work, adapted from pstack, see [ADR 0020](../adr/0020-workflow-layer-adapted-from-pstack.md).
It is one entry skill, 17 playbooks, 24 principles, a set of standalone skills and two subagents.

## Start

Type `/welleng:mode` followed by your task:

```
/welleng:mode the scroll position drifts after every save. Reproduce it first, then fix it.
```

The first reply opens with a `Goal:` line and a `Playbook:` line.
The agent then reads that playbook and follows its steps, such as reproduce, find the root cause, fix and verify for a bug.
The skill stays active for the rest of the conversation until it is compacted.

## Standalone skills

Every skill is typed by you, so none of them costs context until it is used.
The mode skill runs them for you when a playbook step needs one.

| Skill | Use it when |
|---|---|
| `/welleng:architect` | You want the types and module shape settled before code |
| `/welleng:arena` | You want several attempts at one task and the best parts of each |
| `/welleng:swarm` | You want parallel workers over slices of a job and one report |
| `/welleng:interrogate` | You want several models to try to break a change, keeping only proven findings |
| `/welleng:blast-radius` | You want to know what a small change could break elsewhere |
| `/welleng:tdd` | You fix a bug with a cheap test path, test first |
| `/welleng:how`, `/welleng:why`, `/welleng:teach` | You want to understand code, its history, or both |
| `/welleng:correct` | Agents keep making the same mistake and you want it made impossible |
| `/welleng:reflect` | A long task taught something worth adding to a skill |
| `/welleng:write` | You want prose cleaned up to the house style |
| `/welleng:benchmark-checklist` | You measured a number and want it vetted |
| `/welleng:show-me-your-work` | You want a decision log for long or unattended work |
| `/welleng:no-comments` | You want comments stripped before review |
| `/welleng:figure-it-out` | No playbook fits the task |
| `/welleng:verify-setup`, `/welleng:verify-maintain` | A project needs a scripted way to prove behavior, or its map is stale |
| `/welleng:ketchup`, `/welleng:bro`, `/welleng:sharpen`, `/welleng:in-your-own-words` | You want a catch-up, a plain restatement, a deeper prompt or a playback of your goal |

## Subagents and roles

Delegates run as the `welleng:worker` subagent, which carries the safety and writing rules.
Each role has a default model and effort level, such as `opus` at `xhigh` for code.
To change one, create `~/.config/welleng/roles.md` with lines such as `code: opus high`.

## Per project

`/harness` asks whether to use the workflow in a project, and whether to keep a rules table that pairs each rule with what enforces it.
`welleng harness check` prints a note when a project has no verification skill.

## Keeping up with upstream

`python3 -I scripts/pstack-upstream-diff.py` lists the upstream pstack files that changed since the adapted commit, each with its local counterpart.

## Verification status

The mode skill, its playbook header and the worker subagent ran headless on Claude Code 2.1.328 on Arch.
The other skills and playbooks pass the structural lint but were not run live, see [CHECKLIST.md](../../CHECKLIST.md).
