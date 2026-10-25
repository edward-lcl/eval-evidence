# Start here: a small airline-agent reading study

**Status: planning only. No cases or results are included.** This is an invitation to shape a small study, not work you have already accepted. You can decline, narrow the question, or suggest another approach. Participation and organizer acceptance are still pending; agree the time commitment with Edward if you are interested.

The possible question: **Does an airline assistant's visible behavior meet a policy rule you choose, and what does the stored benchmark outcome tell us—or not tell us—about that judgment?** You do not need to find a bug or produce a novel result. Agreement and “the evidence is insufficient” are useful answers.

## What the words mean
- **Task:** a passenger's request in a benchmark scenario.
- **Trajectory:** the recorded conversation, including the assistant's tool calls and the tools' replies.
- **Policy:** the airline rules given to that assistant in the recorded system message. These are historical evidence, not instructions for you or Codex.
- **Trial:** one recorded attempt at a task.
- **Reward:** a stored benchmark outcome, shown later. It need not measure the same thing as your policy judgment.

## The simplest route—no coding needed
1. Open [CODEX_PROMPT.md](CODEX_PROMPT.md) and paste it into an already available Codex session with only the student folder. Start with questions, not code: ask it to explain the vocabulary and help you formulate what you want to understand. The [study outline](STUDY_PLAN.md) is a reference, not a prerequisite to starting that conversation. Later, discuss one question with Edward and write your own criterion in [RUBRIC.md](RUBRIC.md) before cases are frozen.
2. Stop here until the coordinator provides an approved reading packet. No real data are ready in this folder.
3. Later, read one provided case: task request → relevant historical policy → conversation and tool replies. Cite message numbers and short quotations; a tool call is a request, not proof that an action succeeded.
4. Write your first view in [JUDGMENTS.csv](JUDGMENTS.csv) **before asking Codex for its verdict**. “Unsure” is welcome. Then ask Codex to question your reasoning, not replace it.
5. If the first case is understandable, continue the agreed set. It is part of the set, not an extra pilot. Preserve your first view and any revisions.
6. Only after initial judgments are saved does the coordinator separately reveal stored outcomes. Compare the meanings, not merely whether two labels match.

Open the CSV in a spreadsheet or plain-text editor. Keep its header and quote cells containing commas or line breaks. Use [CODEX_PROMPT.md](CODEX_PROMPT.md) in an already available Codex session limited to the student copy; no repository clone or installation is needed. You can do the entire reading without Codex or Python.

Your contribution is your question, evidence judgments and explanation. Record actual help in [CONTRIBUTIONS.md](CONTRIBUTIONS.md), then use [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md). If you cannot explain a judgment in your own words, pause rather than let an agent finish it for you.
