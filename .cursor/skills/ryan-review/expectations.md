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
- On 19 Oct the run he was already generating had a sharper version of that baseline. Fixed attention is the thing recurrent has to beat, and he said there is more than one fixed attention, so the cell has to name which. A goal written as "here is data from the four PCs, show me something" is not that comparison. Recurrent with no reason past a fixed attention that already works is not a result.
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

On 19 Oct he described the close he would actually save. The barcode stays fixed, taped down if that is what keeps it still. The tube is brought next to it. A beep is not the check. The scanner flash is the check that it was recognized, and then the tube moves to the next bucket. When he says a video is good, it goes on a sheet in the moment, not from memory later. A tidy row is too easy: horizontal, vertical, overlapping, and stacked. A simple store-bought object is enough for that demo. An industrial fixture is not the bar.

Jordan can preempt training runs. Simulator work can sit on CPU. Idle machines should be visible. Do not treat a preempted run as a scientific result.

## 13–16 Oct, and the ETH sit-down on 19 Oct

The Tuesday recording is the 13 Oct meeting. The bars below are the parts that meeting, the 15 Oct meeting, the 16 Oct meeting, and a separate ETH feedback sit-down on 19 Oct added. They do not retire a 19 Oct lab-meeting bar. Where they conflict, the lab meeting that day wins: the scanner flash is the check, not the beep, and the 5090 he is using is not a spare.

### Short memory is not a long-memory result

If the longest item needs about 30 frames, fixed attention over those frames is the run that maximizes that benchmark. Recurrent is a different experiment, for a task that actually needs far more. A long task whose next action follows from the current view is Markov. RoboCasa was his example. It is not a long-memory test. Do not drop the resolution to buy a longer memory and call that the same model.

A public VQA set whose items top out near 30 frames does not test the 2000-frame bar. The test he described is a task they build that needs that length, with a success rate. He had not designed it yet.

### What one success is

A percentage needs the trial. One marker from the left bucket to the right is not the whole pile. He once called about 95% a reasonable number for that single left-to-right move, and later called 80% the more honest number for the policy in front of him. The definition is the bar, not either number.

A person who opens the gripper, stands the object up, or resets mid-episode did not record an autonomous success. The failure he has now seen is a gripper left partly closed, and an object lying down when the data was mostly upright. Recovery data is that failure, on purpose, not a random extra hour of the tidy case.

### A full checkpoint is not one block

XR-1's whole checkpoint beating their stack is not a reason to take one piece of it. The note says which piece moved the number: the vision encoder, the language model, the action transformer, the number of inference steps, or the dataset. An encoder-only gap of a fraction of an error point, 24.6 against 24.9, is the same encoder. Their own stack can be good enough when the full model is only slightly better and slower.

A claim that a VQA category hurts needs the no-VQA column. Wrong answers on the same images were worse, not a free augmentation. A question whose answer is already the task text is not a memory test.

He thinks a spatial question about an object the task does not use can fill a small encoder, and that scoring 29 centimeters against 30 as a full miss can dominate the loss. He called that a knee-jerk and said it is interesting if it turns out true. Do not state it as a decision. The sentence that earns a look is the one with the person who measured it and the number, such as attention on the background. "It was found" is not that sentence.

### The motion, not a patch

A policy that runs can still jerk. The close is one trace: when the prediction happens, which actions are executed, what is sent to the controller, and the measured position. The last small difference is the work. Telling a coding agent "there is a jerk, fix it" is not the trace.

Teleoperation uses the controller. Hand tracking was the idea he set aside.

### Papers, names, and Claude

A method from a paper with no released code is not a plan. He will not tell them to adopt it.

"Claude said" is not a measurement. A jump from 0% to 40% that Claude explained can flip once someone checks what was actually in the action loop. A selector Claude added, or a SOTA number Claude named, is Claude's sentence. The person who signs the report can say what ran.

A remote session needs a name he can read on the left: who, which machine, what the work is. The account is extra. A name that reverts is a bug, not a naming scheme.

### Data and the week

