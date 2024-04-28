from collections import Counter
import glob
import json
from typing import Any, TypedDict
import typo_checker
import numpy as np
import matplotlib.pyplot as plt

# define schema
class WordData(TypedDict):
    expected: str
    typed: str
    typos: dict[typo_checker.EditType, int]
class DeviceData(TypedDict):
    total: int
    incorrect: int
    words: list[WordData]
class ProcessedData(TypedDict):
    desktop: DeviceData
    mobile:  DeviceData

TYPO_DATA: ProcessedData = {
    "desktop": {
        "total": 0,
        "incorrect": 0,
        "words": []
    },
    "mobile": {
        "total": 0,
        "incorrect": 0,
        "words": []
    }
}

def process_json_word(json_word: Any) -> WordData:
    expected, typed = json_word["word"], json_word["input"]
    path = typo_checker.find_path(expected, typed) # see the changes to get from expected to what was typed
    typos = dict(Counter(node[0] for node in path))

    return {
        "expected": expected,
        "typed": typed,
        "typos": typos
    }

# read all files
for path in glob.glob("data/desktop-*"):
    with open(path) as f:
        obj = json.load(f)
        
        typoed_words = [pw for word in obj["words"] if len((pw := process_json_word(word))["typos"]) != 0]
        
        TYPO_DATA["desktop"]["total"] += len(obj["words"])
        TYPO_DATA["desktop"]["incorrect"] += len(typoed_words)
        TYPO_DATA["desktop"]["words"].extend(typoed_words)

for path in glob.glob("data/mobile-*"):
    with open(path) as f:
        obj = json.load(f)
        
        typoed_words = [pw for word in obj["words"] if len((pw := process_json_word(word))["typos"]) != 0]
        
        TYPO_DATA["mobile"]["total"] += len(obj["words"])
        TYPO_DATA["mobile"]["incorrect"] += len(typoed_words)
        TYPO_DATA["mobile"]["words"].extend(typoed_words)


# make stats!
for name, device_data in TYPO_DATA.items():
    print("Incorrectly typed words ({}): {}/{} = {:.03f}"
            .format(name,
                    device_data['incorrect'], 
                    device_data['total'], 
                    device_data['incorrect'] / device_data['total']
            )
    )
for name, device_data in TYPO_DATA.items():
    print("Number of typos ({}): {}"
            .format(
                name,
                sum(n for word in device_data['words'] for n in word["typos"].values())
            )
    )

# graphs!
def capitalize(s: str) -> str:
    return s[0].upper() + s[1:].lower() if len(s) != 0 else ""

typos: dict[str, Counter[typo_checker.EditType]] = {}
for name, device_data in TYPO_DATA.items():
    typos[name] = Counter()
    for word in device_data["words"]:
        typos[name].update(word["typos"])

label_map = {
    val: {
        "label": capitalize(name),
        "color": f"C{i}"
    } for i, (name, val) in enumerate(typo_checker.EditType.__members__.items())
}
## proportion of typos:
fig, axes = plt.subplots(len(typos))
for ((name, data), ax) in zip(typos.items(), axes):
    ax.pie(data.values(), labels=[label_map[k]["label"] for k in data.keys()], autopct='%1.1f%%', colors=[label_map[k]["color"] for k in data.keys()])
    ax.set_title(f"{capitalize(name)}")

fig.suptitle("Proportion of Typos between Devices")
fig.show()

## bar chart of typos:
fig, ax = plt.subplots(layout='constrained')

x = np.arange(len(typo_checker.EditType.__members__))
width = 0.25  # the width of the bars
multiplier = 0
n_bars = 2

for device, ctrs in typos.items():
    offset = width * multiplier
    rects = ax.bar(x + offset, [typos[device][k] for k in typo_checker.EditType.__members__.values()], width, label=capitalize(device))
    ax.bar_label(rects, padding=3)
    multiplier += 1

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Length (mm)')
ax.set_title('Typo occurrences by device')
ax.set_xticks(x + (n_bars - 1) * width / 2, [label_map[k]["label"] for k in typo_checker.EditType.__members__.values()])
ax.legend(loc='upper right', ncols=3)

plt.show()