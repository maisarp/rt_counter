"""
Gerenciamento centralizado de caminhos da aplicação.

Este módulo define onde os arquivos de dados e configuração são armazenados,
seguindo as melhores práticas para aplicações desktop (AppData no Windows).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def get_app_data_dir() -> Path:
    """
    Retorna o diretório de dados da aplicação.
    
    No Windows: C:\\Users\\{usuario}\\AppData\\Local\\RetweetCounter\\
    No Linux: ~/.local/share/RetweetCounter/
    No macOS: ~/Library/Application Support/RetweetCounter/
    
    Returns:
        Path: Caminho para o diretório de dados da aplicação.
    """
    app_name = "RetweetCounter"
    
    if sys.platform == "win32":
        # Windows: usa LOCALAPPDATA
        base_path = os.environ.get("LOCALAPPDATA")
        if not base_path:
            base_path = Path.home() / "AppData" / "Local"
        else:
            base_path = Path(base_path)
    elif sys.platform == "darwin":
        # macOS: usa Application Support
        base_path = Path.home() / "Library" / "Application Support"
    else:
        # Linux e outros: usa XDG_DATA_HOME ou ~/.local/share
        xdg_data = os.environ.get("XDG_DATA_HOME")
        if xdg_data:
            base_path = Path(xdg_data)
        else:
            base_path = Path.home() / ".local" / "share"
    
    app_dir = base_path / app_name
    return app_dir


def ensure_app_data_dir() -> Path:
    """
    Garante que o diretório de dados da aplicação existe.
    
    Returns:
        Path: Caminho para o diretório de dados (criado se não existir).
    """
    app_dir = get_app_data_dir()
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_data_file_path(filename: str) -> Path:
    """
    Retorna o caminho completo para um arquivo de dados.
    
    Args:
        filename: Nome do arquivo (ex: 'contador_retweets.csv').
    
    Returns:
        Path: Caminho completo para o arquivo dentro do diretório de dados.
    """
    return ensure_app_data_dir() / filename


def get_default_paths() -> dict[str, Path]:
    """
    Retorna todos os caminhos padrão da aplicação.
    
    Returns:
        dict: Dicionário com os caminhos para cada arquivo.
    """
    app_dir = ensure_app_data_dir()
    
    return {
        "data_dir": app_dir,
        "data_file": app_dir / "contador_retweets.csv",
        "config_file": app_dir / "contador_config.json",
        "targets_file": app_dir / "weekly_targets.json",
        "week_config_file": app_dir / "weekly_config.json",
        "view_csv": app_dir / "contador_retweets_view.csv",
        "view_xlsx": app_dir / "contador_retweets_view.xlsx",
        "view_html": app_dir / "contador_retweets_view.html",
    }


def migrate_legacy_files(legacy_dir: Path) -> bool:
    """
    Migra arquivos de uma instalação antiga para o novo diretório.
    
    Verifica se existem arquivos de dados no diretório legado
    e os copia para o novo local (AppData).
    
    Args:
        legacy_dir: Diretório onde a aplicação era executada anteriormente.
    
    Returns:
        bool: True se migrou algum arquivo, False caso contrário.
    """
    import shutil
    
    legacy_files = [
        "contador_retweets.csv",
        "contador_config.json",
        "weekly_targets.json",
        "weekly_config.json",
    ]
    
    app_dir = ensure_app_data_dir()
    migrated = False
    
    for filename in legacy_files:
        legacy_path = legacy_dir / filename
        new_path = app_dir / filename
        
        # Só migra se o arquivo legado existe e o novo não existe
        if legacy_path.exists() and not new_path.exists():
            try:
                shutil.copy2(legacy_path, new_path)
                migrated = True
            except (OSError, shutil.Error):
                # Se falhar a cópia, ignora silenciosamente
                pass
    
    return migrated


def open_data_folder() -> bool:
    """
    Abre a pasta de dados da aplicação no explorador de arquivos.
    
    Returns:
        bool: True se abriu com sucesso, False caso contrário.
    """
    import subprocess
    
    app_dir = ensure_app_data_dir()
    
    try:
        if sys.platform == "win32":
            os.startfile(str(app_dir))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(app_dir)], check=True)
        else:
            subprocess.run(["xdg-open", str(app_dir)], check=True)
        return True
    except Exception:
        return False


# ---
# Nota de Transparência e Responsabilidade
#
# Descrição: Este arquivo contém seções de código que foram geradas
#            ou assistidas por IA.
#
# Auditoria: Todo o código foi revisado, testado e validado por
#            uma desenvolvedora humana.
#
# Tag:       @ai_generated
# Dev:       Maisa Pires
# ---
