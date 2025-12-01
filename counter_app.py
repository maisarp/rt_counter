from pathlib import Path

from retweet_counter.app import run_app
from retweet_counter.paths import get_default_paths, migrate_legacy_files


def main() -> None:
    """Ponto de entrada para execução local do contador."""
    # Obtém caminhos centralizados (AppData)
    paths = get_default_paths()
    
    # Tenta migrar arquivos de instalação antiga (mesma pasta do executável)
    legacy_dir = Path(__file__).parent
    migrate_legacy_files(legacy_dir)
    
    run_app(
        data_path=paths["data_file"],
        config_path=paths["config_file"],
    )


if __name__ == "__main__":
    main()