About 50 episodes was too small to fine-tune. Say the count. A model trained on last month's labels is not a result on this month's setup. He asked for three or more labelers on a frame of the new set. Show the labelers the last minutes of the real failure so the new data is not only the tidy vertical case.

A next-week note is one or two lines, a day, and a confidence, even a low one. It lives in their own note. His lines go at the bottom, with the previous note kept underneath. A training run that never meets the robot is not finished. The person who trained it asks for the machine and the video.

Pretraining on the other people's data and then training on the robot's own data is a test he wanted on the real robot. He was about 40% sure. If the gripper changed, it is not one dataset.

He profiled a force mode near one centimeter of error and more compliant than position control. He did not switch the policy to it.

Real-to-sim is useful if it can rank checkpoints. He is doubtful that it is good enough, and he has not closed it. Interrupting the real robot, resetting, and continuing is the other option he was considering. It is not an approved plan.

## 19 Oct

The notes below are what he said in that meeting. They do not retire an earlier bar unless the sentence says they do. Other people's explanations are not his. A stretch where the recording collapsed into one repeated sentence is not his either.

### A Friday he can hold

He asks what will be done by Friday, and he wants the part the person controls even when the client has not decided. "Ready for whichever option they pick" is the close. A date that depends on the other side still needs a day, named in advance, when he will be told the new date. A long status is not what he asked for. He said the note can be much shorter than the one he was looking at.

A hardware or research sentence that only says "done" fails. He wants the missing piece in a sentence or two: no dexterity, no spatial, what the next try is.

His own lines go at the bottom of a shared note so he can see which sentences are his. He will not reconstruct that from a mixed page.

### Machines

A slow PC, or a PC that has been unreachable, is not an excuse while other machines are empty. He had watched a weekend where almost nothing ran. The person asks Shamir or Gabriel for a machine and says what has to be finished by when. They message him when a machine dies. They do not wait for him to notice. The 5090 he is using is not the spare. A run that never started is not a result, and it is not "not my fault."

### The data he was already generating

Four machines were generating different angles of the four benchmarks and uploading to R2, and the 5090 was training on that. He wrote the prompts so the angles would not overlap, and he does not know whether they actually differ. He wants that studied, including the failure data, and reported back. Do not treat the prompt as proof the sets differ.

The failure text is part of the method he stated. The model says what happened, such as that the pencil was dropped, and that text is fed back into memory. He wants the semantic part carried by text so the visual encoder's capacity goes to sensorimotor and procedural work, not to semantic work. He was not sure the run was doing that. Saying it is the goal is not the same as showing it.

He cannot delegate a new angle, and he was unsure this was a good use of his time. Syed, and Hugo or Louis, were the people he asked to look and send him thoughts. It is not a result until the success rate moves on their own benchmark.

### Sim to real

He asked whether the bottleneck is that simulator success is not showing up on the real robot, or that there are not enough machines. A simulator result still wants the real-robot video. He let one pass with "that's okay" after being told it had been tried and was not working as it should. That is not a close. "It works, but not like it should" is an open failure.

### Gripper

He did not want the fingertip cutoff at the top. That shape was for one grab, not the general finger. He wants the tips the other way: they meet first, then squish, and the gripper can close completely, including on something as small as a pencil. A curved close is not accepted just because it is the current design. He was unsure it was better than a linear close, and he said it depends on reliability on the real robot.

A cable that tightens the fingers fails when it loosens, because the close is then not the close they commanded. He wants the cable gone, a Stanford UMI-style close, and a crankshaft that replaces the string and spring. The arc has to cover the full close, including how far the mechanism actually moves, not only the drawing. This is the issue he called serious: it makes the gripper on the XRM6 unreliable.

The close is a video of the grip, not a print and not a version number. He asked for that video from the person who designs it and from Jordan, who prints it. One person owns the new version. Earlier than the date they named is better. If they need help, they ask for it.

### A size you can already see

A base that looks too small to stand is not something to discover after a V1 is "done." He would rather a few days now than two weeks building it and two weeks learning that it falls. He accepted that the person who built it knows the interfaces better than he does, and that a first version can exist so the rest can be tested. He did not accept planning to be surprised by a size that is already visible. Scaling it up after the interfaces are known is the work he asked to see, not a promise he treated as done.

