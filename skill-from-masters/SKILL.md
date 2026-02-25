---
name: skill-from-masters
description: Create AI skills built on proven methodologies from domain experts. Use this when you want to create a new skill based on expert frameworks and best practices.
license: MIT
github_url: https://github.com/GBSOSS/skill-from-masters
github_hash: c4d27d29bfda00f73c23abd4990f700a6d3df480
version: 1.0.0
created_at: 2026-02-16
entry_point: SKILL.md
---

# Skill From Masters

> **Stand on the shoulders of giants** — Create AI skills built on proven methodologies from domain experts.

A skill that helps you discover and incorporate frameworks, principles, and best practices from recognized masters before generating any new skill. Works with Claude Code, Codex, and other AI agent platforms.

## Why This Skill?

**The hard part of creating a skill isn't the format — it's knowing the best way to do the thing.**

Most professional domains have masters who spent decades figuring out what works:
- Jobs on product, hiring, and marketing
- Bezos on writing (6-pager) and decision-making
- Munger on mental models
- Chris Voss on negotiation

This skill surfaces their methodologies before you write a single line, so your skill embodies world-class expertise from day one.

## How It Works

```
1. You: "I want to create a skill for user interviews"

2. Skill-from-masters:
   ├── Checks local methodology database
   ├── Searches web for additional experts
   ├── Finds golden examples of great outputs
   ├── Identifies common mistakes to avoid
   └── Cross-validates across sources

3. Surfaces experts:
   - Rob Fitzpatrick (The Mom Test)
   - Steve Portigal (Interviewing Users)
   - Nielsen Norman Group best practices

4. You select which methodologies to incorporate

5. Extracts actionable principles from primary sources

6. Hands off to skill-creator to generate the final skill
```

## Key Features

| Feature | Description |
|---------|-------------|
| **3-Layer Search** | Local database → Web search for experts → Deep dive on primary sources |
| **Golden Examples** | Finds exemplary outputs to define quality bar |
| **Anti-Patterns** | Searches for common mistakes to encode "don't do this" |
| **Cross-Validation** | Compares multiple experts to find consensus and flag disagreements |
| **Quality Checklist** | Verifies completeness before generating |

## Methodology Database

The skill includes a curated database covering 15+ domains:

| Domain | Example Experts |
|--------|-----------------|
| Writing | Barbara Minto, William Zinsser, Amazon 6-pager |
| Product | Marty Cagan, Teresa Torres, Gibson Biddle |
| Sales | Neil Rackham (SPIN), Challenger Sale, MEDDIC |
| Hiring | Laszlo Bock, Geoff Smart, Lou Adler |
| User Research | Rob Fitzpatrick, Steve Portigal, JTBD |
| Engineering | Martin Fowler, Robert Martin, Kent Beck |
| Leadership | Kim Scott, Ray Dalio, Andy Grove |
| Negotiation | Chris Voss, Fisher & Ury |
| Startups | Eric Ries, Paul Graham, YC |
| Decision Making | Jeff Bezos, Charlie Munger, Annie Duke |

Plus an **"Oral Tradition"** section for experts who share primarily through talks and interviews (Steve Jobs, Elon Musk, Jensen Huang, Patrick Collison, etc.)

## Usage

**Trigger**: When you want to create a new skill

The skill automatically activates when you ask to create a new skill. It runs **before** skill-creator to ensure your skill is built on proven methodologies.

### Example Session

**You:** "Help me create a skill for writing product requirement documents"

**Skill-from-masters:**
> Let me search for the best methodologies on PRD writing.
>
> *[Searches: "PRD best practices expert", "product requirements document methodology"]*
>
> I found several strong frameworks:
>
> **Product Management:**
> - Marty Cagan: Problem-first PRDs, separating problem space from solution space
> - Teresa Torres: Outcome-focused requirements
>
> **Business Writing:**
> - Barbara Minto: Pyramid Principle - lead with conclusion, MECE structure
> - Amazon: Working backwards, 6-pager narrative format
>
> **Golden Examples Found:**
> - Intercom's public PRD template
> - Linear's product spec format
>
> **Common Mistakes:**
> - Jumping to solutions before defining the problem
> - Writing for engineers instead of for alignment
> - Missing success metrics
>
> Which approaches resonate? Or should I search deeper into any of them?

**You:** "I like Amazon's approach combined with Cagan's problem-first thinking."

**Skill-from-masters:** *[Fetches primary sources on Amazon's methodology, extracts principles, then generates skill via skill-creator]*

## Sub-Skills

This repository contains additional skills:

| Skill | Description |
|-------|-------------|
| **search-skill** | Search for existing skills from trusted marketplaces |
| **skill-from-github** | Learn from high-quality GitHub projects and create skills based on that knowledge |

## Quality Checklist

Before finalizing any skill, this skill verifies:

- [ ] Searched beyond the local database
- [ ] Found primary sources, not just summaries
- [ ] Found golden examples of the output
- [ ] Identified common mistakes to avoid
- [ ] Cross-validated across multiple experts
- [ ] Encoded specific, actionable steps (not vague principles)

## Philosophy

**Quality isn't written. It's selected.**
