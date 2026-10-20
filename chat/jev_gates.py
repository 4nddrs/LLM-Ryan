"""Jev choice used as the first objection on an update.

The criteria are the bars already written in the review notes. Jev is not
fine-tuned. Editing a criterion and re-running this file is the training step.
"""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
ENDPOINT = "https://api.typesafe.ai/v1/systemone"
# Lowest no_objection confidence on the labeled set after the criteria settled.
RELEASE = 0.75

OBJECTION = {
    "unfinished_comparison": "The other side is not shown finished on the same model, the same data, and the same eval.",
    "missing_fixed_baseline": "The fixed-attention or fixed-memory number at the same frame budget is missing.",
    "not_long_memory": "The longest bin is a few hundred frames, not the 2000-frame bar.",
    "offline_not_success": "The number is an offline error or a loss, not a success rate.",
    "stage2_early": "The policy was trained on subtask text before that text was shown to be right on the simulator and on the real setup.",
    "hardware_not_closed": "There is no video of the behavior this part was built for.",
    "small_gap_called_big": "A gap of about two points is called big.",
    "name_not_exact": "The model name is a family nickname, not the exact variant.",
    "skipped_row": "The best-group sentence skips a row that sits inside the group.",
    "missing_trial_count": "The trial count is missing from a suite they want to retire.",
    "idea_without_result": "The mechanism has no measured result.",
    "model_not_human": "A model is the only one who checked the videos, the items, or the reason for the gain.",
    "page_unreadable": "The page does not show who is on the machine, with CPU, memory, and GPU.",
    "idle_machine": "A slow or dead machine is the excuse, and no empty machine was requested.",
    "not_the_crop": "A wrist camera left on high resolution is not the where-to-look crop.",
    "not_our_call": "The meetings do not decide this.",
    "trial_undefined": "The success rate does not say what one trial is, or a person intervened.",
    "jerk_untraced": "The motion has no trace of prediction, executed actions, controller command, and position.",
}