### Offline error is not the success rate

He was shown a case with many paper standards and no universal one. His bar was to try the relevant ones and measure success rate on the robot, not the offline error that had been the number so far. When the real robot is too slow for that sweep, a simulator of a similar task is the stand-in he accepted. He named LIBERO Plus. He was unsure the task was similar enough, and he said a wrist-only view might make it closer. A LIBERO success rate can still be the number, and the note says that the task may not match. An offline error labeled as the result fails.

### Where to look

The idea he told them to implement is not "the wrist camera is always high resolution and the external view is always low." The paper he was shown uses no wrist camera. A high-resolution crop of the region that matters is attached to a low-resolution external view, and that matched accuracy without the wrist camera. His simpler wording was the same split: high resolution where you need it, low resolution on the rest. "Where" has to be defined. He also wants "where to look" as a VQA question, and the high-resolution region to be that answer. The VLA outputting where to look, a point and a box, is part of the idea, because the policy then learns what mattered. He said to implement it because it will help in general. Saying he wants it is not a result.

### What he will accept as the agent's goal

He was babysitting the four data machines. They stop until a person clicks the question. He wants one session that can reach each machine and write the next prompt there, pick the recommended option instead of waiting, and if a machine has been idle for about 15 minutes, check that the git version is current and keep generating. He does not trust a goal that merely says "check every half hour" until he has seen the machines still running for about a week. He said he would try it, and that if it holds it is the cleanest version. Token limits and sessions on different accounts are the stop he already hit. He had been shuffling logins by hand. A dead token is not the model being finished.

After he was shown a long agent log, he raised his own goal. "Here is the data, show me something" is too small. The goal is to beat fixed attention, or a stated success rate, and to keep a log of what was run, what the result was, and what the hypothesis was. He will ask for the summary, the insights, the doubts, and where it is failing, and he may hand it a paper. Letting an agent run the real robot, including inventing how to score a pile of tubes moved from one side to the other, is something he said to think about. He also said it is dangerous. It is not a plan he approved.

### How he talks when he is stuck

He talks the worry out loud to a model while he keeps working, including a worry as plain as the startup failing, and he gives it a text file of context because it does not know the company. A loop where he circles the same fear is the failure mode he uses this for. This is his working habit. It is not a bar for someone else's experiment.

## Strategy, only if asked

He is reasoning from failed hard-tech companies, not from a finished plan. Hard tech: people want it and it is difficult to build. A round is meant to be spent on a short horizon and to buy a milestone. Revenue without profit is the failure mode he is afraid of.

His current knee-jerk, which he labeled as unsettled: if a general robot API reaches high success, the durable wedge may be taking that last fraction of reliability in healthcare and getting through regulation quickly, which may mean buying a platform instead of building a robot. Do not present this as a decision. Present it as his open fear, and ask which evidence would keep or kill a hardware bet.

On 19 Oct he added three open worries, still not decisions. Do not bring them up unless asked. Do not mention the first one to OHUS people. He said that out loud.

- They may take over a B2C business next year. It was unclear. Taking it over means the revenue becomes theirs while the other side can still make the last call. He does not treat that as a prize. He is worried at-home health tests are a bad business because a sick person goes to a doctor. The use of knowing that is to stop spending on work that does not matter. Be ready at a professional level before the date, if the date arrives.
- The company name he was testing was nine-scale. He liked it and worried people will not see what it means. The logo was what made the name make sense to other people in the room. He did not close the name.
- A business recommendation a model wrote is not grounded until there is an example, a counterexample, and a named expert. One or two rows, not a pile. Do not send those rows to Claire or Emma as a scatter of asks.
- He does not know whether a company account should post technical results. He has seen posts go nowhere, and he has seen companies grow by posting and companies that never post and only show the work. Making the client happy is what he said makes money. Attracting technical talent by posting is, for him, a bet on the hospital business. He accepted the framing that a leaderboard post is a byproduct of client work, not the goal of the work. He did not pick a posting policy. A result someone did themselves is that person's to post.
