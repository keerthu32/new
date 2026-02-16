#!/usr/bin/env python3
import json
import os
import random
import sys


def classify_from_filename(image_path: str) -> str:
    name = os.path.basename(image_path).lower()

    keyword_map = {
        "buzz": "buzz_cut",
        "crew": "crew_cut",
        "side": "side_part",
        "pomp": "pompadour",
        "long": "long_wavy",
        "wavy": "long_wavy",
    }

    for key, value in keyword_map.items():
        if key in name:
            return value

    return random.choice(["buzz_cut", "crew_cut", "side_part", "pompadour", "long_wavy"])


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Image path argument is required."}))
        sys.exit(1)

    image_path = sys.argv[1]
    hairstyle = classify_from_filename(image_path)
    print(json.dumps({"hairstyle": hairstyle}))


if __name__ == "__main__":
    main()
