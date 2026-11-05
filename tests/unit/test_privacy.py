from cynogis.core.privacy import MASK, mask_sensitive, sensitive_fields


def test_mask_sensitive_hides_only_sensitive_values():
    attrs = {"proprietaire": "DUPONT Jean", "ddenom": "MARTIN", "code_habitat": "G1.1",
             "surface": 12.5}
    assert mask_sensitive(attrs) == {"proprietaire": MASK, "ddenom": MASK,
                                     "code_habitat": "G1.1", "surface": 12.5}
    assert attrs["proprietaire"] == "DUPONT Jean"  # entrée non modifiée


def test_sensitive_fields_in_filter_columns():
    assert sensitive_fields(["code_habitat", "ddenom", "Propriétaire", "ddenom"]) == [
        "ddenom", "Propriétaire"]
    assert sensitive_fields(["surface", "code_habitat"]) == []