QUESTION = {
    "first_objection": {
        "type": "choice",
        "instructions": (
            "Pick the single first objection. "
            "no_objection only when the sentence is already entitled, "
            "or the message is only a greeting or a next-step question "
            "that does not claim a finished result."
        ),
        "criteria": {
            "unfinished_comparison": (
                "A winner is named between two methods, and the update does not "
                "say the other side finished on the same model, the same data, "
                "and the same eval. Writing both scores is not enough: a fine-tune "
                "with no epoch and no 'finished' still counts. A method tried only "
                "on an earlier model counts. A full third-party checkpoint credited "
                "to one block, or a VQA category said to hurt with no no-VQA column, "
                "counts. It does not count when the update says both runs finished. "
                "A missing fixed-attention number is not this option."
            ),
            "missing_fixed_baseline": (
                "Recurrent memory or a recurrent policy is said to improve or "
                "to be the one to ship, and no fixed-attention or fixed-memory "
                "number is given at the same frame budget. Shipping recurrent "
                "because the longest item is about 30 frames counts. It does not "
                "count when the update only calls a task long memory and does "
                "not say recurrent should ship."
            ),
            "not_long_memory": (
                "The update calls the coverage long memory, and the longest bin "
                "it reports is a few hundred frames. The bar is on the order of "
                "2000 frames. A long task whose next action follows from the "
                "current view, called long memory, is this even with no frame "
                "count. Dropping resolution to buy length and calling that long "
                "memory is this. A result that already states about 2000 frames "
                "is not this. Choosing recurrent versus fixed on a short benchmark "
                "is not this."
            ),
            "offline_not_success": (
                "The reported number is an offline error, a loss, MSE, or a "
                "representation score, and that number is treated as the robot "
                "result. Calling a pretrain unhelpful, or an encoder the one to "
                "use, from an error, without a robot run, counts. A fraction of "
                "an error point treated as a difference counts. Two policy "
                "accuracies, such as 71 versus 64, are not an offline error. A "
                "success rate on the robot or on LIBERO is not this."
            ),
            "stage2_early": (
                "A policy or VLA was trained or fine-tuned to follow subtask "
                "text. Naming the model that writes the text is not a reliability "
                "check. This fires unless the update says how often that text is "
                "right on the simulator and on the real setup."
            ),
            "hardware_not_closed": (
                "A hardware version is called done, or the only evidence is CAD, "
                "a print, or a version number. A video that does not show the "
                "behavior the part was built for also counts, including a "
                "fingertip touch that does not deform the tip. A tester score "
                "plus a video where the tip deforms does not count."
            ),
            "small_gap_called_big": (
                "A gap of about two points, such as 17 versus 19, is called big, "
                "large, or a lot. Saying the policies do not separate is not this."
            ),
            "name_not_exact": (
                "The result is attributed to a family nickname. 'Cosmos' with no "
                "Reasoner and no Policy is this, even if a success rate is "
                "written next to it. A full name such as Qwen3VL is not this."
            ),
            "skipped_row": (
                "A best group is named, and a row that sits inside that group "
                "is left out of the sentence."
            ),
            "missing_trial_count": (
                "Suites are called saturated, skipped, or retired, and no trial "
                "count is written. If a trial count is written, this does not fire."
            ),
            "idea_without_result": (
                "A new mechanism is described and no measured result is attached. "
                "A keyframe or memory idea with no number is this. A paper with "
                "no released code, offered as the method to train, is this."
            ),
            "model_not_human": (
                "A language model is the only check that videos, items, a sensor, "
                "or a reason for a gain are valid. 'Claude said' why a percentage "
                "moved, a SOTA number a model named, or a model saying a phone is "
                "accurate enough, is this. No person is said to have measured it. "
                "Strong numbers do not cancel this. It does not fire when the "
                "update says a person measured it."
            ),
            "page_unreadable": (
                "A machines page is shown and it does not answer, in a few "
                "seconds, who is using the machine and whether CPU, memory, and "
                "GPU are busy. A bare number with no unit counts."
            ),
            "idle_machine": (
                "The work is late because a PC was slow or unreachable, and the "
                "update does not say another empty machine was requested or that "
                "he was told the machine died."
            ),
            "not_the_crop": (
                "A wrist camera that is always high resolution, paired with a "
                "low-resolution external view, is presented as the where-to-look "
                "method. That method crops a high-resolution patch on the "
                "external view and does not use a wrist camera."
            ),
            "not_our_call": (
                "The question is company strategy, buying versus building a "
                "robot, fundraising, or what to post. The experiment rules do "
                "not decide it."
            ),
            "trial_undefined": (
                "A robot or policy success percentage is given, and the update "
                "does not say whether one success is one object or the whole "
                "pile, or a person opened the gripper or moved the object and "
                "the run is still called autonomous. It does not fire when one "
                "success is named as a single object and the update says no "
                "person touched the run. A benchmark accuracy with a named "
                "frame budget is not this."
            ),
            "jerk_untraced": (
                "A robot motion is called smooth, done, or fixed, and the update "
                "does not describe when the prediction happened, which actions "
                "ran, what the controller was sent, and the measured position. "
                "Handing the jerk to a coding agent counts. A table of two "
                "finished runs is not a motion."
            ),
            "no_objection": (
                "A greeting, or a claim that already carries the field the bar "
                "asks for. A trial count when suites are retired. A fixed "
                "baseline named beside a recurrent number, with both runs "
                "finished. A tester score out of 5 together with a video of the "
                "tip deforming. A success rate that names the trial and says "
                "no person intervened. One named object, where it started, where "
                "it ended, and that no person touched it, is enough on its own. "
                "Architecture is not required for that sentence. A motion trace with prediction, executed "
                "actions, controller command, and position. A next-step question "
                "that does not claim a new finished result."
            ),
        },
    }
}

