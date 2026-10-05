# 43 Work Breakdown Structure — 执行任务总表

状态：ACTIVE

## Phase M — 人物模型

### M01 DAIYU Model Sheet
Owner：ChatGPT/Hero Lane
Status：candidate exists
Exit：用户批准脸、发式、服装

### M02 WUKONG Model Sheet
Owner：ChatGPT/Hero Lane
Status：candidate exists
Exit：用户批准猴脸、毛区、冠饰、服装

### M03 Couple Scale Sheet
Owner：ChatGPT/Hero Lane
Status：candidate exists
Exit：身高/体型/同框比例批准

### M04 Local Hash
Owner：Codex
Blocked by：M01–M03 final files local

### M05 Golden Model Manifest
Owner：Codex + User
Blocked by：M04

---

## Phase V0 — Visual Lock

V001 reference import
V002 reference index
V003 face set approval
V004 costume set approval
V005 composition refs index
V006 contact sheet
V007 VISUAL_TARGET_LOCKED

---

## Phase K1 — LOOKREEL Keyframes

每个 COMP 拆为：
- K1-Cxx-01 bundle
- K1-Cxx-02 candidate generation
- K1-Cxx-03 face QA
- K1-Cxx-04 costume QA
- K1-Cxx-05 anatomy QA
- K1-Cxx-06 user approval
- K1-Cxx-07 manifest/hash

10 镜全部完成：
K1-GATE = TEN_KEYFRAMES_APPROVED

---

## Phase T1 — Video Candidate

T101 production workflow hash
T102 Guard test expected fail on unapproved
T103 Guard test pass on approved
T104 COMP09 I2V
T105 COMP04 I2V
T106 COMP01/05 I2V
T107 identity QA
T108 repeat best LOW-risk 3–5 times
T109 production candidate decision

---

## Phase E0 — Look Reel

E001 select 10 stills
E002 select accepted clips
E003 assembly
E004 ambience/music
E005 technical QC
E006 user review
E007 LOOK_REEL_APPROVED

---

## Phase E1 — EP001 Keyframes

S001–S020：
每镜与 K1 相同：
bundle → candidate → QA → user approval → manifest

EP-KF-GATE：
20/20 story keyframes approved

---

## Phase E2 — EP001 Motion

优先：
SH001
SH002
SH006
SH007
SH013
SH017
SH018
SH019

从中选 4–6。

每镜：
Guard → Take1 → QA → optional Take2 → accepted/static。

---

## Phase E3 — First Cut

E301 picture assembly
E302 pacing
E303 VO
E304 ambience
E305 SFX
E306 subtitle
E307 technical QC
E308 user review

---

## Phase A1 — Identity Automation

A101 approved dataset audit
A102 dataset split
A103 caption
A104 first LoRA
A105 fixed regression
A106 compare Hero Lane
A107 promote/reject

---

## Phase A2 — Audio

A201 voice casting/reference
A202 TTS baseline
A203 emotion test
A204 EP001 VO
A205 lip sync eligible-shot test
A206 sound mix

---

## Phase A3 — Control Plane

A301 schema validation
A302 episode init
A303 render queue
A304 guard
A305 submit
A306 monitor
A307 QA records
A308 resume
A309 edit command
A310 final QC

## 总规则

任何任务都有：
Input / Owner / Output / Exit Gate。

“继续做”不是任务状态。
必须能指向具体 WBS ID。
