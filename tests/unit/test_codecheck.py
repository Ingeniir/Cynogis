from cynogis.core.codecheck import risky_names


def test_repere_modules_et_appels_sensibles():
    code = ("import os.path\nfrom shutil import rmtree\nlayer.deleteFeatures([1])\n"
            "open('f', 'w')\nproject.removeMapLayer(lid)\n")
    assert risky_names(code) == ["deleteFeatures", "open", "os", "removeMapLayer", "shutil"]


def test_code_anodin_ou_invalide():
    assert risky_names("result = [l.name() for l in project.mapLayers().values()]") == []
    assert risky_names("def (") == []
