from cynogis.core.privacy import MASK, mask_sensitive


def test_mask_sensitive_hides_only_sensitive_values():
    attrs = {"proprietaire": "DUPONT Jean", "ddenom": "MARTIN", "code_habitat": "G1.1",
             "surface": 12.5}
    assert mask_sensitive(attrs) == {"proprietaire": MASK, "ddenom": MASK,
                                     "code_habitat": "G1.1", "surface": 12.5}
    assert attrs["proprietaire"] == "DUPONT Jean"  # entrée non modifiée
