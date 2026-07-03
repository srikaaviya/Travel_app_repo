# Backend Resume — Honest Reality Check & Upgrade Plan

**Date:** 2026-07-02

---

## Brutal Assessment of the Backend Resume Content

**As a hiring manager screening for Backend SWE / SWE Intern roles, here's what I see in 6 seconds:**

### Problem 1: The bullets say nothing specific
Every bullet starts with "Built..." but none answer "what scale, what complexity, what trade-off did you navigate?" Examples:

- "Built a backend service for a conversational travel assistant" — built *what*? How many endpoints? What does the API contract look like? Did you handle auth? Rate limiting? Error handling? This reads like a homework description.
- "Offloaded long-running calls to Celery/Redis" — okay, you used a task queue. Every Flask tutorial teaches this. What was the actual problem? Did you handle retries? Dead letter queues? Task failure?

### Problem 2: OSS section is QA-framed, not backend-framed
"Wrote 90 unit tests" is your lead bullet. On a *backend* resume. A backend hiring manager reads that and thinks "this is a QA candidate who wandered into the wrong pile." The actual backend work you did in OSS — fixing race conditions in Submitty, fixing core logic in MoinMoin, dependency resolution in Poetry — is buried or one-lined.

### Problem 3: AI Support Triage Agent is not a backend project
RAG + ChromaDB + prompt engineering = AI/ML project. A backend hiring manager sees zero backend engineering here. No API design, no database schema, no request handling, no deployment. The hackathon ranking is impressive but it proves AI chops, not backend chops.

### Problem 4: Skills section has credibility problems
- **Django** — you have zero Django projects. First question in an interview: "Show me something you built in Django." You can't.
- **"AWS Fundamentals"** — this is "I watched a tutorial." Either you deployed something on AWS or don't list it.

### Problem 5: System Engineer role is vague
"Building and maintaining the company website" — what stack? PHP? WordPress? Custom Python? "Inventory tracking system" — was this a spreadsheet or a database-backed application? Without tech specifics, this reads like IT support, not engineering.

### Problem 6: No numbers, no scale, no "so what?"
Not a single bullet has a concrete metric. How many API endpoints? How many records in the DB? What response time? How many concurrent users? Even for personal projects, you can say "handles N requests/sec" or "processes N documents."

---

## What's actually strong (that the resume undersells)

1. **pytestgen-ai is genuinely good for backend** — AST parsing, CLI architecture, async concurrency, PyPI publishing, FastAPI endpoint. This is real software engineering. But the bullets make it sound like a testing tool instead of an engineering achievement.

2. **Smart Travel Assistant has real backend patterns** — Celery, PostgreSQL, Docker, API integration. But the bullets describe it like a hackathon demo, not a system.

3. **OSS bug fixes** — fixing a race condition in a production codebase (Submitty) is harder than most entry-level candidates' entire portfolio. This should be front and center for backend, not hidden behind "90 tests."

4. **14 merged PRs in real projects** — OpenTelemetry is a CNCF project. Poetry is critical Python infrastructure. This is legitimately strong. The resume treats it like a footnote.

---

## What's missing for Backend/SWE roles in 2026

| What hiring managers want | What your resume shows |
|---|---|
| API design — REST or GraphQL, versioning, error contracts | "Built a backend service" (vague) |
| Database work — schema design, migrations, query optimization | "PostgreSQL" listed in skills, no proof |
| System design thinking — why Celery? Why not background threads? | No architectural reasoning shown |
| Deployment — actual cloud deploys, not "Docker" as a skill | Nothing deployed to a live URL |
| Concurrency / async — real async patterns | One mention of asyncio.gather |
| Authentication / authorization | Zero mention |
| Monitoring / observability | You contribute to OpenTelemetry but don't use it in your own projects |

---

## System Engineer Role — Tech Stack Confirmed

PHPMyAdmin means **PHP + MySQL** stack. The bullet can now say:
> Built and maintained a company website on PHP/MySQL (administered via phpMyAdmin), managing inventory data for tools and instruments across release cycles

---

## The truth about entry-level backend hiring

No entry-level candidate — zero — has production auth, rate limiting, observability, deployment pipelines, AND database optimization on personal projects. The people who have those things have **jobs already**. That's where you learn them. Hiring managers at entry-level know this. They're looking for:

- Can this person write working code? **Yes — PyPI-published tools, OSS merges prove it.**
- Can they work with APIs and databases? **Yes — FastAPI, Flask, PostgreSQL across projects.**
- Can they navigate an unfamiliar codebase? **Yes — 14 merged PRs across 4 codebases you didn't write.**
- Will they survive code review? **Yes — maintainer-reviewed OSS contributions.**

That's the bar for entry-level. You clear it.

---

## Final Upgrade Plan — No More Moving Goalposts

### Must-do (2 items only, then resume ships):

1. **Add JWT auth to Smart Travel Assistant** — not because the resume is incomplete without it, but because "I've implemented authentication" is genuinely the single most asked-about thing in backend interviews. You'll need it for interviews anyway, so build it now and put it on the resume.

2. **Deploy Smart Travel Assistant to Railway/Fly.io** — a live URL turns "I built this" into "here, try it." Takes 30 minutes once the app works locally. Free tier.

### Nice-to-have (only if time permits):

3. **Add OpenTelemetry tracing to pytestgen-ai** — you contribute to OpenTelemetry's codebase AND use it in your own tool. That's a closed loop no other entry-level candidate has.

**How OTel tracing works:**

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

# Setup once at app start
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("pytestgen-ai")

# Then wrap your existing functions
@tracer.start_as_current_span("parse_source_file")
def parse_source_file(filepath):
    # your existing AST parsing code
    span = trace.get_current_span()
    span.set_attribute("file.path", filepath)
    span.set_attribute("functions.found", len(functions))
    ...
```

What this gives you:
- Every API request produces a trace showing: file parsed → functions found → concurrent LLM calls → tests generated → response returned
- Each step has timing, so you can see "LLM calls took 3.2s, AST parsing took 0.01s"
- Errors get captured with full context automatically

The packages:
```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi
```

The FastAPI one auto-instruments all endpoints with zero code — it just wraps the app. Then manually add spans to the interesting parts (AST parsing, LLM calls). ~30-50 lines of code total.

---

## Resume Rules for Next Session

When the upgrades are done and we rebuild the resume:
- Use only skills from actual projects — no Django, no "AWS Fundamentals"
- OSS bullets reframed for backend (lead with bug fixes, not tests)
- System Engineer role uses PHP/MySQL/phpMyAdmin
- Real numbers in every bullet
- No invented gaps or new requirements — we ship what exists
