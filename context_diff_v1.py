
import json, re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional
from difflib import SequenceMatcher
from pathlib import Path

# ----------------------------- Token & helpers -----------------------------
@dataclass
class Token:
    text: str
    kind: str
    norm: str
    conf: float
    bbox: Optional[Tuple[float, float, float, float]]
    page: Optional[int]
    block_id: str
    line_idx: int
    col_idx: int

def _normalize_for_align(s: str) -> str:
    s = s.replace('—','-').replace('–','-')
    s = s.replace('“','"').replace('”','"').replace('’',"'")
    s = re.sub(r'\s+', ' ', s).strip().lower()
    s = s.replace('\u200b','')
    return s

CURRENCY = {'$', 'usd', 'eur', '€', '£', 'inr', '¥'}
UNITS = {'kg','g','mg','lb','oz','m','cm','mm','km','°c','°f','%','hrs','hr','min','s','l','ml'}
NEGATIONS = {'no','not','without','except','unless'}
MODALS = {'shall','must','may','should','warranty','guarantee'}
COMPARATORS = {'<','≤','=','≥','>','<=','>=','≦','≧'}

_num_re = re.compile(r'^\d{1,4}(?:([,\.\s])\d{3})*(?:\.\d+)?$')
_date_re = re.compile(r'^(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{4}[-\/]\d{2}[-\/]\d{2}|[a-zA-Z]{3,9}\s+\d{1,2},?\s+\d{2,4})$')
_id_re = re.compile(r'^[A-Za-z]{0,3}\d{5,}[-\dA-Za-z]*$')
_punct_re = re.compile(r'^[\.,;:(){}\[\]\-–—"\'`•·…]$')


def _classify_token(tok: str) -> str:
    t = tok.strip(); tl = t.lower()
    if tl in COMPARATORS: return 'comp'
    if tl in NEGATIONS: return 'negation'
    if tl in MODALS: return 'modal'
    if tl in CURRENCY: return 'currency'
    if tl in UNITS: return 'unit'
    if _num_re.match(tl): return 'number'
    if _date_re.match(t): return 'date'
    if _id_re.match(t): return 'id'
    if _punct_re.match(t): return 'punct'
    return 'word'

_word_or_sym_re = re.compile(r'\w+|[^\w\s]', re.UNICODE)

def _tokenize_line(line_text: str, meta: Dict[str, Any]) -> List[Token]:
    toks = _word_or_sym_re.findall(line_text)
    out: List[Token] = []
    for j, tok in enumerate(toks):
        out.append(Token(
            text=tok,
            kind=_classify_token(tok),
            norm=_normalize_for_align(tok),
            conf=float(meta.get('confidence', meta.get('conf', 1.0)) or 1.0),
            bbox=tuple(meta.get('bbox')) if isinstance(meta.get('bbox'), (list, tuple)) and len(meta.get('bbox'))==4 else None,
            page=int(meta.get('page')) if str(meta.get('page') or '').isdigit() else None,
            block_id=str(meta.get('block_id') or meta.get('block', '') or ''),
            line_idx=int(meta.get('line_idx')) if str(meta.get('line_idx') or '').isdigit() else int(meta.get('line', meta.get('index', 0)) or 0),
            col_idx=j
        ))
    return out

# ----------------------------- JSON line extractor -----------------------------
def _collect_lines(node: Any, acc: List[Dict[str, Any]], path: List[Any] = None):
    if path is None: path = []
    if isinstance(node, dict):
        if any(k in node for k in ('text','line','content')) and isinstance(node.get('text', node.get('line', node.get('content', ''))), str):
            txt = node.get('text') or node.get('line') or node.get('content') or ''
            meta = {k: v for k, v in node.items() if k not in ('text','line','content')}
            meta['_path'] = '/'.join(map(str, path))
            acc.append({'text': txt, 'meta': meta})
        for k, v in node.items():
            _collect_lines(v, acc, path + [k])
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _collect_lines(v, acc, path + [i])

def extract_lines(json_obj: Any) -> List[Dict[str, Any]]:
    acc: List[Dict[str, Any]] = []
    _collect_lines(json_obj, acc, [])
    if not acc and isinstance(json_obj, str):
        acc = [{'text': json_obj, 'meta': {}}]
    for i, ln in enumerate(acc):
        ln['meta'].setdefault('line_idx', i)
    return acc

