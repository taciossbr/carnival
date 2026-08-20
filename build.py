from pathlib import Path
import shutil
import subprocess
import sys
from html import escape


ROOT = Path(__file__).resolve().parent
TOOLS_DIR = ROOT / "tools"
DIST_DIR = ROOT / "dist"


def clean_dist():
    """Remove e recria o diretório global de distribuição."""
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

    DIST_DIR.mkdir(parents=True)


def build_simple_tool(tool_file: Path):
    """Copia uma tool HTML simples diretamente para dist/."""
    output = DIST_DIR / tool_file.name

    shutil.copy2(tool_file, output)

    return {
        "name": tool_file.stem,
        "file": output.name,
    }


def build_complex_tool(tool_dir: Path):
    """Executa o build da tool e copia o HTML gerado para dist/."""
    build_script = tool_dir / "build.py"

    if not build_script.exists():
        raise RuntimeError(
            f"Tool complexa '{tool_dir.name}' não possui build.py"
        )

    tool_dist = tool_dir / "dist"

    # Executa o build.py dentro do diretório da própria tool.
    subprocess.run(
        [sys.executable, str(build_script)],
        cwd=tool_dir,
        check=True,
    )

    output = tool_dist / "tool.html"

    if not output.exists():
        raise RuntimeError(
            f"O build de '{tool_dir.name}' não gerou {output}"
        )

    # O nome público é o nome do diretório da tool.
    final_output = DIST_DIR / f"{tool_dir.name}.html"

    shutil.copy2(output, final_output)

    return {
        "name": tool_dir.name,
        "file": final_output.name,
    }


def build_tools():
    """Encontra e processa todas as ferramentas."""
    tools = []

    for entry in sorted(TOOLS_DIR.iterdir(), key=lambda p: p.name.lower()):
        # Ignora arquivos/diretórios ocultos.
        if entry.name.startswith("."):
            continue

        # Tool simples: tools/foo.html
        if entry.is_file() and entry.suffix.lower() == ".html":
            tools.append(build_simple_tool(entry))

        # Tool complexa: tools/foo/
        elif entry.is_dir():
            tools.append(build_complex_tool(entry))

    return tools


def generate_index(tools):
    """Gera a página inicial com a lista de ferramentas."""
    items = "\n".join(
        f'        <li><a href="{escape(tool["file"])}">'
        f'{escape(tool["name"])}</a></li>'
        for tool in tools
    )

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tools</title>
</head>
<body>
    <h1>Tools</h1>

    <ul>
{items}
    </ul>
</body>
</html>
"""

    (DIST_DIR / "index.html").write_text(
        html,
        encoding="utf-8",
    )


def main():
    if not TOOLS_DIR.exists():
        raise RuntimeError(f"Diretório não encontrado: {TOOLS_DIR}")

    clean_dist()

    tools = build_tools()
    generate_index(tools)

    print(f"Build concluído: {len(tools)} tool(s)")
    print(f"Output: {DIST_DIR}")


if __name__ == "__main__":
    main()