# (name, update, expected choice). Verbatim lines are from the review notes.
# The second of each pair is a paraphrase, so a hit is not a memorized sentence.
CASES: list[tuple[str, str, str]] = [
    ("fine-tune open", "Frozen V-JEPA, recurrent memory 64: higher accuracy than fine-tuning the last transformer blocks.", "unfinished_comparison"),
    ("fine-tune open, other words", "The frozen encoder scores 71 and the fine-tune of the last blocks scores 64. We're going with frozen.", "unfinished_comparison"),
    ("earlier model only", "No gain from DINOv2 or a flow-matching head. Those two were only run on the early model. On the current model, predicting the target as a pixel went from 8% to 12.5%.", "unfinished_comparison"),
    ("recurrent, no fixed", "Recurrent memory accuracy rises as we go from short clips toward 2000 frames.", "missing_fixed_baseline"),
    ("recurrent, ship it", "As the clips get longer, the recurrent policy keeps climbing. At the longest setting it's the one to ship.", "missing_fixed_baseline"),
    ("bins stop at 511", "LIBERO-Mem, RoboMME, and MIKASA-Robo show strong long-memory coverage. About 63–65% of QA pairs have evidence gaps over 192 frames, and about 30–33% over 320. The longest bin is 321–511.", "not_long_memory"),
    ("offline error", "We tried the standards from the papers. Offline error is down, so the representation is better.", "offline_not_success"),
    ("mse as the robot", "Held-out feature MSE dropped from 0.42 to 0.31, so the visual encoder is in good shape for the robot.", "offline_not_success"),
    ("stage 2", "We fine-tuned the VLA on simulator subtask text so it follows the subgoal. Qwen3VL writes the subgoal.", "stage2_early"),
    ("stage 2, other words", "Qwen writes the subgoal sentence and we already fine-tuned the policy to follow it.", "stage2_early"),
    ("gripper cad", "Gripper v3 is done. CAD is uploaded.", "hardware_not_closed"),
    ("soft touch", "Gripper tip v2, video attached. The finger touches the tip.", "hardware_not_closed"),
    ("two points", "Ours is a big gap over the paper, 19 versus 17, on RoboMME.", "small_gap_called_big"),
    ("two points, other words", "We beat the paper by a lot: 19 against their 17.", "small_gap_called_big"),
    ("cosmos", "Fine-tuned Cosmos on our VQA and the policy success is 78%.", "name_not_exact"),
    ("skipped row", "g_nospatial, g_semantic, and g_state are the best group. g_semantic_s43t sits second and the sentence skips it.", "skipped_row"),
    ("no trial count", "Clean scenes are saturated and cannot differentiate these policies, so we will skip full evaluations. Spatial 97.0 / 97.5, Object 99.5 / 99.0, Goal 96.5 / 94.0.", "missing_trial_count"),
    ("keyframe idea", "Save a frame when velocity drops, keep one frame per slowdown, pass those keyframes as memory.", "idea_without_result"),
    ("claude watched", "We made the long-memory items need ~2000 frames. Other models fell to ~0, ours is ~50%. Claude confirmed the items really need 2000 frames.", "model_not_human"),
    ("machines page", "The machines page lists every host, with notes and scores. 87 is on the front.", "page_unreadable"),
    ("slow pc", "The run is late. The PC was too slow, and Linux 4 has been unreachable since Saturday.", "idle_machine"),
    ("wrist as the paper", "We implemented the paper. The wrist view is high resolution and the external view is low resolution.", "not_the_crop"),
    ("buy or build", "Should we buy a robot platform or build our own?", "not_our_call"),
    ("greeting", "hey, you there?", "no_objection"),
    ("clean, counted", "Clean scenes, 40 trials per cell. Spatial 97.0 versus 97.5, Object 99.5 versus 99.0, Goal 96.5 versus 94.0. These do not separate the policies, so we will skip full evaluations.", "no_objection"),
    ("fixed is named", "Recurrent scores 61 and fixed attention scores 44 at 2000 frames, same frame budget, both runs finished.", "no_objection"),
    ("grip video", "Jordan scored the grip 4/5. The video shows the tip deforming under the press.", "no_objection"),
    ("next run", "Clean suites are saturated, 40 trials per cell, and they do not separate the policies. Should I spend the compute on noisier scenes or collect more demos?", "no_objection"),
    ("markov called long", "RoboCasa is a long-horizon task, so this is our long-memory result. The current view is enough for the next action.", "not_long_memory"),
    ("thirty frames, ship recurrent", "Nothing in the benchmark needs more than 30 frames, so the recurrent model is the one to ship.", "missing_fixed_baseline"),
    ("claude explained the jump", "Success went from 0% to 40%. Claude said Cosmos 3 Nano Reasoner is why, and it was only choosing the object.", "model_not_human"),
    ("error point as the robot", "DINO's error is 24.62 and the other encoder is 24.94, so DINO is the one to use on the robot.", "offline_not_success"),
    ("paper, no code", "We should train the method from that contact paper. They never released the code.", "idea_without_result"),
    ("spatial hurts, no control", "Spatial VQA hurts the policy. Semantic plus state is better. We never ran the no-VQA arm.", "unfinished_comparison"),
    ("whole checkpoint, one block", "The full XR-1 checkpoint beats our DINO policy, so we should take their language model.", "unfinished_comparison"),
    ("ninety, no trial", "Autonomous success is about 90% on the marker task.", "trial_undefined"),
    ("hand in the run", "About 90% autonomous. I opened the gripper once when it stalled, then it finished the pile.", "trial_undefined"),
    ("jerk patched", "The motion is smooth now. I told Claude there was a jerk and it patched the controller.", "jerk_untraced"),
    ("one marker, untouched", "One marker, left bucket to right, 9 of 10. Nobody touched the gripper.", "no_objection"),
    ("trace is there", "The trace shows the prediction at 2.5 Hz, the four executed actions, the command to the arm, and the measured position. The jerk is at the replan.", "no_objection"),
]


