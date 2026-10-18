from dataclasses import dataclass

@dataclass
class Action:
    name: str
    sensitive: bool = False

# A model may propose an action. It may not authorize itself.
def authorize(action, approved=False):
    return not action.sensitive or approved

plan = [Action("read_file"), Action("send_payment", sensitive=True)]

for step in plan:
    verdict = "run" if authorize(step) else "needs approval"
    print(step.name, "->", verdict)