# ----------------------------- Alignment -----------------------------
def align_token_sequences(a: List[Token], b: List[Token]) -> List[Tuple[str, Optional[Token], Optional[Token]]]:
    a_norm = [t.norm for t in a]
    b_norm = [t.norm for t in b]
    sm = SequenceMatcher(a=a_norm, b=b_norm, autojunk=False)
    ops: List[Tuple[str, Optional[Token], Optional[Token]]] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for i, j in zip(range(i1, i2), range(j1, j2)):
                ops.append(('match', a[i], b[j]))
        elif tag == 'replace':
            n = min(i2-i1, j2-j1)
            for k in range(n):
                ops.append(('sub', a[i1+k], b[j1+k]))
            for i in range(i1+n, i2):
                ops.append(('del', a[i], None))
            for j in range(j1+n, j2):
                ops.append(('ins', None, b[j]))
        elif tag == 'delete':
            for i in range(i1, i2):
                ops.append(('del', a[i], None))
        elif tag == 'insert':
            for j in range(j1, j2):
                ops.append(('ins', None, b[j]))
    return ops

# ----------------------------- Severity Scoring -----------------------------
def _category_impact(kind_a: str, kind_b: str) -> float:
    k = kind_a if kind_a not in ('∅','word') else kind_b
    critical = {'currency','number','date','unit','comp','negation','id'}
    medium   = {'modal','ref','proper'}
    if k in critical: return 1.0
    if k in medium: return 0.5
    return 0.1

def _number_value(tok: Token) -> Optional[float]:
    try:
        s = tok.text.replace(',', '').replace(' ', '')
        return float(s)
    except Exception:
        return None

def _magnitude(a_tok: Optional[Token], b_tok: Optional[Token]) -> float:
    if a_tok and b_tok and (a_tok.kind=='number' or b_tok.kind=='number'):
        a = _number_value(a_tok); b = _number_value(b_tok)
        if a is not None and b is not None:
            if abs(a) < 1e-9: return 1.0 if abs(b) > 1e-9 else 0.0
            return min(1.0, abs(a-b)/max(1.0, abs(a)))
    return 0.0

def _rule_bump(a_tok: Optional[Token], b_tok: Optional[Token]) -> float:
    if (a_tok and a_tok.kind=='negation') ^ (b_tok and b_tok.kind=='negation'): return 1.0
    if (a_tok and a_tok.kind=='unit') ^ (b_tok and b_tok.kind=='unit'): return 0.7
    if (a_tok and a_tok.kind=='comp') ^ (b_tok and b_tok.kind=='comp'): return 0.8
    if a_tok and b_tok and a_tok.kind=='number' and b_tok.kind=='number':
        if ('.' in a_tok.text) ^ ('.' in b_tok.text): return 0.8
        if re.fullmatch(r'\d+0+', a_tok.text) or re.fullmatch(r'\d+0+', b_tok.text): return 0.6
    return 0.0

def _position_weight(meta: Dict[str, Any]) -> float:
    path = meta.get('_path',''); line_idx = int(meta.get('line_idx', 0) or 0)
    boost = 0.0
    if re.search(r'total|amount|balance|fee|price|payment|due|subtotal|grand', path, re.I): boost += 0.5
    if re.search(r'signature|authorized|terms|effective|date', path, re.I): boost += 0.4
    if line_idx < 10: boost += 0.1
    return min(1.0, max(0.0, boost))

def _explain(a_tok: Optional[Token], b_tok: Optional[Token]) -> str:
    if (a_tok and a_tok.kind=='negation') ^ (b_tok and b_tok.kind=='negation'): return "Negation term added/removed; obligation may invert."
    if (a_tok and a_tok.kind=='number') or (b_tok and b_tok.kind=='number'): return "Numeric value changed; verify totals/limits/quantities."
    if (a_tok and a_tok.kind=='unit') ^ (b_tok and b_tok.kind=='unit'): return "Unit changed; check scale and safety implications."
    if (a_tok and a_tok.kind=='date') or (b_tok and b_tok.kind=='date'): return "Date changed; deadlines/effective periods may shift."
    if (a_tok and a_tok.kind=='comp') ^ (b_tok and b_tok.kind=='comp'): return "Comparator changed; threshold semantics altered."
    if (a_tok and a_tok.kind=='punct') or (b_tok and b_tok.kind=='punct'): return "Punctuation change; usually low impact unless disambiguating numbers."
    return "Lexical change; review in surrounding context."

