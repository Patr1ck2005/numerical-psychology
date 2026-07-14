#!/usr/bin/env python3
"""PreToolUse hook: block Read on image files for text-only models.

Reading an image file with the Read tool sends an image content block to the
API. On a text-only model this returns a 400 error and pollutes the context
for the rest of the session. This hook denies the Read before it fires when
the target file has an image extension.
"""
import json
import os
import sys

IMAGE_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp",
    ".svg", ".ico", ".tiff", ".tif",
}


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path", "")
    if not isinstance(file_path, str) or not file_path:
        sys.exit(0)

    _, ext = os.path.splitext(file_path)
    ext_lower = ext.lower()

    if ext_lower in IMAGE_EXTS:
        reason = (
            f"Blocked: Read on image file '{file_path}' ({ext_lower}). "
            f"Current model is text-only - reading images triggers 400 errors "
            f"and pollutes context. Alternatives: "
            f"(1) Bash `ls -la` / `file` for file metadata; "
            f"(2) `python -c \"from PIL import Image; im=Image.open(r'{file_path}'); print(im.size, im.mode)\"` for dimensions; "
            f"(3) ask the user to describe the image; "
            f"(4) for plot verification, print numerical stats (value range, "
            f"peak location via argmax, NaN ratio) instead of viewing. "
            f"See memory/feedback_no_image_read.md."
        )
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }
        print(json.dumps(output))
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
