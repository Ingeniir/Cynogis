"""Teste le pont QGIS sans IA (clic droit > Run dans PyCharm)."""
import asyncio
import json

from cynogis_server.client import BridgeError, QgisBridgeClient


async def main() -> None:
    client = QgisBridgeClient()
    try:
        for method in ("ping", "get_project_info"):
            result = await client.call(method)
            print(f"✓ {method} :", json.dumps(result.data, indent=2, ensure_ascii=False))
            for w in result.warnings:
                print("  ⚠", w)
        tools = (await client.call("list_tools")).data["tools"]
        print("✓ Outils :", ", ".join(f"{t['name']} (N{t['level']})" for t in tools))
    except BridgeError as exc:
        print(f"✗ {exc}")


if __name__ == "__main__":
    asyncio.run(main())