def load_key() -> str:
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("KEY_JEV="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("KEY_JEV is missing from .env")


def first_objection(update: str, key: str | None = None) -> dict:
    payload = {"model": "jev-latest", "state": update, "questions": QUESTION}
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {key or load_key()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = json.loads(response.read().decode())
    return body["answers"]["first_objection"]


def decide(update: str, key: str | None = None) -> dict:
    answer = first_objection(update, key)
    ranked = sorted(answer["probabilities"].items(), key=lambda item: -item[1])
    choice = answer["choice"]
    confidence = float(answer["probabilities"].get(choice, answer["confidence"]))
    runner = ranked[1][0] if len(ranked) > 1 else ""
    runner_p = float(ranked[1][1]) if len(ranked) > 1 else 0.0
    return {
        "choice": choice,
        "confidence": confidence,
        "runner": runner,
        "runner_p": runner_p,
        "release": choice == "no_objection" and confidence >= RELEASE,
    }


ASK = {
    "unfinished_comparison": "What is the other side's number on the same model, data, and eval, and did that run finish?",
    "missing_fixed_baseline": "What does fixed attention score at the same frame budget?",
    "not_long_memory": "What is the longest item, in frames, and does the next action follow from the current view?",
    "offline_not_success": "What is the success rate on the robot, or on the simulator if that is the stand-in?",
    "stage2_early": "How often is that subtask text right on the simulator and on the real setup?",
    "hardware_not_closed": "Where is the video of the behavior this part was built for?",
    "small_gap_called_big": "What are the two numbers, without calling a two-point gap big?",
    "name_not_exact": "What is the exact model name, including the variant?",
    "skipped_row": "What does the skipped row score?",
    "missing_trial_count": "How many trials are in the cell you want to retire?",
    "idea_without_result": "What number has this been measured at, and is the code available?",
    "model_not_human": "Which person checked this, and what did they see?",
    "page_unreadable": "Who is on the machine, and what are the CPU, memory, and GPU?",
    "idle_machine": "Which empty machine did you ask for, and when was he told it died?",
    "not_the_crop": "Where is the high-resolution crop on the external view, with no wrist camera?",
    "not_our_call": "Is this a company question rather than a result?",
    "trial_undefined": "What is one success, one object or the whole pile, and did anyone touch the run?",
    "jerk_untraced": "Where is the jerk in the trace: the prediction, the executed actions, the controller, or the measured position?",
}


def talk_text(decision: dict) -> str:
    """One or two sentences. Empty when the objection is not clear enough to stop the talk."""
    choice = decision["choice"]
    if choice == "no_objection" or decision["confidence"] < RELEASE:
        return ""
    line = OBJECTION.get(choice, choice).rstrip(".")
    question = ASK.get(choice, "What would close that?")
    return f"{line}. {question}"


def hold_text(decision: dict) -> str:
    """The hold the colleague sees. The writer does not paraphrase it."""
    if decision["choice"] == "no_objection" and not decision["release"]:
        choice = decision["runner"] or "trial_undefined"
        line = OBJECTION.get(choice, choice)
        question = ASK.get(choice, "What would close that line?")
        return (
            "What's missing\n"
            f"- {line}\n"
            "I am not sure the update is clean.\n\n"
            "Questions\n"
            f"- {question}\n"
        )
    choice = decision["choice"]
    line = OBJECTION.get(choice, choice)
    question = ASK.get(choice, "What would close that line?")
    unsure = ""
    if decision["confidence"] < 0.60 and decision["runner"]:
        runner = OBJECTION.get(decision["runner"], decision["runner"])
        unsure = f"I am not sure this comes before: {runner}\n"
    return (
        "What's missing\n"
        f"- {line}\n"
        f"{unsure}\n"
        "Questions\n"
        f"- {question}\n"
    )


_FENCE = re.compile(r"```.*?```", re.S)
_NUMBER = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?(?![A-Za-z])")
_ARROW = re.compile(r"(?:→|->|-->|─)")
_SENTENCE = re.compile(r"[^.!?\n]+[.!?]?")


def _methods(text: str) -> set[str]:
    lowered = text.lower()
    found = set()
    if "recurrent" in lowered:
        found.add("recurrent")
    if "fixed attention" in lowered or "fixed-attention" in lowered:
        found.add("fixed")
    return found


def _strip_unpaired(reply: str, source: str) -> str:
    """A number sits beside two methods only when the update already put it there."""

    def source_allows(number: str, methods: set[str]) -> bool:
        for sentence in _SENTENCE.findall(source):
            if number in _NUMBER.findall(sentence) and methods <= _methods(sentence):
                return True
        return False

    def one_sentence(match: re.Match[str]) -> str:
        sentence = match.group(0)
        methods = _methods(sentence)
        if len(methods) < 2:
            return sentence

        def one(number: re.Match[str]) -> str:
            token = number.group(0)
            if source_allows(token, methods):
                return token
            return "—"

        return _NUMBER.sub(one, sentence)

    def scrub_part(part: str) -> str:
        return _SENTENCE.sub(one_sentence, part)

    parts = _FENCE.split(reply)
    fences = _FENCE.findall(reply)
    rebuilt: list[str] = []
    for index, part in enumerate(parts):
        rebuilt.append(scrub_part(part))
        if index < len(fences):
            rebuilt.append(fences[index])
    return "".join(rebuilt)


def _blocks_named(source: str) -> bool:
    text = source.lower()
    return any(word in text for word in ("architecture", "encoder", "transformer", "backbone"))


def scrub_released(reply: str, source: str) -> str:
    """Drop a drawn architecture and any measured number the update did not contain."""
    if not _blocks_named(source):
        reply = _FENCE.sub(
            lambda match: "Architecture was not named." if _ARROW.search(match.group(0)) else match.group(0),
            reply,
        )
    allowed = set(_NUMBER.findall(source))
    source_counts: dict[str, int] = {}
    for token in _NUMBER.findall(source):
        source_counts[token] = source_counts.get(token, 0) + 1

    def scrub_fence(match: re.Match[str]) -> str:
        body = match.group(0)
        if "Architecture was not named." in body and "```" not in body:
            return body
        seen: dict[str, int] = {}

        def one(number: re.Match[str]) -> str:
            token = number.group(0)
            seen[token] = seen.get(token, 0) + 1
            if token not in allowed or seen[token] > source_counts.get(token, 0):
                return "—"
            return token

        return _NUMBER.sub(one, body)

    reply = _FENCE.sub(scrub_fence, reply)
    reply = _strip_unpaired(reply, source)

    def one_prose(number: re.Match[str]) -> str:
        token = number.group(0)
        if token in allowed:
            return token
        start = number.start()
        end = number.end()
        at_line = start == 0 or reply[start - 1] == "\n"
        if at_line and reply[end:end + 2] in (". ", ".\n"):
            return token
        return "—"

    return _NUMBER.sub(one_prose, reply)


def report_instruction(decision: dict) -> str:
    if not decision["release"]:
        return (
            "\n\nThe report check already wrote the hold. Do not write the report. "
            "Do not add a missing line of your own."
        )
    return (
        "\n\nThe report check found no open objection. This wins over any earlier "
        "instruction to ask for the architecture or to draw a diagram. Write the "
        "report from the thread. Every number you write must appear in the update. "
        "A number given once does not go on a second row. If they never named the "
        "blocks, the Architecture section is the sentence 'Architecture was not "
        "named.' with no diagram and no code fence. If they gave no score, write "
        "not scored. Do not mention this check."
    )


def run() -> int:
    hits = 0
    for name, update, expected in CASES:
        answer = first_objection(update)
        choice = answer["choice"]
        confidence = answer["confidence"]
        ok = choice == expected
        hits += int(ok)
        mark = "ok" if ok else "MISS"
        print(f"{mark:<4} {confidence:4.2f}  {choice:<24}  expected {expected:<24}  {name}")
    print(f"\n{hits}/{len(CASES)}")
    return 0 if hits == len(CASES) else 1


if __name__ == "__main__":
    raise SystemExit(run())
