# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-04 19:48
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
| EV01 | evasion | signal two: typos raise word variety | 200 | `5889f74f-bca6-4235-8ae9-32ee6616c108` | human | 0.817 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `4746510d-dc53-49c4-9378-6ca97dc5f0aa` | human | 0.685 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `f9057057-a88c-41ae-a81d-e2d6dc7ae424` | unsure | 0.534 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `b3c7403d-ee66-4b5f-a67a-4cb0d7d66511` | unsure | 0.617 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `50c93660-9042-4f9f-b3bb-11a675c3e691` | human | 0.665 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `5e9cc7f8-368c-4a44-89d8-516b59494816` | unsure | 0.573 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `4d29cf4d-415c-488e-9515-71b37ff39f4d` | unsure | 0.627 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `ee606bea-2dde-45b0-b978-f9edd55090fa` | human | 0.692 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `9f209319-b166-4ffa-b57d-47d4c96a3899` | unsure | 0.505 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `db7ad3b9-fc57-4259-87c3-fb52861cab44` | unsure | 0.705 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `5560a9a5-03e5-4284-8261-3204201d0b5c` | unsure | 0.587 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `b978eeb6-0932-4dab-a71d-6385a4564db1` | unsure | 0.710 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `b485df78-c0a9-4e1f-bc6a-60961ad3e68e` | unsure | 0.685 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `e81ed042-cb9f-459a-bbce-37d380e351ea` | unsure | 0.625 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `0708653e-69df-4d30-999a-79e38817acfa` | unsure | 0.719 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `44ca535f-752f-4e28-81b9-240c6f44675c` | unsure | 0.584 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `0ce29f96-e98e-45fc-b929-0d96c47eef4d` | unsure | 0.518 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `2c88019a-d4e9-4f54-861c-b559b914f8bc` | unsure | 0.622 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `6a3e1f68-2d8c-4e07-be2c-cc4be768e998` | unsure | 0.565 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `2beabbf6-affe-4a6e-8533-dd664ba485fe` | human | 0.737 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `8f2891e7-591b-49f8-ab52-463a74ee0f46` | unsure | 0.536 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `eacd3c28-72e8-4467-b230-8831893ec504` | unsure | 0.502 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `de2e7f7e-4864-4a1b-842d-2847b288d1f4` | unsure | 0.509 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `2488d78e-0814-4a40-af3d-07fb6a7348df` | unsure | 0.566 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 400 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 200 | `4f2ed37b-cfde-4e3d-8767-b8416b8474d1` | human | 1.000 |  |
| MF04 | malformed | text is only punctuation | 200 | `0cab5c82-3511-4d0b-b70d-165fd6768103` | human | 0.983 |  |
| MF05 | malformed | text is a very long single word | 200 | `5c5714c4-93da-4b26-b42d-6414476d3d84` | unsure | 0.501 |  |
| MF06 | malformed | text is emoji only | 200 | `84354b1b-9943-48c0-b238-4b9a55c15446` | unsure | 0.501 |  |
| MF07 | malformed | text is right-to-left script | 200 | `498a5114-a198-404f-a013-165332c4ff14` | unsure | 0.538 |  |
| MF08 | malformed | text is 60,000 characters | 200 | `34dd146c-6fbc-4477-93e6-041a02af845a` | unsure | 0.707 |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 200 | `0a65a30e-6e07-4cfd-af16-3a3d32240dbb` | human | 0.698 |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 200 | `660bd357-7ea7-4ad6-ae61-652de1326ec1` | human | 0.925 |  |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — |  |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `0c966497-4942-496f-9283-0652b18165a6` | human | 0.955 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `115776e8-567d-4112-ad50-25511295b4f1` | human | 0.955 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `09c52a51-fbae-442f-a72f-7cb419274d8b` | human | 0.955 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `42dca357-bee5-46b1-a1d7-d577212ab6fb` | human | 0.955 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `9bb8307f-43b4-406e-a8a5-0bc5b785fa90` | human | 0.955 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `91e023fd-2033-4185-bce8-43238678fb92` | human | 0.955 |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | `8db80191-d8b6-460f-b845-d0b6424b4665` | human | 0.955 |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | `1a4374f7-fb8b-4f3b-a6e9-0cffaccd4851` | human | 0.955 |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | `db4791ed-0ae6-4a86-aa0f-4c0b5fe04c64` | human | 0.955 |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | `a97a4413-90d5-4ec5-b390-cc043299ccd5` | human | 0.955 |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 200 | `db23d371-b118-4932-99aa-93f981b9f2cb` | human | 0.955 |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 200 | `b9eac451-8019-410a-8ab1-9e3a1b7e19c8` | human | 0.955 |  |

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
  "content_id": "5889f74f-bca6-4235-8ae9-32ee6616c108",
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
  "content_id": "4746510d-dc53-49c4-9378-6ca97dc5f0aa",
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
  "content_id": "f9057057-a88c-41ae-a81d-e2d6dc7ae424",
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
  "content_id": "b3c7403d-ee66-4b5f-a67a-4cb0d7d66511",
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
  "content_id": "50c93660-9042-4f9f-b3bb-11a675c3e691",
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
  "content_id": "5e9cc7f8-368c-4a44-89d8-516b59494816",
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
  "content_id": "4d29cf4d-415c-488e-9515-71b37ff39f4d",
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
  "content_id": "ee606bea-2dde-45b0-b978-f9edd55090fa",
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
  "content_id": "9f209319-b166-4ffa-b57d-47d4c96a3899",
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
  "content_id": "db7ad3b9-fc57-4259-87c3-fb52861cab44",
  "creator_id": "attacker_EV10",
  "guess": "unsure",
  "confidence": 0.7052,
  "model_score": 0.9792,
  "style_score": 0.6491,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
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
  "content_id": "5560a9a5-03e5-4284-8261-3204201d0b5c",
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
  "content_id": "b978eeb6-0932-4dab-a71d-6385a4564db1",
  "creator_id": "attacker_FP02",
  "guess": "unsure",
  "confidence": 0.71,
  "model_score": 0.7387,
  "style_score": 0.6867,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
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
  "content_id": "b485df78-c0a9-4e1f-bc6a-60961ad3e68e",
  "creator_id": "attacker_FP03",
  "guess": "unsure",
  "confidence": 0.6847,
  "model_score": 0.8051,
  "style_score": 0.6274,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
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
  "content_id": "e81ed042-cb9f-459a-bbce-37d380e351ea",
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
  "content_id": "0708653e-69df-4d30-999a-79e38817acfa",
  "creator_id": "attacker_FP05",
  "guess": "unsure",
  "confidence": 0.7191,
  "model_score": 0.8005,
  "style_score": 0.6712,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
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
  "content_id": "44ca535f-752f-4e28-81b9-240c6f44675c",
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
  "content_id": "0ce29f96-e98e-45fc-b929-0d96c47eef4d",
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
  "content_id": "2c88019a-d4e9-4f54-861c-b559b914f8bc",
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
  "content_id": "6a3e1f68-2d8c-4e07-be2c-cc4be768e998",
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
  "content_id": "2beabbf6-affe-4a6e-8533-dd664ba485fe",
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
  "content_id": "8f2891e7-591b-49f8-ab52-463a74ee0f46",
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
  "content_id": "eacd3c28-72e8-4467-b230-8831893ec504",
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
  "content_id": "de2e7f7e-4864-4a1b-842d-2847b288d1f4",
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
  "content_id": "2488d78e-0814-4a40-af3d-07fb6a7348df",
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
  "content_id": "4f2ed37b-cfde-4e3d-8767-b8416b8474d1",
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
  "content_id": "0cab5c82-3511-4d0b-b70d-165fd6768103",
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
  "content_id": "5c5714c4-93da-4b26-b42d-6414476d3d84",
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
  "content_id": "84354b1b-9943-48c0-b238-4b9a55c15446",
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
  "content_id": "498a5114-a198-404f-a013-165332c4ff14",
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
  "content_id": "34dd146c-6fbc-4477-93e6-041a02af845a",
  "creator_id": "attacker_MF08",
  "guess": "unsure",
  "confidence": 0.7074,
  "model_score": 0.9876,
  "style_score": 0.6522,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. Our checks gave mixed or weak results, which often happens with clear, plain or carefully edited writing. This is not a finding that AI was used, and it shouldn't be treated as one.",
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
  "content_id": "0a65a30e-6e07-4cfd-af16-3a3d32240dbb",
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
  "content_id": "660bd357-7ea7-4ad6-ae61-652de1326ec1",
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
  "content_id": "0c966497-4942-496f-9283-0652b18165a6",
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
  "content_id": "115776e8-567d-4112-ad50-25511295b4f1",
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
  "content_id": "09c52a51-fbae-442f-a72f-7cb419274d8b",
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
  "content_id": "42dca357-bee5-46b1-a1d7-d577212ab6fb",
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
  "content_id": "9bb8307f-43b4-406e-a8a5-0bc5b785fa90",
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
  "content_id": "91e023fd-2033-4185-bce8-43238678fb92",
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
  "content_id": "8db80191-d8b6-460f-b845-d0b6424b4665",
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
  "content_id": "1a4374f7-fb8b-4f3b-a6e9-0cffaccd4851",
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
  "content_id": "db4791ed-0ae6-4a86-aa0f-4c0b5fe04c64",
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
  "content_id": "a97a4413-90d5-4ec5-b390-cc043299ccd5",
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
  "content_id": "db23d371-b118-4932-99aa-93f981b9f2cb",
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
  "content_id": "b9eac451-8019-410a-8ab1-9e3a1b7e19c8",
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
