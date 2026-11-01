# Attack run — before

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-01 16:43
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `d638979f-f763-40ee-b48d-db3bc8c43c8a` | human | 0.817 || **BROKE** |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `382cbdaa-9757-4b48-8d95-9b03f6c00799` | human | 0.685 || **BROKE** |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `1df8bb55-1e13-4861-9914-ca52b3de6165` | unsure | 0.534 || **BROKE** |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `ba7fc32a-7033-4392-ba72-b4df3b085358` | unsure | 0.617 || **BROKE** |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `3395f97b-f9d0-43eb-b823-aa15bbd34724` | human | 0.665 || **BROKE** |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `901717dd-f508-41bd-8119-27dec2de267c` | unsure | 0.573 || **BROKE** |
| EV07 | evasion | signal two: padding with punctuation | 200 | `87701fdb-2c57-4f91-bf83-d65a1bea68fe` | unsure | 0.627 || **BROKE** |
| EV08 | evasion | signal one: text below the token window | 200 | `00dee3fe-91f9-40fd-b3c7-5032f34b859b` | human | 0.692 || **BROKE** |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `e1997250-54d6-4a78-abb0-856f6908ce17` | unsure | 0.505 || **BROKE** |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `0268eebb-7743-4027-9223-ffa5fd0487d0` | ai | 0.705 || **HELD** |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `0ccda09a-c9de-493a-b6b9-b2205117a7fa` | unsure | 0.587 || **HELD** |
| FP02 | false_positive | human writing in a formal register | 200 | `ddc898c9-f098-496e-8a4e-2b312dcf29f1` | ai | 0.710 || **BROKE** |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `f4d6bd78-4133-433f-8d9e-6d3960eb7339` | ai | 0.685 || **BROKE** |
| FP04 | false_positive | a student essay written to a rubric | 200 | `974f0bb8-564c-4cac-a71b-6d20893da35f` | unsure | 0.625 || **HELD** |
| FP05 | false_positive | technical documentation written by a person | 200 | `c04ff633-4615-4d7f-88a8-e538b87786da` | ai | 0.719 || **BROKE** |
| FP06 | false_positive | a person imitating a formal template | 200 | `b5b6a2d2-f92a-4a17-aafb-98dc3cb247a6` | unsure | 0.584 || **HELD** |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `3af39547-d94a-408a-a623-13b74b41cee8` | unsure | 0.518 || **HELD** |
| FP08 | false_positive | very short genuine human submission | 200 | `9f95c3f6-b990-4c1b-ae47-c29d73ab9b81` | unsure | 0.622 || **HELD** |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c727a9fd-98bd-4c78-b093-2446c7300a3d` | unsure | 0.565 || **BROKE** |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `0ab9c5ff-ca6d-49b4-a9ff-05687d4f7c92` | human | 0.737 || **BROKE** |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `6144eb1f-f5d2-494c-8242-37a51a63caec` | unsure | 0.536 || **BROKE** |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `a2afcc39-72cc-4add-ada4-a9bd9720fe1d` | unsure | 0.502 || **HELD** |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c02516af-d124-4b98-9633-afb5423e516e` | unsure | 0.509 || **HELD** |
| PI06 | prompt_injection | instruction plus real human text | 200 | `712c576c-4049-4a0c-b3a2-93107466a36b` | unsure | 0.566 || **HELD** |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — || **HELD** |
| MF02 | malformed | text is a single character | 400 | `—` | — | — || **HELD** |
| MF03 | malformed | text is control characters | 200 | `b7d25fc7-586a-474f-99a2-021f93f1fca5` | human | 1.000 || **BROKE** |
| MF04 | malformed | text is only punctuation | 200 | `1fe7265f-619f-4c22-8b96-f757ec744735` | human | 0.983 || **BROKE** |
| MF05 | malformed | text is a very long single word | 200 | `8f328aa6-4d1b-4889-a57c-ab09db3dc7ec` | unsure | 0.501 || **BROKE** |
| MF06 | malformed | text is emoji only | 200 | `2d5f2c97-fd1d-4a05-a4ce-c536b7f0fd6e` | unsure | 0.501 || **BROKE** |
| MF07 | malformed | text is right-to-left script | 200 | `fb302ce1-24fa-4743-95e9-39d1d941d136` | unsure | 0.538 || **HELD** |
| MF08 | malformed | text is 60,000 characters | 200 | `4b167135-4cb3-45a4-895f-5681961a1553` | ai | 0.707 || **BROKE** |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — || **HELD** |
| RQ02 | malformed | no creator_id | 200 | `7b66cfa4-07d2-468e-b3c8-ce8e9ba1db61` | human | 0.698 || **BROKE** |
| RQ03 | malformed | text is a number | 400 | `—` | — | — || **HELD** |
| RQ04 | malformed | text is a list | 400 | `—` | — | — || **HELD** |
| RQ05 | malformed | text is null | 400 | `—` | — | — || **HELD** |
| RQ06 | malformed | creator_id is an object | 200 | `c9c95dd7-40ca-422d-9fbb-0e15577731f5` | human | 0.925 || **BROKE** |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — || **HELD** |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — || **HELD** |
| RQ09 | malformed | body is empty | 400 | `—` | — | — || **HELD** |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — || **HELD** |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | `—` | — | — || **HELD** |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — || **HELD** |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `d24ff274-75d7-4ae5-91b7-08a1309bcd0a` | human | 0.955 || **BROKE** |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `9806b102-a863-4f65-ba9c-6432dc4e1f38` | human | 0.955 || **BROKE** |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `80e03f0b-6233-452b-bd3b-485f16372068` | human | 0.955 || **BROKE** |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `270a2eef-9afe-475d-8574-d4892b096069` | human | 0.955 || **BROKE** |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `a2fe56f8-c75c-4e7d-866e-489bfada0c6f` | human | 0.955 || **BROKE** |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `3f546af3-bb75-479b-9ba2-0bf8196b3f72` | human | 0.955 || **BROKE** |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | `856fcfd2-3a4c-49d0-ba66-835e281cbc07` | human | 0.955 || **BROKE** |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c04624bd-9615-40e8-bc15-aa339c12b9cc` | human | 0.955 || **BROKE** |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | `3922dfdf-6565-43e4-a4f6-4d40e13dae6d` | human | 0.955 || **BROKE** |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | `9f026bf5-86b7-42d4-ada1-590c2dd4abad` | human | 0.955 || **BROKE** |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 200 | `6536e39d-4471-47a6-a657-f10137bb9b94` | human | 0.955 || **BROKE** |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 200 | `17027dbc-0b95-4ba1-8dcf-c42ba0d17d22` | human | 0.955 || **BROKE** |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "d638979f-f763-40ee-b48d-db3bc8c43c8a",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.8168,
  "model_score": 0.1635,
  "style_score": 0.6204,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "382cbdaa-9757-4b48-8d95-9b03f6c00799",
  "creator_id": "attacker_EV02",
  "guess": "human",
  "confidence": 0.6853,
  "model_score": 0.5943,
  "style_score": 0.2594,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "1df8bb55-1e13-4861-9914-ca52b3de6165",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.5338,
  "model_score": 0.6662,
  "style_score": 0.4039,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "ba7fc32a-7033-4392-ba72-b4df3b085358",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.6169,
  "model_score": 0.6114,
  "style_score": 0.6226,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "3395f97b-f9d0-43eb-b823-aa15bbd34724",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.6655,
  "model_score": 0.3212,
  "style_score": 0.3493,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "901717dd-f508-41bd-8119-27dec2de267c",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.5731,
  "model_score": 0.5727,
  "style_score": 0.3663,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "87701fdb-2c57-4f91-bf83-d65a1bea68fe",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.6275,
  "model_score": 0.5862,
  "style_score": 0.3107,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "00dee3fe-91f9-40fd-b3c7-5032f34b859b",
  "creator_id": "attacker_EV08",
  "guess": "human",
  "confidence": 0.6924,
  "model_score": 0.2452,
  "style_score": 0.5026,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "e1997250-54d6-4a78-abb0-856f6908ce17",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.5048,
  "model_score": 0.7042,
  "style_score": 0.4331,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "0268eebb-7743-4027-9223-ffa5fd0487d0",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.7052,
  "model_score": 0.9792,
  "style_score": 0.6491,
  "label": "We think this was probably written with help from an AI tool. Its wording and sentence patterns closely match what AI writing tools usually produce. This is an automatic estimate, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "0ccda09a-c9de-493a-b6b9-b2205117a7fa",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.5873,
  "model_score": 0.6175,
  "style_score": 0.5631,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "ddc898c9-f098-496e-8a4e-2b312dcf29f1",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.71,
  "model_score": 0.7387,
  "style_score": 0.6867,
  "label": "We think this was probably written with help from an AI tool. Its wording and sentence patterns closely match what AI writing tools usually produce. This is an automatic estimate, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "f4d6bd78-4133-433f-8d9e-6d3960eb7339",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "confidence": 0.6847,
  "model_score": 0.8051,
  "style_score": 0.6274,
  "label": "We think this was probably written with help from an AI tool. Its wording and sentence patterns closely match what AI writing tools usually produce. This is an automatic estimate, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "974f0bb8-564c-4cac-a71b-6d20893da35f",
  "creator_id": "attacker_FP04",
  "guess": "unsure",
  "confidence": 0.6246,
  "model_score": 0.8329,
  "style_score": 0.5625,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "c04ff633-4615-4d7f-88a8-e538b87786da",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.7191,
  "model_score": 0.8005,
  "style_score": 0.6712,
  "label": "We think this was probably written with help from an AI tool. Its wording and sentence patterns closely match what AI writing tools usually produce. This is an automatic estimate, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "b5b6a2d2-f92a-4a17-aafb-98dc3cb247a6",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.5844,
  "model_score": 0.8814,
  "style_score": 0.5318,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "3af39547-d94a-408a-a623-13b74b41cee8",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.518,
  "model_score": 0.8816,
  "style_score": 0.4518,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "9f95c3f6-b990-4c1b-ae47-c29d73ab9b81",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.6221,
  "model_score": 0.3223,
  "style_score": 0.489,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "c727a9fd-98bd-4c78-b093-2446c7300a3d",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.5648,
  "model_score": 0.4625,
  "style_score": 0.4129,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "0ab9c5ff-ca6d-49b4-a9ff-05687d4f7c92",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.7373,
  "model_score": 0.2044,
  "style_score": 0.3899,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "6144eb1f-f5d2-494c-8242-37a51a63caec",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.5359,
  "model_score": 0.5943,
  "style_score": 0.4966,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "a2afcc39-72cc-4add-ada4-a9bd9720fe1d",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.502,
  "model_score": 0.4998,
  "style_score": 0.5042,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "c02516af-d124-4b98-9633-afb5423e516e",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.5092,
  "model_score": 0.6401,
  "style_score": 0.4503,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "712c576c-4049-4a0c-b3a2-93107466a36b",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.5655,
  "model_score": 0.5583,
  "style_score": 0.5731,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "b7d25fc7-586a-474f-99a2-021f93f1fca5",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.9995,
  "model_score": 0.0,
  "style_score": 0.4989,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "1fe7265f-619f-4c22-8b96-f757ec744735",
  "creator_id": "attacker_MF04",
  "guess": "human",
  "confidence": 0.9833,
  "model_score": 0.0112,
  "style_score": 0.5,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "8f328aa6-4d1b-4889-a57c-ab09db3dc7ec",
  "creator_id": "attacker_MF05",
  "guess": "unsure",
  "confidence": 0.5006,
  "model_score": 0.9976,
  "style_score": 0.4996,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "2d5f2c97-fd1d-4a05-a4ce-c536b7f0fd6e",
  "creator_id": "attacker_MF06",
  "guess": "unsure",
  "confidence": 0.5015,
  "model_score": 0.9969,
  "style_score": 0.5,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "fb302ce1-24fa-4743-95e9-39d1d941d136",
  "creator_id": "attacker_MF07",
  "guess": "unsure",
  "confidence": 0.538,
  "model_score": 0.9064,
  "style_score": 0.5,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 200,
  "content_id": "4b167135-4cb3-45a4-895f-5681961a1553",
  "creator_id": "attacker_MF08",
  "guess": "ai",
  "confidence": 0.7074,
  "model_score": 0.9876,
  "style_score": 0.6522,
  "label": "We think this was probably written with help from an AI tool. Its wording and sentence patterns closely match what AI writing tools usually produce. This is an automatic estimate, not proof, and it can be wrong. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 200,
  "content_id": "7b66cfa4-07d2-468e-b3c8-ce8e9ba1db61",
  "creator_id": null,
  "guess": "human",
  "confidence": 0.698,
  "model_score": 0.2395,
  "style_score": 0.4941,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 200,
  "content_id": "c9c95dd7-40ca-422d-9fbb-0e15577731f5",
  "creator_id": {
    "id": "x"
  },
  "guess": "human",
  "confidence": 0.9247,
  "model_score": 0.0492,
  "style_score": 0.49,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "d24ff274-75d7-4ae5-91b7-08a1309bcd0a",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.9545,
  "model_score": 0.0287,
  "style_score": 0.4925,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "9806b102-a863-4f65-ba9c-6432dc4e1f38",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.9545,
  "model_score": 0.0287,
  "style_score": 0.4925,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "80e03f0b-6233-452b-bd3b-485f16372068",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.9545,
  "model_score": 0.0287,
  "style_score": 0.4925,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "270a2eef-9afe-475d-8574-d4892b096069",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.9545,
  "model_score": 0.0287,
  "style_score": 0.4925,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "a2fe56f8-c75c-4e7d-866e-489bfada0c6f",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.9545,
  "model_score": 0.0287,
  "style_score": 0.4925,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 200,
  "content_id": "3f546af3-bb75-479b-9ba2-0bf8196b3f72",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.9545,
  "model_score": 0.0287,
  "style_score": 0.4925,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 200,
  "content_id": "856fcfd2-3a4c-49d0-ba66-835e281cbc07",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.9545,
  "model_score": 0.0287,
  "style_score": 0.4925,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 200,
  "content_id": "c04624bd-9615-40e8-bc15-aa339c12b9cc",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.9545,
  "model_score": 0.0287,
  "style_score": 0.4925,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 200,
  "content_id": "3922dfdf-6565-43e4-a4f6-4d40e13dae6d",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.9545,
  "model_score": 0.0287,
  "style_score": 0.4925,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 200,
  "content_id": "9f026bf5-86b7-42d4-ada1-590c2dd4abad",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.9545,
  "model_score": 0.0287,
  "style_score": 0.4925,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 200,
  "content_id": "6536e39d-4471-47a6-a657-f10137bb9b94",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.9545,
  "model_score": 0.0287,
  "style_score": 0.4925,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 200,
  "content_id": "17027dbc-0b95-4ba1-8dcf-c42ba0d17d22",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.9545,
  "model_score": 0.0287,
  "style_score": 0.4925,
  "label": "We think this was probably written by a person. Its wording and sentence patterns vary in the way people's writing usually does.",
  "error": null,
  "verdict": ""
}
```
