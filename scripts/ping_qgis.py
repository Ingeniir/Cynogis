"""Teste le pont QGIS sans IA. À lancer depuis PyCharm (clic droit > Run)."""
import asyncio
import json
import sys

from cynogis_server.client import BridgeError, QgisBridgeClient


async def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # console Windows cp1252 : ✓/✗
    client = QgisBridgeClient()
    for method in ("ping", "get_project_info"):
        try:
            result = await client.call(method)
            print(f"✓ {method} :", json.dumps(result.data, indent=2, ensure_ascii=False))
        except BridgeError as exc:
            print(f"✗ {method} : {exc}")


if __name__ == "__main__":
    asyncio.run(main())
