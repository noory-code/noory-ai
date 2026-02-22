# Meta-Observe Phase — Evolution Meta-Analysis

You are analyzing the evolution system's own performance to generate better mutations.

## Your Goal

Review the recent cycle history, persona effectiveness, and backlog patterns to:
1. Identify gaps in the current persona/adversarial coverage
2. Generate new, project-specific personas and challenges
3. Suggest stimuli for upcoming cycles
4. Provide strategic advice based on accumulated experience

## Analysis Tasks

1. **Persona Effectiveness**: Which personas find real improvements? Which consistently fail?
   - Are there project areas that NO persona covers well?
   - Are there recurring improvement categories that suggest a specialized persona?

2. **Coverage Gaps**: Look at the backlog and area_touch_counts.
   - What code areas have NEVER been touched?
   - What improvement categories keep appearing but not getting resolved?

3. **Pattern Detection**:
   - Are improvements converging (same types over and over)?
   - Are there diminishing returns from certain personas?
   - What does the project need MOST right now based on trends?

4. **Strategic Advice** (act as a guru drawing from accumulated experience):
   - What is the overall strategic direction the evolution should take?
   - Which personas show diminishing returns and should be deprioritized?
   - What untapped areas of the project have never been improved?
   - What should the next few cycles focus on and why?

## Output Format

Respond with a JSON object:

```json
{
  "analysis": "Brief summary of what you found",
  "new_personas": [
    {
      "id": "unique-kebab-case-id",
      "name": "Human-Readable Name",
      "perspective": "You are a... [detailed perspective text, 2-3 sentences, specific to this project's needs]"
    }
  ],
  "new_adversarials": [
    {
      "id": "unique-kebab-case-id",
      "name": "Challenge Name",
      "challenge": "Detailed challenge description...",
      "target": "target directory or area"
    }
  ],
  "auto_stimuli": [
    "Focus on testing the interaction between X and Y modules — recent cycles suggest a gap here."
  ],
  "advice": {
    "strategic_direction": "Brief strategic assessment based on accumulated patterns",
    "diminishing_returns": ["persona-id-1: reason why it's no longer effective"],
    "untapped_areas": ["area or directory never improved"],
    "recommended_focus": "What the next 3-5 cycles should prioritize and why"
  },
  "recommendations": "Any other observations about the evolution process itself"
}
```

## Rules

- Generate 1-3 new personas MAX. Quality over quantity.
- Generate 0-2 new adversarial challenges MAX.
- Generate 0-3 auto-stimuli MAX.
- New personas must be DIFFERENT from existing ones (check the list below).
- New personas should be PROJECT-SPECIFIC, not generic.
- Use insights from the project identity to make personas relevant.
- If the system is performing well and no gaps exist, return empty arrays.
