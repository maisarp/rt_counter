"""Gerenciamento de visualização em tempo real."""
from __future__ import annotations

import os
import threading
import time
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .storage import CalendarCounter


class HtmlRealtimeViewer:
    """Visualizador HTML com atualização automática em tempo real."""
    
    def __init__(self, counter: CalendarCounter) -> None:
        """
        Inicializa o visualizador HTML em tempo real.
        
        Args:
            counter: Instância do CalendarCounter para monitorar mudanças.
        """
        self.counter = counter
        # Usa pasta de exportação personalizada se definida
        self.view_path = counter.get_export_path(f"{counter.file_path.stem}_view.csv")
        self.html_path = counter.get_export_path(f"{counter.file_path.stem}_view.html")
        self.running = False
        self.thread = None
        self._last_modification = 0
        
    def start(self) -> bool:
        """
        Inicia o monitor em uma thread separada.
        
        Returns:
            True se iniciou com sucesso.
        """
        # Limpa qualquer arquivo de sinal de fechamento anterior
        self.cleanup_close_signal()
        
        # Garante que o CSV view existe antes de criar o HTML
        if not self.view_path.exists():
            # Força a criação do CSV view
            try:
                self.counter.save()
            except Exception:
                pass
        
        # Cria o HTML inicial
        self._update_html()
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        return True
    
    def stop(self) -> None:
        """Para o monitor."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
    
    def create_close_signal(self) -> None:
        """Cria um arquivo sinalizador para fechar o navegador e atualiza o HTML."""
        try:
            close_signal_path = self.counter.file_path.with_name(f"{self.counter.file_path.stem}_close.signal")
            close_signal_path.write_text("close", encoding="utf-8")
            
            # Força a atualização do HTML para mostrar a tela de fechamento
            self._update_html()
        except Exception:
            pass
    
    def cleanup_close_signal(self) -> None:
        """Remove o arquivo sinalizador de fechamento se existir."""
        try:
            close_signal_path = self.counter.file_path.with_name(f"{self.counter.file_path.stem}_close.signal")
            if close_signal_path.exists():
                close_signal_path.unlink()
        except Exception:
            pass
    
    def _monitor_loop(self) -> None:
        """Loop principal de monitoramento."""
        while self.running:
            try:
                if self.view_path.exists():
                    current_mtime = self.view_path.stat().st_mtime
                    
                    if current_mtime != self._last_modification:
                        self._update_html()
                        self._last_modification = current_mtime
                        
            except Exception:
                pass
            
            time.sleep(0.3)  # Verifica a cada 300ms
    
    def _update_html(self) -> None:
        """Atualiza o arquivo HTML com os dados mais recentes do CSV."""
        try:
            import pandas as pd
            import calendar as cal
            
            if not self.view_path.exists():
                return

            # Lê o CSV em formato de calendário
            df = pd.read_csv(self.view_path, sep=";", encoding="utf-8-sig")
            
            if df.empty:
                return

            html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="1">
    <title>Visualização em Tempo Real - Contador de Retweets</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #c3e6cb 0%, #d4edda 100%);
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            overflow: visible;
        }
        
        .header {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 25px;
            text-align: center;
            border-radius: 15px 15px 0 0;
        }
        
        .header h1 {
            font-size: 26px;
            margin-bottom: 8px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .header p {
            font-size: 13px;
            opacity: 0.9;
        }
        
        .live-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #4ade80;
            border-radius: 50%;
            animation: pulse 2s infinite;
            margin-right: 6px;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .calendar-section {
            padding: 30px;
            border-bottom: 2px solid #e2e8f0;
            overflow-x: auto;
            scroll-behavior: smooth;
        }
        
        .calendar-section:last-of-type {
            border-bottom: none;
        }
        
        .month-header {
            font-family: 'Sylfaen', Georgia, serif;
            font-size: 35px;
            color: #28a745;
            text-align: center;
            margin-bottom: 25px;
            font-weight: bold;
        }
        
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 10px;
            min-width: 750px;
            max-width: 900px;
            margin: 0 auto;
        }
        
        .day-header {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 10px;
            text-align: center;
            font-weight: bold;
            font-size: 12px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .day-cell {
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 10px;
            min-height: 85px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            position: relative;
        }
        
        .day-cell:hover {
            border-color: #28a745;
            box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
            transform: translateY(-2px);
        }
        
        .day-cell.empty {
            background: #f8f9fa;
            border-color: transparent;
            opacity: 0.3;
        }
        
        .day-cell.weekend {
            background: #fff3cd;
        }
        
        .day-cell.weekend:hover {
            border-color: #ffc107;
        }
        
        .day-cell.has-retweets {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-color: #28a745;
        }
        
        .day-cell.has-retweets:hover {
            background: linear-gradient(135deg, #c3e6cb 0%, #b1e0bf 100%);
            box-shadow: 0 6px 16px rgba(40, 167, 69, 0.4);
        }
        
        .day-number {
            font-size: 11px;
            color: #6c757d;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .retweet-count {
            font-size: 42px;
            font-weight: bold;
            color: #28a745;
            text-align: center;
            line-height: 1;
        }
        
        .day-cell.has-retweets .retweet-count {
            color: #155724;
        }
        
        .retweet-label {
            font-size: 9px;
            color: #6c757d;
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .footer {
            padding: 18px;
            text-align: center;
            background: #f8f9fa;
            color: #6c757d;
            font-size: 12px;
            border-top: 1px solid #e2e8f0;
            border-radius: 0 0 15px 15px;
        }
        
        .timestamp {
            color: #495057;
            font-size: 11px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📅 Contador de Retweets</h1>
            <p>
                <span class="live-indicator"></span>
                Visualização em Tempo Real - Atualização Automática
            </p>
        </div>
"""
            
            # Processa o CSV em formato de calendário usando configuração dinâmica
            from .storage import get_weekday_labels
            weekday_labels = get_weekday_labels(self.counter.first_weekday)
            weekday_display = [label.upper() for label in weekday_labels]
            
            # Processa linha por linha do CSV
            current_month = None
            rows_data = df.to_dict('records')
            i = 0
            
            while i < len(rows_data):
                row = rows_data[i]
                first_col = str(row.get('Unnamed: 0', '')).strip()
                
                # Para de processar se chegou na seção de resumo semanal
                if first_col.startswith("====") or "RESUMO SEMANAL" in first_col:
                    break
                
                # Detecta início de novo mês
                if any(mes in first_col for mes in ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                                                      "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]):
                    # Fecha calendário anterior se houver
                    if current_month is not None:
                        html_content += """            </div>
        </div>
"""
                    
                    current_month = first_col
                    html_content += f"""
        <div class="calendar-section">
            <div class="month-header">{first_col}</div>
            <div class="calendar-grid">
"""
                    # Adiciona cabeçalhos dos dias da semana
                    for day_label in weekday_display:
                        html_content += f'                <div class="day-header">{day_label}</div>\n'
                
                # Linha com dias (começa com "dia")
                elif any("dia" in str(row.get(label, '')).lower() for label in weekday_labels if str(row.get(label, '')).strip()):
                    # Processa linha de dias e a próxima linha de valores
                    week_days = {}
                    for weekday_label in weekday_labels:
                        cell_value = str(row.get(weekday_label, '')).strip()
                        if cell_value and cell_value != "nan" and "dia" in cell_value.lower():
                            try:
                                day_num = int(cell_value.lower().replace("dia", "").strip())
                                week_days[weekday_label] = day_num
                            except ValueError:
                                week_days[weekday_label] = None
                        else:
                            week_days[weekday_label] = None
                    
                    # Pega próxima linha com valores de RTs se houver
                    if i + 1 < len(rows_data):
                        next_row = rows_data[i + 1]
                        
                        for weekday_idx, weekday_label in enumerate(weekday_labels):
                            day_num = week_days.get(weekday_label)
                            
                            if day_num is None:
                                html_content += '                <div class="day-cell empty"></div>\n'
                                continue
                            
                            cell_value = str(next_row.get(weekday_label, '')).strip()
                            
                            try:
                                retweet_count = int(float(cell_value)) if cell_value and cell_value != "nan" and cell_value != "" else 0
                                
                                # Define classes CSS
                                classes = ['day-cell']
                                if weekday_idx >= 5:  # Sábado ou Domingo
                                    classes.append('weekend')
                                if retweet_count > 0:
                                    classes.append('has-retweets')
                                
                                class_str = ' '.join(classes)
                                
                                html_content += f"""                <div class="{class_str}">
                    <div class="day-number">{day_num:02d}</div>
                    <div class="retweet-count">{retweet_count}</div>
                    <div class="retweet-label">RTs</div>
                </div>
"""
                            except (ValueError, TypeError):
                                html_content += f"""                <div class="day-cell">
                    <div class="day-number">{day_num:02d}</div>
                    <div class="retweet-count">0</div>
                    <div class="retweet-label">RTs</div>
                </div>
"""
                        
                        i += 1  # Pula a próxima linha pois já foi processada
                    else:
                        # Se não há próxima linha, adiciona células vazias para os dias
                        for weekday_idx, weekday_label in enumerate(weekday_labels):
                            day_num = week_days.get(weekday_label)
                            
                            if day_num is None:
                                html_content += '                <div class="day-cell empty"></div>\n'
                            else:
                                html_content += f"""                <div class="day-cell">
                    <div class="day-number">{day_num:02d}</div>
                    <div class="retweet-count">0</div>
                    <div class="retweet-label">RTs</div>
                </div>
"""
                
                i += 1
            
            # Fecha o último calendário se houver
            if current_month is not None:
                html_content += """            </div>
        </div>
"""
            
            # Verifica se existe arquivo de sinal de fechamento
            close_signal_path = self.counter.file_path.with_name(f"{self.counter.file_path.stem}_close.signal")
            close_signal_exists = close_signal_path.exists()
            
            # Se a aplicação foi fechada, mostra tela de fechamento
            if close_signal_exists:
                html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aplicação Fechada - Contador de Retweets</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            text-align: center;
            max-width: 400px;
        }}
        .container h2 {{
            color: #28a745;
            margin-bottom: 20px;
            font-size: 24px;
        }}
        .container p {{
            color: #666;
            margin-bottom: 15px;
            line-height: 1.5;
        }}
        .close-button {{
            margin-top: 20px;
            padding: 12px 24px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: background 0.3s;
        }}
        .close-button:hover {{
            background: #218838;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>✅ Aplicação Fechada</h2>
        <p>A aplicação principal do Contador de Retweets foi encerrada.</p>
        <p>Esta aba será fechada automaticamente em 40 segundos.</p>
        <p>Você também pode fechá-la manualmente clicando no botão abaixo.</p>
        <p><small>Encerrado em: {time.strftime("%d/%m/%Y às %H:%M:%S")}</small></p>
        <button class="close-button" onclick="window.close()">Fechar Aba</button>
    </div>
    
    <script>
        // Contador regressivo de 40 segundos
        let countdown = 40;
        const button = document.querySelector('.close-button');
        
        function updateCountdown() {{
            if (countdown > 0) {{
                button.textContent = 'Fechar Aba (' + countdown + 's)';
                countdown--;
                setTimeout(updateCountdown, 1000);
            }} else {{
                button.textContent = 'Fechar Aba';
                // Tenta fechar automaticamente após 40 segundos
                window.close();
            }}
        }}
        
        // Inicia o contador regressivo
        updateCountdown();
        
        // Foca no botão para facilitar o uso
        setTimeout(function() {{
            button.focus();
        }}, 500);
    </script>
</body>
</html>"""
            else:
                # HTML normal - sem monitoramento automático por tempo
                html_content += f"""        
        <div class="footer">
            <div class="timestamp">
                📊 Última atualização: {time.strftime("%d/%m/%Y às %H:%M:%S")}
            </div>
            <p style="margin-top: 8px;">
                Esta página é atualizada automaticamente a cada segundo
            </p>
        </div>
    </div>
</body>
</html>
"""
            
            # Salva o HTML
            with open(self.html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
                
        except Exception:
            pass


def open_html_viewer(html_path: Path) -> bool:
    """
    Abre o visualizador HTML no navegador padrão.
    
    Args:
        html_path: Caminho para o arquivo HTML.
    
    Returns:
        True se abriu com sucesso.
    """
    if not html_path.exists():
        return False
    
    try:
        webbrowser.open(f"file:///{html_path.absolute().as_posix()}")
        return True
    except Exception:
        return False


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
        csv_path: Caminho para o arquivo CSV final.
    """
    import tkinter as tk
    from tkinter import messagebox
    
    # Se parent não existe mais, cria uma janela temporária
    if parent is None or not parent.winfo_exists():
        temp_root = tk.Tk()
        temp_root.withdraw()
        parent_window = temp_root
    else:
        parent_window = parent
    
    response = messagebox.askyesno(
        "Planilha Salva",
        "Deseja abrir a planilha final gerada?\n\n"
        f"Arquivo: {csv_path.name}",
        icon="question",
        parent=parent_window
    )
    
    # Fecha a janela temporária se foi criada
    if 'temp_root' in locals():
        temp_root.destroy()
    
    if response:
        open_csv_in_excel(csv_path)
