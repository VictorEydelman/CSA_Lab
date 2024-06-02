import sys

from isa import Opcode, write_code

start = 0


def translate_stage(text):
    labels = {}
    code = []
    for num, line in enumerate(text.splitlines()):
        token = line.split(";", 1)[0].strip()
        if token == "":
            continue
        if token.endswith(":"):
            assert token.strip(":") not in labels, "{}".format(token.strip(":"))
            labels[token.strip(":")] = len(code) + 4
            if token.strip(":") == "_start":
                global start
                start = len(code) + 4
        elif " " in token:
            sub_token = token.split(" ")
            assert len(sub_token) == 2, "{}".format(token)
            mnemonic, arg = sub_token
            opcode = Opcode(mnemonic)
            code.append({"index": len(code) + 4, "opcode": opcode, "arg": arg})
        else:
            opcode = Opcode(token)
            code.append({"index": len(code) + 4, "opcode": opcode, "arg": ""})
    return labels, code


def translate_stage2(labels, code):
    for instruction in code:
        if instruction["arg"] in labels:
            label = instruction["arg"]
            instruction["arg"] = labels[label]
    code.insert(0, {"_start": start})
    return code


def translate(text):
    labels, code = translate_stage(text)
    return translate_stage2(labels, code)


def main(source, target):
    with open(source, encoding="utf-8") as f:
        source = f.read()
    code = translate(source)
    write_code(target, code)


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: translator_asm.py <input_file> <target_file>"
    _, sourse, target = sys.argv
    main(sourse, target)