def _severity(a_tok: Optional[Token], b_tok: Optional[Token], meta_a: Dict[str, Any], meta_b: Dict[str, Any]) -> float:
    kind_a = a_tok.kind if a_tok else '∅'; kind_b = b_tok.kind if b_tok else '∅'
    ic = _category_impact(kind_a, kind_b); mag = _magnitude(a_tok, b_tok)
    conf = min((a_tok.conf if a_tok else 1.0), (b_tok.conf if b_tok else 1.0))
    U = 1.0 - 0.5*(1.0 - conf)
    pos_weight = max(_position_weight(meta_a), _position_weight(meta_b))
    rb = _rule_bump(a_tok, b_tok)
    s = ic*0.5 + mag*0.3 + pos_weight*0.1 + rb*0.1
    return max(0.0, min(1.0, s*U))

# ----------------------------- Orchestration -----------------------------
def _align_lines_by_text(a_lines: List[Dict[str, Any]], b_lines: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
    a_norm = [_normalize_for_align(x['text']) for x in a_lines]
    b_norm = [_normalize_for_align(x['text']) for x in b_lines]
    sm = SequenceMatcher(a=a_norm, b=b_norm, autojunk=False)
    pairs: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for i, j in zip(range(i1, i2), range(j1, j2)):
                pairs.append((a_lines[i], b_lines[j]))
        elif tag == 'replace':
            n = min(i2-i1, j2-j1)
            for k in range(n):
                pairs.append((a_lines[i1+k], b_lines[j1+k]))
        elif tag == 'delete':
            for i in range(i1, i2):
                pairs.append((a_lines[i], {'text':'', 'meta':{'line_idx':-1}}))
        elif tag == 'insert':
            for j in range(j1, j2):
                pairs.append(({'text':'', 'meta':{'line_idx':-1}}, b_lines[j]))
    return pairs

def context_diff(docA: Dict[str, Any], docB: Dict[str, Any], pair_id: str = "run") -> Dict[str, Any]:
    a_lines = extract_lines(docA); b_lines = extract_lines(docB)
    aligned_lines = _align_lines_by_text(a_lines, b_lines)
    diffs: List[Dict[str, Any]] = []; summary = {'critical': 0, 'medium': 0, 'low': 0}
    for a_ln, b_ln in aligned_lines:
        a_toks = _tokenize_line(a_ln['text'], a_ln['meta']); b_toks = _tokenize_line(b_ln['text'], b_ln['meta'])
        ops = align_token_sequences(a_toks, b_toks)
        for op, at, bt in ops:
            if op == 'match': continue
            sev = _severity(at, bt, a_ln['meta'], b_ln['meta'])
            bucket = 'low' if sev < 0.2 else ('medium' if sev < 0.6 else 'critical')
            summary[bucket] += 1
            diffs.append({
                "id": f"d_{len(diffs):05d}",
                "op": op,
                "level": "token",
                "page": at.page if at else (bt.page if bt else None),
                "block_label": a_ln['meta'].get('block_id') or b_ln['meta'].get('block_id') or "",
                "line_index": a_ln['meta'].get('line_idx', None),
                "bbox": at.bbox if at else (bt.bbox if bt else None),
                "lhs": at.text if at else "",
                "rhs": bt.text if bt else "",
                "lhs_kind": at.kind if at else "∅",
                "rhs_kind": bt.kind if bt else "∅",
                "severity": round(sev, 3),
                "severity_bucket": bucket,
                "why_it_matters": _explain(at, bt),
                "suggested_action": "Manual review" if bucket != 'low' else "Low impact; accept or ignore",
            })
    return {"document_pair_id": pair_id, "summary": summary, "totals": {"diffs": len(diffs)}, "diffs": diffs}

def context_diff_from_files(lhs_path: str, rhs_path: str, pair_id: str = "run") -> Dict[str, Any]:
    with open(lhs_path, "r", encoding="utf-8") as f: A = json.load(f)
    with open(rhs_path, "r", encoding="utf-8") as f: B = json.load(f)
    return context_diff(A, B, pair_id=pair_id)

# ----------------------------- Simple local runner (edit paths) -----------------------------
if __name__ == "__main__":
    FILE_A = "run_5.json"     # <- edit to your file path
    FILE_B = "run_10.json"    # <- edit to your file path
    OUTPUT = "report.json"   # <- edit to desired output path

    report = context_diff_from_files(FILE_A, FILE_B, pair_id="run_vs_code")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    Path(OUTPUT).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved report to: {OUTPUT}")
