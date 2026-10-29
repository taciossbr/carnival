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


def build_simple_tool(tool_file: Path, relative_path: Path):
    """Copia uma tool HTML simples para dist/ mantendo a estrutura de subpastas."""
    # relative_path representa o caminho a partir de TOOLS_DIR
    target_dir = DIST_DIR / relative_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)
    
    output = target_dir / tool_file.name
    shutil.copy2(tool_file, output)

    # Caminho relativo para o link no index (ex: subpasta/tool.html)
    relative_file = relative_path.with_suffix(".html")

    return {
        "name": tool_file.stem,
        "file": str(relative_file).replace("\\", "/"),
    }


def build_complex_tool(tool_dir: Path, relative_path: Path):
    """Executa o build da tool complexa e copia o HTML gerado para dist/ mantendo as subpastas."""
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

    # Cria a estrutura correspondente em dist/
    target_dir = DIST_DIR / relative_path
    target_dir.mkdir(parents=True, exist_ok=True)

    # O arquivo final dentro da pasta de distribuição da tool
    final_output = target_dir / "tool.html"

    shutil.copy2(output, final_output)

    # Caminho relativo para o link no index (ex: subpasta/nome-da-tool/tool.html)
    relative_file = relative_path / "tool.html"

    return {
        "name": tool_dir.name,
        "file": str(relative_file).replace("\\", "/"),
    }


def process_directory(current_dir: Path):
    """Varre diretórios de forma recursiva buscando tools simples ou complexas."""
    tools = []

    for entry in sorted(current_dir.iterdir(), key=lambda p: p.name.lower()):
        # Ignora arquivos/diretórios ocultos
        if entry.name.startswith("."):
            continue

        relative_path = entry.relative_to(TOOLS_DIR)

        # Tool simples (.html)
        if entry.is_file() and entry.suffix.lower() == ".html":
            tools.append(build_simple_tool(entry, relative_path))

        # Diretório
        elif entry.is_dir():
            build_script = entry / "build.py"
            
            if build_script.exists():
                # É uma tool complexa (possui build.py)
                tools.append(build_complex_tool(entry, relative_path))
            else:
                # É apenas uma subpasta comum, entra nela recursivamente
                tools.extend(process_directory(entry))

    return tools


def build_tools():
    """Encontra e processa todas as ferramentas a partir da raiz de tools."""
    if not TOOLS_DIR.exists():
        return []
    return process_directory(TOOLS_DIR)


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
