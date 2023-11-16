
import z3

def formula_from_text(text):
    text = fix_transcendental_decl_for_z3(text)
    formula = z3.parse_smt2_string(text)
    if isinstance(formula, z3.z3.AstVector): 
        formula = z3.And(formula)
    if not isinstance(formula, z3.z3.BoolRef):
        raise TypeError(f"Type {type(formula)} not supported")
    return formula




def fix_transcendental_decl_for_z3(text):
    #print(f"\noriginal text: {text}")
    if "(exp " in text and not "(declare-fun exp " in text:
        text = text.replace(
            "(declare-fun", "(declare-fun exp (Real) Real)\n(declare-fun", 1)

    if "(log " in text and not "(declare-fun log " in text:
        text = text.replace(
            "(declare-fun", "(declare-fun log (Real) Real)\n(declare-fun", 1)

    if "(arcsin " in text and not "(declare-fun arcsin " in text or "(asin " in text and not "(declare-fun asin " in text:
        text = text.replace(
            "(declare-fun", "(declare-fun asin (Real) Real)\n(declare-fun", 1)

    if "(arccos " in text and not "(declare-fun arccos " in text or "(acos " in text and not "(declare-fun acos " in text:
        text = text.replace(
            "(declare-fun", "(declare-fun acos (Real) Real)\n(declare-fun", 1)

    if "(arctan " in text and not "(declare-fun arctan " in text or "(atan " in text and not "(declare-fun atan " in text:
        text = text.replace(
            "(declare-fun", "(declare-fun atan (Real) Real)\n(declare-fun", 1)

    if "(arctan2 " in text and not "(declare-fun arctan2 " in text or "(atan2 " in text and not "(declare-fun atan2 " in text:
        text = text.replace(
            "(declare-fun", "(declare-fun atan2 (Real Real) Real)\n(declare-fun", 1)

    if "(power " in text:
        text = text.replace("(power ", "(pow ")

    if "pow " in text and not "(declare-fun pow " in text:
        text = text.replace(
            "(declare-fun", "(declare-fun pow (Real Real) Real)\n(declare-fun", 1)

    if "(^ " in text or " ^ " in text and not "(declare-fun ^" in text:
        text = text.replace(
            "(declare-fun", "(declare-fun pow (Real Real) Real)\n(declare-fun", 1)
        text = text.replace("^", "power")

    if "(sin" in text and not "(declare-fun sin" in text:
        text = text.replace(
            "(declare-fun", "(declare-fun sin (Real) Real)\n(declare-fun", 1)

    if "(cos" in text and not "(declare-fun cos" in text:
        text = text.replace(
            "(declare-fun", "(declare-fun cos (Real) Real)\n(declare-fun", 1)

    if "(tan" in text and not "(declare-fun tan" in text:
        text = text.replace(
            "(declare-fun", "(declare-fun tan (Real) Real)\n(declare-fun", 1)

    if "(tanh" in text and not "(declare-fun tanh" in text:
        text = text.replace(
            "(declare-fun", "(declare-fun tanh (Real) Real)\n(declare-fun", 1)

    if ("(pi" in text or "pi)" in text or " pi " in text) and not "(declare-fun pi" in text:
        text = text.replace(
            "(declare-fun", "(declare-fun pi () Real)\n(declare-fun", 1)

    text = text.replace("power", "pow")
    #print(f"\nfixed text: {text}")

    return text


def list_of_transcendental_functions():
    return ["pi", "exp", "log",  "power",
            "arcsin", "arccos", "arctan", "arctan2",
            "sin", "cos", "tan", "tanh"]
