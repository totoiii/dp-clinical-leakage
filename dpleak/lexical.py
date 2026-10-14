"""Lexical comparison of canary documents and source corpora (reviewer A.6): python -m dpleak.lexical"""
import json
import re
from collections import Counter
from pathlib import Path

from . import data

OUT = Path(__file__).resolve().parent.parent / "results"
TOPK = (50, 100)

# Stopwords mínimas embebidas: evita depender de nltk.
STOP = {
    "en": set("""a about above after again against all am an and any are as at be because been before
being below between both but by can could did do does doing down during each few for from further had
has have having he her here hers herself him himself his how i if in into is it its itself just me more
most my myself no nor not now of off on once only or other our ours out over own same she should so some
such than that the their theirs them themselves then there these they this those through to too under
until up very was we were what when where which while who whom why will with would you your yours
yourself also per may without within noted since patient pt""".split()),
    "es": set("""a al algo algunas algunos ante antes como con contra cual cuando de del desde donde durante
e el ella ellas ellos en entre era eran es esa esas ese eso esos esta estaba estado estan estar este esto
estos fue fueron ha habia han hasta hay la las le les lo los mas me mi muy nada ni no nos o otra otras otro
otros para pero poco por porque que quien se sea ser si sin sobre su sus tambien te tiene tienen todo
todos tu un una uno unos y ya paciente""".split()),
}
LANG = {"i2b2": "en", "meddocan": "es"}
TOKEN = re.compile(r"[a-záéíóúñü]{3,}")


def text_without_pii(xml_path):
    raw = xml_path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"<TEXT><!\[CDATA\[(.*?)\]\]></TEXT>", raw, re.S)
    body = m.group(1) if m else raw
    for span in re.findall(r'text="([^"]+)"', raw):
        body = body.replace(span, " ")
    return body


def pii_tokens(files):
    """Tokens de cualquier span PII: se excluyen aunque aparezcan sin anotar."""
    toks = set()
    for f in files:
        for span in re.findall(r'text="([^"]+)"', f.read_text(encoding="utf-8", errors="ignore")):
            toks.update(TOKEN.findall(span.lower()))
    return toks


def term_counts(files, lang):
    banned = STOP[lang] | pii_tokens(files)
    c = Counter()
    for f in files:
        c.update(t for t in TOKEN.findall(text_without_pii(f).lower()) if t not in banned)
    return c


def main():
    report = {}
    for ds, lang in LANG.items():
        base = data.DATA / ds
        canaries = sorted((data.CANARIES / ds).glob("*.xml"))
        corpus = sorted((base / "original").glob("*.xml"))
        cc, sc = term_counts(canaries, lang), term_counts(corpus, lang)
        report[ds] = {"n_canary_docs": len(canaries), "n_corpus_docs": len(corpus)}
        for k in TOPK:
            a = [t for t, _ in cc.most_common(k)]
            b = [t for t, _ in sc.most_common(k)]
            inter = set(a) & set(b)
            report[ds][f"top{k}"] = {
                "overlap": len(inter),
                "overlap_pct": round(100 * len(inter) / k, 1),
                "jaccard": round(len(inter) / len(set(a) | set(b)), 3),
                "only_canary": [t for t in a if t not in inter],
                "only_corpus": [t for t in b if t not in inter],
                "canary_top": a,
                "corpus_top": b,
            }
            print(f"{ds} top{k}: solapamiento {len(inter)}/{k} ({100*len(inter)/k:.0f}%)")
        print(f"   solo canarios : {report[ds]['top50']['only_canary'][:20]}")
        print(f"   solo corpus   : {report[ds]['top50']['only_corpus'][:20]}")
    OUT.mkdir(exist_ok=True)
    (OUT / "a6_lexical_check.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"-> {OUT / 'a6_lexical_check.json'}")


if __name__ == "__main__":
    main()
