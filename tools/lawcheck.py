# -*- coding: utf-8 -*-
"""카드가 인용한 조문이 실재하는지, 그 조문에 그 숫자가 있는지 대조한다.

   이 게임은 시험 공부 도구다. 그러면 조문 번호도 답이므로, 틀린 번호는 틀린 값과
   같다. 실제로 한 번 훑었더니 서른 장에서 인용이 어긋나 있었고 그중 여덟 장은
   법령에 아예 없는 수치를 규칙 조문으로 제시하고 있었다 — 2019·2022·2023년
   개정으로 삭제된 값이거나 고시·지침 값을 규칙인 양 적은 것이었다.
   사람이 다시 그러지 않도록 기계에 맡긴다.

   대조 원본: ../sanup-safety-cbt/build/_laws.json (법제처 조문 전문)
   그 파일이 없으면 조용히 건너뛴다 — 저장소가 둘로 나뉘어 있어서다.

   두 가지를 본다.

   ① 인용한 조문이 실재하는가.        없으면 FAIL.
   ② f 필드의 <em>값</em>이 그 조문에 있는가.
      없으면 WARN 이다 — 별표·고시·KS 에 있는 값일 수 있고, 그런 값은 law 필드에
      출처를 따로 적기로 했다. 그래서 law 에 「고시」·「별표」·「지침」·「KS」·
      「GUIDE」 같은 말이 있으면 그 카드의 숫자는 묻지 않는다.

   ② 는 다 잡히지 않는다. 조문이 표(그림 파일)로 값을 담은 곳 — 충전전로
   접근한계거리표(제321조제1항제8호) 같은 데 — 은 본문에 숫자가 없어서 늘 걸린다.
   단위 자릿수가 다른 것(조문 「300센티미터」 대 카드 「3 m」)도 걸린다.
   그래서 ② 는 종료코드를 올리지 않는다. **눈으로 보라는 목록**이다.

   쓰기: python tools/lawcheck.py [reigns.html]
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LAWS = os.path.join(ROOT, os.pardir, "sanup-safety-cbt", "build", "_laws.json")

# law 필드에 이 말이 있으면 그 카드의 숫자는 규칙 밖에서 온 것이다
OUTSIDE = ("고시", "별표", "지침", "KS", "GUIDE", "CODE", "표준")

# 규칙 조문은 「센티미터」로 적고 카드는 「cm」로 적는다. 대조하려면 맞춰야 한다.
UNITS = [
    ("센티미터", "cm"), ("밀리미터", "mm"), ("킬로미터", "km"), ("미터", "m"),
    ("킬로그램", "kg"), ("그램", "g"), ("퍼센트", "%"), ("리터", "L"),
    ("밀리암페어", "mA"), ("암페어", "A"), ("킬로볼트", "kV"), ("볼트", "V"),
    ("옴", "Ω"), ("럭스", "lux"), ("톤", "t"), ("킬로와트", "kW"),
    ("피피엠", "ppm"), ("세제곱미터", "m3"), ("제곱미터", "m2"),
    ("데시벨", "dB"), ("시간당", ""), ("매시", ""), ("도", "°"),
]
NUMWORD = {"하나": "1", "둘": "2", "셋": "3", "넷": "4", "다섯": "5",
           "여섯": "6", "일곱": "7", "여덟": "8", "아홉": "9", "열": "10"}


def norm(s):
    """조문 문장과 카드 문구를 같은 자리에서 만나게 한다."""
    for ko, en in UNITS:
        s = s.replace(ko, en)
    for ko, num in NUMWORD.items():
        s = s.replace(ko, num)
    s = s.replace("％", "%").replace("㎡", "m3").replace("㎝", "cm3")
    s = re.sub(r"[\s·・,]", "", s)
    return s


def load_laws():
    if not os.path.exists(LAWS):
        return None
    d = json.load(io.open(LAWS, encoding="utf-8"))
    out = {}
    for key, law in d.items():
        arts = {}
        for a in law.get("arts", []):
            no = a.get("no", "")
            br = a.get("branch", "")
            if not no:
                continue
            k = no + ("의" + br if br else "")
            arts[k] = arts.get(k, "") + "\n" + a.get("text", "")
        out[key] = {"name": law.get("name", key), "eff": law.get("eff", ""), "arts": arts}
    return out


# 카드 하나를 통째로 잡아 k · law · f 를 꺼낸다
CARD = re.compile(r"\{k:'([^']+)',(.*?)\n(?=  \{k:'|  \];|  \];)", re.S)
LAWF = re.compile(r"law:'([^']*)'")
FF = re.compile(r"\bf:'((?:[^'\\]|\\.)*)'")
EM = re.compile(r"<em>(.*?)</em>")
# 「제339조제1항」·「제332조의2제1호」·「제14조 ②」를 다 잡는다
ART = re.compile(r"제\s*(\d+)\s*조(?:의\s*(\d+))?")


# law 필드가 가리키는 법령을 고른다. 긴 이름부터 봐야 「시행규칙」이
# 「규칙」에 먹히지 않는다.
BOOKS = [
    ("산업안전보건기준에 관한 규칙", "안전보건규칙"),
    ("산업안전보건법 시행규칙", "시행규칙"),
    ("산업안전보건법 시행령", "시행령"),
    ("중대재해 처벌 등에 관한 법률", "중대재해처벌법"),
    ("중대재해처벌법", "중대재해처벌법"),
    ("산업안전보건법", "산업안전보건법"),
]


def which(law, laws):
    for label, key in BOOKS:
        if law.startswith(label) or ("· " + label) in law:
            return laws.get(key)
    # 「규칙 제311조」처럼 줄여 쓴 것은 안전보건규칙으로 본다
    if law.startswith("규칙 제") or " 규칙 제" in law:
        return laws.get("안전보건규칙")
    return None


def cards(src):
    body = src[src.index("var DECK = ["):]
    body = body[:body.index("\n  ];")]
    for m in re.finditer(r"^  \{k:'([^']+)',", body, re.M):
        start = m.start()
        nxt = body.find("\n  {k:'", start + 1)
        chunk = body[start:nxt if nxt > 0 else len(body)]
        yield m.group(1), chunk


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "reigns.html")
    src = io.open(path, encoding="utf-8").read()
    laws = load_laws()
    if laws is None:
        print("법령 원문(%s)이 없어 건너뜁니다." % os.path.normpath(LAWS))
        print("이 검사는 sanup-safety-cbt 저장소가 나란히 있을 때만 돕니다.")
        return 0

    rule = laws.get("안전보건규칙")
    print("대조 원본: %s 시행 %s · 조문 %d개"
          % (rule["name"], rule["eff"], len(rule["arts"])))

    missing, unmatched, checked, skipped = [], [], 0, 0
    for key, chunk in cards(src):
        lm = LAWF.search(chunk)
        if not lm or not lm.group(1):
            continue
        law = lm.group(1)
        book = which(law, laws)
        if book is None:
            continue          # 우리가 원문을 갖고 있지 않은 법령
        # 인용한 조문이 실재하는가
        refs = []
        for a in ART.finditer(law):
            refs.append(a.group(1) + ("의" + a.group(2) if a.group(2) else ""))
        if not refs:
            continue
        checked += 1
        text = ""
        for r in refs:
            if r not in book["arts"]:
                missing.append((key, r, law))
            else:
                text += book["arts"][r]
        if not text:
            continue
        # 숫자가 그 조문에 있는가. 밖에서 온 값이라고 적어 두었으면 묻지 않는다.
        if any(w in law for w in OUTSIDE):
            skipped += 1
            continue
        fm = FF.search(chunk)
        if not fm:
            continue
        ntext = norm(text)
        for em in EM.findall(fm.group(1)):
            val = em.strip()
            if not re.search(r"\d", val):
                continue          # 숫자가 없는 강조는 대조 대상이 아니다
            nv = norm(val)
            # 「38~60 도」 같은 구간은 조문에서 「38도 이상 60도 이하」로 풀어 쓴다.
            # 양 끝을 따로 찾는다.
            m2 = re.match(r"([\d.,]+)~([\d.,]+)\s*([A-Za-z%°Ω]*)", nv)
            if m2:
                unit = m2.group(3)
                probes = [m2.group(1) + unit, m2.group(2) + unit]
            else:
                # 「16 cm 미만」처럼 꼬리말이 붙은 것은 숫자+단위까지만 본다
                core = re.match(r"([\d.,]+)([A-Za-z%°Ω]*)", nv)
                probes = [core.group(0)] if core else [nv]
            if any(p and p not in ntext for p in probes):
                unmatched.append((key, val, ",".join(refs)))

    print("")
    print("규칙을 인용한 카드 %d장 검사 · 출처를 밖으로 적어 둔 카드 %d장은 숫자 대조 제외"
          % (checked, skipped))
    print("")
    if missing:
        print("없는 조문을 인용한 곳: %d건" % len(missing))
        for k, r, law in missing:
            print("  %-12s 제%s조 — %s" % (k, r, law))
    else:
        print("없는 조문을 인용한 곳: 0건")
    print("")
    if unmatched:
        print("조문에서 못 찾은 값: %d건 (별표·고시 값이면 law 필드에 출처를 적으세요)" % len(unmatched))
        for k, v, r in unmatched:
            print("  %-12s %-22s 제%s조" % (k, v, r))
    else:
        print("조문에서 못 찾은 값: 0건")

    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
