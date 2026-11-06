from cynogis.core.codecheck import blocking_calls, risky_names


def test_repere_modules_et_appels_sensibles():
    code = ("import os.path\nfrom shutil import rmtree\nlayer.deleteFeatures([1])\n"
            "open('f', 'w')\nproject.removeMapLayer(lid)\n")
    assert risky_names(code) == ["deleteFeatures", "open", "os", "removeMapLayer", "shutil"]


def test_code_anodin_ou_invalide():
    assert risky_names("result = [l.name() for l in project.mapLayers().values()]") == []
    assert risky_names("def (") == []


def test_appels_bloquants():
    code = ("processing.run('native:buffer', {})\ntime.sleep(1)\nrequests.get(u)\n"
            "layer.run()\nd.get('k')\n")
    assert blocking_calls(code) == ["processing.run", "requests.get", "time.sleep"]
    assert blocking_calls("res = yield from run_algorithm('native:buffer', {})") == []
