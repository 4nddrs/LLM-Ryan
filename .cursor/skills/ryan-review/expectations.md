# What Ryan expects

Use these as interpretation rules, not as a demand that every update use his default stack. He changes his mind when a result survives contact with another result he trusts. Say so when you are applying a prior rather than reading it off the page.

## Default stack, when the setup is underspecified

He reaches for this when imitation or RL is not learning and the encoder is frozen or weak:

- Fine-tune the visual encoder. DINO v2 is the checkpoint he named. Gradients have to reach it. A frozen ResNet that needs on the order of 1M–10M samples for about +5% success is, for him, a reason to change encoder and algorithm.
- Diffusion or flow matching, with action chunks. He treats VQ-BeT-style discretization and flow matching as different algorithms. "It is just a data problem" is not an answer until the speaker can say what each algorithm is doing.
- Separate the contact problem from the semantic-memory problem. A low-velocity keyframe can matter for dexterity. It fails as a general memory rule: a stuck failure also has near-zero velocity, and a semantic scene can change while the arm moves quickly.

## Long memory

- "Long memory" in this group means the question actually depends on a long video. A benchmark whose items need fewer than ~32 frames is not long memory, even if the paper calls it that.
- The bar he got excited about is items that need on the order of 2,000 frames, produced by making an existing benchmark harsher (more repetitions, done only at the end), then showing other models near zero and theirs well above that.
- That claim is only as good as a human watching the videos and agreeing the question really needs those frames.
- V-JEPA, as he stated it, does not go past ~500 frames. A fixed-memory column at ~2,000 frames (fewer tokens per frame) is the baseline he asked for against recurrent memory. If fixed memory still wins at the longest videos they can run, the recurrent result is not yet evidence. The non-recurrent run exists to test whether recurrent is needed at all.
- Do not buy that length by lowering the resolution. Two frames collapsed into one token is a different claim from a longer video at the same resolution. He was unsure a paper's "no gain from more frames and higher resolution" answered it. Frozen V-JEPA plus transformer blocks trained on top is not a V-JEPA fine-tune, and it is not automatically a VLM fine-tune. Ask which weights moved. A recurrent output still has to say whether those weights were trained, fine-tuned, or taken from somewhere else.
- He wants the plan, a short literature check, and the prompt itself, so he can re-run it. Clarifying questions come before "done."

## Data, before the next training run

- A surprising or counterintuitive data result earns days of reading, not a new run. He would rather three people spend several days deciding which VQA angle to train than start from a pile a model already "filtered."
- Audit simulator VQA by category. Spatial questions are suspect until someone checks that left/right and similar labels match the scene. Ask whether every simulator uses the same three categories, whether spatial should be dropped, and how much data remains. On 13 Oct the split was still inconclusive, with a general trend and no decision. A left/right question from a single image is ill-defined. A question whose answer is given as input at the start is not a prediction. Object identity (which thing to pick up) he treated as useful because the motion repeats and the identity is what the policy needs. The same images and questions with wrong answers were worse, which is the control that the text mattered. Ask whether spatial was helpful, slightly helpful, or worse. Do not upgrade that to a decision.
- A set he called out at 52 examples is too small to fine-tune or train. Increase it. Do not invent a new minimum.
- A 7-number action (xyz, rotation, gripper) is comparable to LIBERO's 7 only when the order matches. A recipe sentence that does not say the order is ill-defined.
- UMI-style public data that ships actions still has to say how those actions were measured. Two cameras plus a file of actions is not yet that answer.
- Demo collection: the honest maximum at acceptable quality. A larger daily count that hurts quality fails. He wants that ceiling said plainly.
- UMI-style video is relevant only with the action ground truth (arm and gripper). "Small experiment" plus many hours and terabytes gets challenged. Ask for a confidence number, and do not push that number down just because the question was skeptical.
- Wrist versus head camera is unsettled. Egocentric hand tracking, in his experience, is usable for coarse left/right motion and weak during in-hand manipulation because the hand occludes the contact. He wants sample videos at a few wrist-camera angles before a decision.

## Writeups

- A report he will read has four parts: the experiment's exact title and why it exists, the architecture drawn in markdown or LaTeX, the context behind the findings, and an evaluation that is the author's own score or an explicit "not scored." Findings alone fail that note. A score he would have to infer fails it too.
- Long context goes in the note, in brackets if needed. He will not reliably remember each person's exact setup.
- Numbers that summarize a qualitative report (a 4/5) must be the author's number, written down. He does not want to infer the score.
- When he asked someone to run a prompt and bring back the model output, that prompt and that output go in the doc. A spoken summary of that session fails. A measured success rate is not a model session. It needs the comparison it claims, on the same setup.
- Hardware and CAD close with a video or a tester score, plus who the tester is and whether they had time. A new version number does not close. The video has to show the behavior the part was built for. A fingertip touch that does not deform the tip fails that test. A different tube is a different object.
- The first line of a note says whether the result supports the hypothesis or cuts against it. He should not have to read to the bottom to learn that the author has not identified it yet.
- A difference of 17 versus 19 is not a big gap. Call a gap big only for the rows that actually separate. "Ours" means either the paper's reported number or a re-run of their checkpoint, and the cell says which.
- Subtask text is stage 1. Using it inside a VLA is stage 2. He was about 70% sure a note had skipped stage 1, and he said the certainty out loud. Reliable subtask text on the simulator and on the real setup comes first. There is no ground-truth subgoal in the real world.
- A success rate is not the end of an improvement claim. Look at the misses. On 13 Oct the split he used was semantic (moved on believing the grasp had worked) and dexterity (motion that never really grasped). Wrong object and failing to navigate are Sudhir's additional split, which he accepted. A 60% success still leaves the other 40% to categorize. Do not invent names for a nine-category list he asked Sudhir to pass on.
- A block added by a model session, such as a small selector network, is unexplained until they can say what it selects, and he wants the failure videos.
- A page he opens has to answer in 2 to 5 seconds. Who is using the machine, in order, and CPU, memory, and GPU, not only idle. Empty rows and a number with no unit fail. Text he has to zoom to read fails. The author's name is on the summary. Login can exist. A ground-truth labeler can be him or Gabriel, and distance to his rating can be computed. A feature that does not change that view does not belong. A fork of the page is acceptable.

## Near-term bar he repeated

One simple autonomous video on their UMI / XRM6 setup: one tube, pick it up, move it. More tasks, more data, and a bigger GPU make the general ML questions matter later. With a single task, those questions are secondary to that video.

Jordan can preempt training runs. Simulator work can sit on CPU. Idle machines should be visible. Do not treat a preempted run as a scientific result.

## Strategy, only if asked

He is reasoning from failed hard-tech companies, not from a finished plan. Hard tech: people want it and it is difficult to build. A round is meant to be spent on a short horizon and to buy a milestone. Revenue without profit is the failure mode he is afraid of.

His current knee-jerk, which he labeled as unsettled: if a general robot API reaches high success, the durable wedge may be taking that last fraction of reliability in healthcare and getting through regulation quickly, which may mean buying a platform instead of building a robot. Do not present this as a decision. Present it as his open fear, and ask which evidence would keep or kill a hardware bet.
