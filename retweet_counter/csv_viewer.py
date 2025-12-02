"""Gerenciamento de visualização e exportação de arquivos."""
from __future__ import annotations

import os
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .storage import CalendarCounter


# ============================================================================
# DEPRECATED - Classe HtmlRealtimeViewer removida
# A visualização em tempo real via HTML foi descontinuada.
# Use o arquivo XLSX gerado automaticamente para visualização.
# ============================================================================
# class HtmlRealtimeViewer:
#     """Visualizador HTML com atualização automática em tempo real."""
#     ...
# ============================================================================


# DEPRECATED - Função open_html_viewer removida
# def open_html_viewer(html_path: Path) -> bool:
#     ...


def open_csv_in_excel(csv_path: Path) -> bool:
    """
    Abre um arquivo CSV no Excel ou aplicativo padrão.
    
    Args:
        csv_path: Caminho para o arquivo CSV a ser aberto.
    
    Returns:
        True se abriu com sucesso, False caso contrário.
    """
    if not csv_path.exists():
        return False
    
    try:
        os.startfile(str(csv_path))
        return True
    except Exception:
        return False


def open_final_csv_dialog(parent, csv_path: Path) -> None:
    """
    Mostra um diálogo perguntando se o usuário deseja abrir a planilha final.
    
    Args:
        parent: Janela principal ou None.
        csv_path: Caminho para o arquivo CSV final (será convertido para XLSX).
    """
    import tkinter as tk
    from tkinter import messagebox
    
    # Prioriza o arquivo XLSX se existir
    xlsx_path = csv_path.with_suffix(".xlsx")
    
    if xlsx_path.exists():
        file_to_open = xlsx_path
        file_type = "Excel"
    elif csv_path.exists():
        file_to_open = csv_path
        file_type = "CSV"
    else:
        # Nenhum arquivo existe
        return
    
    # Se parent não existe mais, cria uma janela temporária
    if parent is None:
        temp_root = tk.Tk()
        temp_root.withdraw()
        parent_window = temp_root
    else:
        try:
            if not parent.winfo_exists():
                temp_root = tk.Tk()
                temp_root.withdraw()
                parent_window = temp_root
            else:
                parent_window = parent
        except Exception:
            temp_root = tk.Tk()
            temp_root.withdraw()
            parent_window = temp_root
    
    response = messagebox.askyesno(
        "Planilha Salva",
        f"Deseja abrir a planilha {file_type} final?\n\n"
        f"Arquivo: {file_to_open.name}",
        icon="question",
        parent=parent_window
    )
    
    # Fecha a janela temporária se foi criada
    if 'temp_root' in locals():
        temp_root.destroy()
    
    if response:
        try:
            import os
            import subprocess
            import sys
            
            if sys.platform == "win32":
                os.startfile(str(file_to_open))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(file_to_open)], check=True)
            else:
                subprocess.run(["xdg-open", str(file_to_open)], check=True)
        except Exception:
            # Se falhar, tenta abrir com webbrowser como fallback
            try:
                import webbrowser
                webbrowser.open(str(file_to_open))
            except Exception:
                pass
