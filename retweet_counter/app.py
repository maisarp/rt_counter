from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import calendar

# Importa CustomTkinter para interface moderna
import customtkinter as ctk

from .csv_viewer import open_final_csv_dialog, open_csv_in_excel
from .paths import open_data_folder, get_app_data_dir
from .storage import (
    CalendarCounter,
    MONTH_CHOICES,
    MONTH_NAME_TO_NUMBER,
    MONTH_NUMBER_TO_NAME,
    WEEKDAY_LABELS,
    WEEK_COLORS,
    WEEK_COLOR_NAMES,
    get_weekday_labels,
)
from .models.timer import Timer

# Configuração do tema CustomTkinter - Tema escuro alternativo/egirl
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Paleta de cores alternativa/egirl - tons pastéis
COLORS = {
    "bg_dark": "#1a1a2e",           # Fundo principal escuro
    "bg_card": "#16213e",           # Fundo dos cards
    "bg_input": "#0f3460",          # Fundo dos inputs
    "accent_pink": "#e94560",       # Rosa vibrante (principal)
    "accent_pink_hover": "#ff6b6b", # Rosa hover
    "accent_cyan": "#00d9ff",       # Ciano neon (timer)
    # Tons pastéis para botões
    "pastel_pink": "#f8a5c2",       # Rosa pastel (+1)
    "pastel_pink_hover": "#f78fb3",
    "pastel_gray": "#778ca3",       # Cinza pastel (-1)
    "pastel_gray_hover": "#596275",
    "pastel_green": "#7bed9f",      # Verde pastel (iniciar)
    "pastel_green_hover": "#2ed573",
    "pastel_red": "#ff6b81",        # Rosa/vermelho pastel (parar)
    "pastel_red_hover": "#ee5a6f",
    "pastel_orange": "#ffa502",     # Laranja (reset/warning)
    "pastel_orange_hover": "#e59400",
    # Lilás para botões de ferramenta
    "tool_purple": "#9b59b6",       # Lilás (ferramentas)
    "tool_purple_hover": "#8e44ad",
    "text_primary": "#eaeaea",      # Texto principal
    "text_secondary": "#a0a0a0",    # Texto secundário
    "text_muted": "#6c6c6c",        # Texto discreto
    "border": "#2d2d44",            # Bordas
}


class CounterApp:
    """Interface gráfica moderna com CustomTkinter para visualizar o calendário e aplicar contagens."""

    def __init__(self, root: ctk.CTk, counter: CalendarCounter) -> None:
        """Configura a janela principal, calendários e ações disponíveis."""
        self.root = root
        self.counter = counter
        # self.html_viewer: HtmlRealtimeViewer | None = None  # DEPRECATED - Visualização HTML removida
        self.root.title("Retweet Counter")
        # Altura estendida para mostrar timer e controles sem precisar expandir
        self.root.geometry("340x720")
        self.root.minsize(320, 680)
        self.root.resizable(True, True)
        self.root.configure(fg_color=COLORS["bg_dark"])

        today = date.today()
        initial_year, initial_month = self.counter.load_last_period(today)

        self.year_var = tk.IntVar(value=initial_year)
        self.month_var = tk.StringVar(value=MONTH_NUMBER_TO_NAME[initial_month])
        self.value_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.manual_value_var = tk.StringVar()
        self.weekly_target_var = tk.StringVar()
        self.selected_day = 1
        self.selected_day_month = initial_month  # Mês real do dia selecionado
        self.selected_day_year = initial_year    # Ano real do dia selecionado
        
        # Inicializa o timer com configuração padrão (start em 1, stop em 50)
        self.timer = Timer()
        self.timer_var = tk.StringVar(value="Tempo: 0.0s")

        # Cores padrão para semanas (usadas na interface)
        self._week_colors = WEEK_COLORS
        self._day_buttons: list[list[ctk.CTkButton]] = []

        self._build_widgets()
        self._render_calendar()
        self._refresh_value()
        self._refresh_weekly_info()
        
        # Configura o protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _build_widgets(self) -> None:
        """Monta os componentes da interface gráfica moderna com CustomTkinter."""
        # Frame principal
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        # Header com título estilizado
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill=tk.X, pady=(0, 8))
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="RT Counter", 
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS["accent_pink"]
        )
        title_label.pack(side=tk.LEFT)
        
        # Botões do header (direita)
        header_buttons = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_buttons.pack(side=tk.RIGHT)
        
        # DEPRECATED - Botão Visualizar HTML removido
        # view_button = ctk.CTkButton(
        #     header_buttons,
        #     text="Visualizar",
        #     width=75,
        #     height=28,
        #     font=ctk.CTkFont(size=10),
        #     command=self._open_html_viewer,
        #     fg_color=COLORS["tool_purple"],
        #     hover_color=COLORS["tool_purple_hover"],
        #     corner_radius=6
        # )
        # view_button.pack(side=tk.LEFT, padx=(0, 6))
        
        config_button = ctk.CTkButton(
            header_buttons,
            text="Config",
            width=55,
            height=28,
            font=ctk.CTkFont(size=10),
            command=self._open_config_dialog,
            fg_color=COLORS["tool_purple"],
            hover_color=COLORS["tool_purple_hover"],
            corner_radius=6
        )
        config_button.pack(side=tk.LEFT, padx=(0, 6))
        
        # Botão para abrir pasta de dados
        folder_button = ctk.CTkButton(
            header_buttons,
            text="Pasta",
            width=50,
            height=28,
            font=ctk.CTkFont(size=10),
            command=self._open_data_folder,
            fg_color=COLORS["tool_purple"],
            hover_color=COLORS["tool_purple_hover"],
            corner_radius=6
        )
        folder_button.pack(side=tk.LEFT)

        # Navegação de período (mês/ano)
        nav_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg_card"], corner_radius=8)
        nav_frame.pack(fill=tk.X, pady=(0, 8))
        
        nav_inner = ctk.CTkFrame(nav_frame, fg_color="transparent")
        nav_inner.pack(pady=8, padx=10)

        # Seta esquerda
        month_down_btn = ctk.CTkButton(
            nav_inner, text="◀", width=32, height=28,
            command=lambda: self._change_month(-1),
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["tool_purple"],
            hover_color=COLORS["tool_purple_hover"],
            corner_radius=6
        )
        month_down_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # Dropdown de mês
        month_selector = ctk.CTkComboBox(
            nav_inner,
            variable=self.month_var,
            values=[name for _, name in MONTH_CHOICES],
            state="readonly",
            width=100,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            button_color=COLORS["tool_purple"],
            button_hover_color=COLORS["tool_purple_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            command=lambda x: self._on_period_change()
        )
        month_selector.pack(side=tk.LEFT, padx=(0, 8))

        # Seta direita
        month_up_btn = ctk.CTkButton(
            nav_inner, text="▶", width=32, height=28,
            command=lambda: self._change_month(1),
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["tool_purple"],
            hover_color=COLORS["tool_purple_hover"],
            corner_radius=6
        )
        month_up_btn.pack(side=tk.LEFT, padx=(0, 12))
        
        # Ano
        year_entry = ctk.CTkEntry(
            nav_inner,
            textvariable=self.year_var,
            width=55,
            height=28,
            justify="center",
            font=ctk.CTkFont(size=11),
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"]
        )
        year_entry.pack(side=tk.LEFT)
        year_entry.bind("<Return>", lambda e: self._on_period_change())
        year_entry.bind("<FocusOut>", lambda e: self._on_period_change())

        # Frame do calendário - MANTIDO IGUAL (cores originais preservadas)
        self.calendar_frame = ctk.CTkFrame(main_frame, fg_color="#f8f9fa", corner_radius=8)
        self.calendar_frame.pack(fill=tk.BOTH, expand=True, pady=6)
        
        # Inner frame para centralizar conteúdo
        calendar_inner = ctk.CTkFrame(self.calendar_frame, fg_color="transparent")
        calendar_inner.pack(expand=True, pady=5, padx=5)

        # Cabeçalho dos dias da semana (compacto)
        weekday_labels = get_weekday_labels(self.counter.first_weekday)
        self.header_labels = []
        for col, label in enumerate(weekday_labels):
            header = ctk.CTkLabel(
                calendar_inner, 
                text=label, 
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color="#495057",
                width=40
            )
            header.grid(row=0, column=col, padx=1, pady=(0, 3))
            self.header_labels.append(header)

        # Botões dos dias (6 linhas x 7 colunas) - CORES DO CALENDÁRIO PRESERVADAS
        for row in range(1, 7):
            row_buttons: list[ctk.CTkButton] = []
            for col in range(7):
                button = ctk.CTkButton(
                    calendar_inner,
                    text="",
                    width=40,
                    height=38,
                    font=ctk.CTkFont(size=9),
                    corner_radius=6,
                    fg_color="#ffffff",
                    text_color="#000000",
                    hover_color="#e9ecef",
                    command=lambda day=0: self._select_day(day),
                )
                button.grid(row=row, column=col, padx=1, pady=1)
                row_buttons.append(button)
            self._day_buttons.append(row_buttons)

        # Frame do contador central
        counter_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg_card"], corner_radius=10)
        counter_frame.pack(fill=tk.X, pady=(6, 6))
        
        counter_inner = ctk.CTkFrame(counter_frame, fg_color="transparent")
        counter_inner.pack(pady=10)
        
        # Valor grande e destacado
        value_label = ctk.CTkLabel(
            counter_inner, 
            textvariable=self.value_var, 
            font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold"),
            text_color=COLORS["accent_pink"]
        )
        value_label.pack()
        
        # Timer
        timer_display_label = ctk.CTkLabel(
            counter_inner, 
            textvariable=self.timer_var, 
            font=ctk.CTkFont(size=11), 
            text_color=COLORS["accent_cyan"]
        )
        timer_display_label.pack(pady=(2, 8))

        # Botões de contagem lado a lado
        count_buttons_frame = ctk.CTkFrame(counter_inner, fg_color="transparent")
        count_buttons_frame.pack()

        # Botão +1 (PRINCIPAL - à ESQUERDA, rosa pastel)
        btn_plus = ctk.CTkButton(
            count_buttons_frame,
            text="+1",
            command=lambda: self._change_value(1),
            width=120,
            height=50,
            font=ctk.CTkFont(size=22, weight="bold"),
            fg_color=COLORS["pastel_pink"],
            hover_color=COLORS["pastel_pink_hover"],
            text_color="#1a1a2e",
            corner_radius=10
        )
        btn_plus.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão -1 (secundário - à direita, cinza pastel)
        btn_minus = ctk.CTkButton(
            count_buttons_frame,
            text="-1",
            command=lambda: self._change_value(-1),
            width=60,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["pastel_gray"],
            hover_color=COLORS["pastel_gray_hover"],
            corner_radius=8
        )
        btn_minus.pack(side=tk.LEFT)

        # Frame inferior com controles organizados
        controls_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg_card"], corner_radius=8)
        controls_frame.pack(fill=tk.X, pady=(0, 6))
        
        controls_inner = ctk.CTkFrame(controls_frame, fg_color="transparent")
        controls_inner.pack(pady=8, padx=10, fill=tk.X)

        # Linha 1: Valor manual + Meta
        row1 = ctk.CTkFrame(controls_inner, fg_color="transparent")
        row1.pack(fill=tk.X, pady=(0, 6))

        # Grupo Valor
        value_group = ctk.CTkFrame(row1, fg_color="transparent")
        value_group.pack(side=tk.LEFT)
        
        ctk.CTkLabel(
            value_group, 
            text="Valor", 
            font=ctk.CTkFont(size=9),
            text_color=COLORS["text_secondary"]
        ).pack(side=tk.LEFT, padx=(0, 4))

        manual_entry = ctk.CTkEntry(
            value_group, 
            textvariable=self.manual_value_var, 
            width=55, 
            height=26,
            justify="center", 
            font=ctk.CTkFont(size=10),
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"]
        )
        manual_entry.pack(side=tk.LEFT, padx=(0, 4))
        manual_entry.bind("<Return>", lambda event: self._on_manual_apply())

        manual_button = ctk.CTkButton(
            value_group, 
            text="OK", 
            command=self._on_manual_apply, 
            width=35,
            height=26,
            font=ctk.CTkFont(size=9),
            fg_color=COLORS["tool_purple"],
            hover_color=COLORS["tool_purple_hover"],
            corner_radius=4
        )
        manual_button.pack(side=tk.LEFT)

        # REMOVIDO: Grupo Meta foi movido para a janela de Configuração
        # A meta agora é configurada junto com a configuração da semana
        # target_group = ctk.CTkFrame(row1, fg_color="transparent")
        # target_group.pack(side=tk.RIGHT)
        # ... (código antigo comentado)

        # Linha 2: Controles do timer (centralizados)
        row2 = ctk.CTkFrame(controls_inner, fg_color="transparent")
        row2.pack()
        
        timer_label = ctk.CTkLabel(
            row2, 
            text="Timer", 
            font=ctk.CTkFont(size=9),
            text_color=COLORS["text_secondary"]
        )
        timer_label.pack(side=tk.LEFT, padx=(0, 8))

        start_timer_button = ctk.CTkButton(
            row2, 
            text="Iniciar", 
            command=lambda: self.timer.start(), 
            width=55,
            height=26,
            font=ctk.CTkFont(size=9),
            fg_color=COLORS["pastel_green"],
            hover_color=COLORS["pastel_green_hover"],
            text_color="#1a1a2e",
            corner_radius=4
        )
        start_timer_button.pack(side=tk.LEFT, padx=(0, 4))

        stop_timer_button = ctk.CTkButton(
            row2, 
            text="Parar", 
            command=lambda: self.timer.stop(), 
            width=50,
            height=26,
            font=ctk.CTkFont(size=9),
            fg_color=COLORS["pastel_red"],
            hover_color=COLORS["pastel_red_hover"],
            text_color="#1a1a2e",
            corner_radius=4
        )
        stop_timer_button.pack(side=tk.LEFT, padx=(0, 4))

        reset_timer_button = ctk.CTkButton(
            row2, 
            text="Reset", 
            command=self._reset_timer, 
            width=50,
            height=26,
            font=ctk.CTkFont(size=9),
            fg_color=COLORS["pastel_orange"],
            hover_color=COLORS["pastel_orange_hover"],
            text_color="#1a1a2e",
            corner_radius=4
        )
        reset_timer_button.pack(side=tk.LEFT)

        # Frame para resumo semanal (footer)
        self.summary_frame = ctk.CTkFrame(main_frame, fg_color=COLORS["bg_input"], corner_radius=6)
        self.summary_frame.pack(fill=tk.X, pady=(0, 4))
        
        self.summary_var = tk.StringVar()
        summary_label = ctk.CTkLabel(
            self.summary_frame, 
            textvariable=self.summary_var, 
            font=ctk.CTkFont(size=9), 
            justify="left",
            text_color=COLORS["text_primary"]
        )
        summary_label.pack(anchor="w", padx=8, pady=5)

        # Status label
        status_label = ctk.CTkLabel(
            main_frame, 
            textvariable=self.status_var, 
            font=ctk.CTkFont(size=9), 
            text_color=COLORS["text_muted"]
        )
        status_label.pack(pady=(0, 0))
        
        # Inicia a atualização do timer
        self._update_timer()

    def _change_month(self, delta: int) -> None:
        """Altera o mês atual pelo delta informado, ajustando o ano se necessário."""
        month_name = self.month_var.get()
        current_month = MONTH_NAME_TO_NUMBER.get(month_name, 1)
        current_year = self.year_var.get()
        
        new_month = current_month + delta
        
        # Ajusta ano quando muda de dezembro para janeiro ou vice-versa
        if new_month < 1:
            new_month = 12
            current_year -= 1
        elif new_month > 12:
            new_month = 1
            current_year += 1
        
        self.month_var.set(MONTH_NUMBER_TO_NAME[new_month])
        self.year_var.set(current_year)
        self._on_period_change()

    def _change_year(self, delta: int) -> None:
        """Altera o ano atual pelo delta informado."""
        current_year = self.year_var.get()
        self.year_var.set(current_year + delta)
        self._on_period_change()

    def _on_period_change(self) -> None:
        """Atualiza o calendário quando mês ou ano são alterados pelo usuário."""
        month_name = self.month_var.get()
        month_number = MONTH_NAME_TO_NUMBER.get(month_name)
        try:
            year_value = int(self.year_var.get())
        except (TypeError, ValueError):
            return

        if not month_number:
            return

        data = self.counter.get_month(year_value, month_number)
        if self.selected_day > data.last_day():
            self.selected_day = data.last_day()

        self.counter.save_last_period(year_value, month_number)
        self._render_calendar()
        self._refresh_value()
        self._refresh_weekly_info()

    def _render_calendar(self) -> None:
        """Redesenha o grid com os dias e seus totais, respeitando configurações de semana."""
        month_number = MONTH_NAME_TO_NUMBER.get(self.month_var.get(), 1)
        year_value = int(self.year_var.get())
        
        # Obtém configurações de semana para este mês
        week_configs = self.counter.get_all_week_configs_for_month(year_value, month_number)
        
        # Obtém dados do mês atual
        data = self._current_month_data()
        
        # Cria set de semanas configuradas
        configured_weeks = {c.week_in_month for c in week_configs} if week_configs else set()
        
        # Usa matriz com suporte a configurações (funciona mesmo sem configs)
        matrix = data.to_matrix_with_week_configs(week_configs)
        
        for row_index, row_buttons in enumerate(self._day_buttons):
            week_num = row_index + 1
            
            if row_index < len(matrix):
                week = matrix[row_index]
            else:
                week = [None] * 7
            
            # Define cor da semana (aplica cor se semana está configurada ou para visual)
            if week_num in configured_weeks or any(cell is not None for cell in week):
                week_color = self._week_colors.get(week_num, "#ffffff")
            else:
                week_color = "#ffffff"
            
            for col_index, button in enumerate(row_buttons):
                cell = week[col_index] if col_index < len(week) else None
                
                if cell is None:
                    button.configure(
                        text="",
                        state=tk.DISABLED,
                        fg_color="#f0f0f0",
                        text_color="#cccccc",
                        hover_color="#f0f0f0"
                    )
                    button.day = None
                    button.date_info = None
                    continue
                
                day, cell_month, cell_year = cell
                
                # Obtém total do dia (pode ser de outro mês)
                if cell_month == month_number and cell_year == year_value:
                    total = data.totals.get(day, 0)
                else:
                    # Dia de outro mês
                    other_data = self.counter.get_month(cell_year, cell_month)
                    total = other_data.totals.get(day, 0)
                
                # Formata texto do dia
                if cell_month != month_number or cell_year != year_value:
                    # Dia de outro mês - cor diferenciada mas sem mostrar mês
                    day_text = f"{day}\n{total}"
                    text_color = "#6c757d"  # Cinza para diferenciar
                else:
                    day_text = f"{day}\n{total}"
                    text_color = "#212529"
                
                # Define cor de fundo baseada na semana
                bg_color = week_color
                hover_color = self._lighten_color(week_color, 0.1)
                
                # Destaca dia selecionado (usando mês/ano real do dia selecionado)
                selected_month = getattr(self, 'selected_day_month', month_number)
                selected_year = getattr(self, 'selected_day_year', year_value)
                
                is_selected = (day == self.selected_day and 
                               cell_month == selected_month and 
                               cell_year == selected_year)
                
                if is_selected:
                    bg_color = "#007bff"
                    text_color = "#ffffff"
                    hover_color = "#0056b3"
                
                button.configure(
                    text=day_text,
                    state=tk.NORMAL,
                    fg_color=bg_color,
                    text_color=text_color,
                    hover_color=hover_color
                )
                # Reconfigura comando para este dia específico
                button.configure(command=lambda d=day, m=cell_month, y=cell_year: self._select_day_extended(d, m, y))
                button.day = day
                button.date_info = (day, cell_month, cell_year)

    def _lighten_color(self, hex_color: str, factor: float = 0.1) -> str:
        """Clareia uma cor hexadecimal."""
        # Remove # se presente
        hex_color = hex_color.lstrip('#')
        
        # Converte para RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Clareia
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        
        return f"#{r:02x}{g:02x}{b:02x}"

    def _select_day_extended(self, day: int, month: int, year: int) -> None:
        """
        Seleciona um dia para trabalhar, podendo ser de outro mês.
        
        NÃO muda o mês visualizado - apenas seleciona o dia para contagem.
        O usuário deve mudar o mês manualmente se desejar.
        """
        # Armazena o dia selecionado E o mês/ano real do dia
        self.selected_day = day
        self.selected_day_month = month  # Mês real do dia selecionado
        self.selected_day_year = year    # Ano real do dia selecionado
        
        self._render_calendar()
        self._refresh_value()
        self._refresh_weekly_info()

    def _select_day(self, day: int | None) -> None:
        """Altera o dia selecionado ao clicar no calendário."""
        if not day:
            return
        self.selected_day = day
        self._render_calendar()
        self._refresh_value()
        self._refresh_weekly_info()

    def _current_month_data(self):
        month_number = MONTH_NAME_TO_NUMBER.get(self.month_var.get(), 1)
        year_value = int(self.year_var.get())
        return self.counter.get_month(year_value, month_number)

    def _current_date(self) -> date:
        """
        Retorna a data do dia selecionado.
        
        Usa o mês/ano real do dia selecionado (que pode ser diferente
        do mês sendo visualizado no calendário).
        """
        # Usa o mês/ano real do dia selecionado se disponível
        month = getattr(self, 'selected_day_month', None)
        year = getattr(self, 'selected_day_year', None)
        
        if month is None or year is None:
            # Fallback para o mês visualizado
            month = MONTH_NAME_TO_NUMBER.get(self.month_var.get(), 1)
            year = int(self.year_var.get())
        
        return date(year, month, self.selected_day)

    def _refresh_value(self) -> None:
        """
        Atualiza o valor exibido para o dia selecionado.
        
        Busca o valor do mês/ano real do dia selecionado.
        """
        current_date = self._current_date()
        # Busca dados do mês correto do dia selecionado
        month_data = self.counter.get_month(current_date.year, current_date.month)
        value = month_data.totals.get(current_date.day, 0)
        self.value_var.set(str(value))
        self.manual_value_var.set(str(value))

    def _update_timer(self) -> None:
        """Atualiza a exibição do timer na interface."""
        if self.timer.is_running:
            elapsed = self.timer.get_elapsed_time()
            self.timer_var.set(f"Tempo: {elapsed:.1f}s")
        self.root.after(100, self._update_timer)  # Atualiza a cada 100ms

    def _reset_timer(self) -> None:
        """Reinicia o timer e atualiza a exibição."""
        self.timer.reset()
        self.timer_var.set("Tempo: 0.0s")

    def _change_value(self, delta: int) -> None:
        """
        Altera o valor do dia selecionado pelo delta informado.
        
        Salva no mês/ano correto do dia selecionado.
        """
        # Obtém a data real do dia selecionado
        current_date = self._current_date()
        month_data = self.counter.get_month(current_date.year, current_date.month)
        
        current = month_data.totals.get(current_date.day, 0)
        new_value = max(0, current + delta)
        month_data.totals[current_date.day] = new_value
        
        # Verifica se deve iniciar/parar o timer automaticamente
        self.timer.check_auto_trigger(new_value)
        
        self.counter.save()
        self._render_calendar()
        self._refresh_value()
        self._refresh_weekly_info()
        
        # Mostra hora do último RT adicionado
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.status_var.set(f"Último RT adicionado às {current_time}")

    def _on_manual_apply(self) -> None:
        """Define manualmente o valor para o dia selecionado."""
        try:
            value = int(self.manual_value_var.get())
            if value < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Informe um número inteiro maior ou igual a zero.")
            return

        current_date = self._current_date()
        try:
            self.counter.set_value(current_date, value)
            self.status_var.set("✓ Valor salvo automaticamente")
            self._render_calendar()
            self._refresh_value()
            self._refresh_weekly_info()
            
            # Limpa o status após 2 segundos
            self.root.after(2000, lambda: self.status_var.set(""))
        except Exception as error:
            messagebox.showerror("Erro", f"Não foi possível definir o valor: {error}")

    def _on_save(self) -> None:
        """Permite ao usuário forçar a gravação dos dados."""
        try:
            self.counter.save()
            current_month = MONTH_NAME_TO_NUMBER[self.month_var.get()]
            self.counter.save_last_period(int(self.year_var.get()), current_month)
            self.status_var.set("Dados salvos com sucesso.")
        except Exception as error:
            messagebox.showerror("Erro", f"Falha ao salvar os dados: {error}")
    
    # DEPRECATED - Visualização HTML em tempo real removida
    # def _start_realtime_viewer(self) -> None:
    #     """Inicia o visualizador HTML em tempo real."""
    #     # Força a criação inicial do arquivo CSV
    #     self.counter.save()
    #     
    #     # Inicia o visualizador
    #     self.html_viewer = HtmlRealtimeViewer(self.counter)
    #     self.html_viewer.start()
    #     
    #     # Aguarda um momento e abre o navegador
    #     self.root.after(500, self._open_html_viewer)
    #     self.status_var.set("Visualização em tempo real ativada no navegador!")
    # 
    # def _open_html_viewer(self) -> None:
    #     """Abre o visualizador HTML no navegador."""
    #     if self.html_viewer:
    #         html_path = self.html_viewer.html_path
    #         if open_html_viewer(html_path):
    #             self.status_var.set("Visualização aberta no navegador - atualização automática ativa!")
    #         else:
    #             messagebox.showwarning(
    #                 "Aviso",
    #                 "Não foi possível abrir o visualizador no navegador."
    #             )

    def _open_data_folder(self) -> None:
        """Abre a pasta onde os dados da aplicação são armazenados."""
        if open_data_folder():
            data_dir = get_app_data_dir()
            self.status_var.set(f"Pasta aberta: {data_dir}")
        else:
            messagebox.showwarning(
                "Aviso",
                "Não foi possível abrir a pasta de dados."
            )

    def _on_target_apply(self) -> None:
        """Aplica a meta semanal definida pelo usuário."""
        try:
            value_text = self.weekly_target_var.get().strip()
            if not value_text:
                return
            
            new_target = int(value_text)
            current_date = self._current_date()
            
            # Obtém número da semana no mês
            week_in_month = self.counter.get_week_number_in_month(current_date)
            
            # Usa novo formato (ano-mês-semana)
            self.counter.set_weekly_target(
                current_date.year,
                current_date.month,
                week_in_month,
                new_target
            )
            self.weekly_target_var.set("")
            self._refresh_weekly_info()
            
            # Atualiza status com formato correto
            self.status_var.set(
                f"Meta {current_date.month:02d}/{current_date.year}-S{week_in_month} definida: {new_target}"
            )
            
        except ValueError:
            messagebox.showerror("Erro", "Digite um número válido para a meta semanal.")
        except Exception as error:
            messagebox.showerror("Erro", f"Erro ao definir meta: {error}")

    def _refresh_weekly_info(self) -> None:
        """Atualiza informações de meta e resumo semanal."""
        current_date = self._current_date()
        
        # Obtém o número da semana no mês usando o método do counter
        week_in_month = self.counter.get_week_number_in_month(current_date)
        
        # Atualiza meta semanal atual usando novo formato (ano-mês-semana)
        current_target = self.counter.get_weekly_target(
            current_date.year, 
            current_date.month, 
            week_in_month
        )
        self.weekly_target_var.set(str(current_target.expected) if current_target.expected > 0 else "")
        
        # Atualiza resumo semanal usando novo formato
        summary = self.counter.get_weekly_summary(
            current_date.year,
            current_date.month,
            week_in_month
        )
        
        # Busca configuração da semana para obter work_days
        week_config = self.counter.get_week_config(current_date.year, current_date.month, week_in_month)
        work_days = week_config.work_days if week_config else 6  # Padrão: 6 dias
        
        # Formato: MM-AA - S# (ex: 12-25 - S1)
        month_year = f"{current_date.month:02d}-{current_date.year % 100:02d}"
        
        summary_text = (
            f"{month_year} - S{week_in_month} ({work_days}d): "
            f"Feito: {summary['completed']} | "
            f"Esperado: {summary['expected']} | "
            f"Falta: {summary['missing']}"
        )
        
        if summary['remaining_days'] > 0:
            summary_text += f" | Por dia: {summary['daily_needed']} ({summary['remaining_days']}d)"
        
        self.summary_var.set(summary_text)
    
    def _open_config_dialog(self) -> None:
        """Abre janela de configurações para configurar semanas personalizadas com CustomTkinter."""
        
        # Cria janela modal com scroll
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Configuração de Semanas")
        dialog.geometry("520x700")
        dialog.minsize(480, 650)
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["bg_dark"])
        
        # Centraliza a janela na tela
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (520 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f"520x700+{x}+{y}")
        
        # Frame com scroll
        scroll_frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Frame principal dentro do scroll
        main_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # === SEÇÃO: Pasta de Exportação ===
        export_frame = ctk.CTkFrame(main_frame, corner_radius=8, fg_color=COLORS["bg_card"])
        export_frame.pack(fill=tk.X, pady=(0, 10))
        
        ctk.CTkLabel(
            export_frame,
            text="Pasta de Exportação (CSV/Excel):",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor=tk.W, padx=10, pady=(8, 4))
        
        export_inner = ctk.CTkFrame(export_frame, fg_color="transparent")
        export_inner.pack(fill=tk.X, padx=10, pady=(0, 8))
        
        # Variável para mostrar o caminho atual
        current_export = self.counter.export_folder or get_app_data_dir()
        export_path_var = tk.StringVar(value=str(current_export))
        
        export_entry = ctk.CTkEntry(
            export_inner,
            textvariable=export_path_var,
            width=320,
            height=28,
            font=ctk.CTkFont(size=9),
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            state="readonly"
        )
        export_entry.pack(side=tk.LEFT, padx=(0, 8))
        
        def choose_export_folder():
            """Abre diálogo para escolher pasta de exportação."""
            from tkinter import filedialog
            folder = filedialog.askdirectory(
                title="Escolha a pasta para salvar os arquivos CSV/Excel",
                initialdir=str(current_export)
            )
            if folder:
                folder_path = Path(folder)
                self.counter.set_export_folder(folder_path)
                export_path_var.set(str(folder_path))
                # Salva a configuração
                current_month = MONTH_NAME_TO_NUMBER[self.month_var.get()]
                self.counter.save_last_period(int(self.year_var.get()), current_month)
        
        def reset_export_folder():
            """Reseta para a pasta padrão (AppData)."""
            self.counter.set_export_folder(None)
            export_path_var.set(str(get_app_data_dir()))
            # Salva a configuração
            current_month = MONTH_NAME_TO_NUMBER[self.month_var.get()]
            self.counter.save_last_period(int(self.year_var.get()), current_month)
        
        choose_btn = ctk.CTkButton(
            export_inner,
            text="Escolher",
            command=choose_export_folder,
            width=70,
            height=28,
            font=ctk.CTkFont(size=10),
            fg_color=COLORS["tool_purple"],
            hover_color=COLORS["tool_purple_hover"]
        )
        choose_btn.pack(side=tk.LEFT, padx=(0, 4))
        
        reset_btn = ctk.CTkButton(
            export_inner,
            text="Padrão",
            command=reset_export_folder,
            width=60,
            height=28,
            font=ctk.CTkFont(size=10),
            fg_color=COLORS["pastel_gray"],
            hover_color=COLORS["pastel_gray_hover"]
        )
        reset_btn.pack(side=tk.LEFT)
        
        # Botão Salvar (não fecha mais a janela)
        def save_config():
            """Salva as configurações e mostra feedback visual."""
            self.counter.save()
            self._render_calendar()
            self._refresh_weekly_info()
            
            # Feedback visual para o usuário
            status_label.configure(
                text="Configurações salvas com sucesso!",
                text_color=COLORS["pastel_green"]
            )
            # Limpa o feedback após 3 segundos
            dialog.after(3000, lambda: status_label.configure(
                text="Selecione uma data no calendário para configurar a semana",
                text_color=COLORS["text_secondary"]
            ))
        
        # Variáveis - usa o mês/ano que está sendo visualizado na tela principal
        viewed_month = MONTH_NAME_TO_NUMBER.get(self.month_var.get(), date.today().month)
        viewed_year = int(self.year_var.get())
        
        calendar_year = tk.IntVar(value=viewed_year)
        calendar_month = tk.IntVar(value=viewed_month)
        target_month = tk.IntVar(value=viewed_month)
        target_year = tk.IntVar(value=viewed_year)
        selected_start_date = tk.StringVar(value="")
        calendar_buttons = []
        
        # Frame superior - Seleção do mês ALVO + botão salvar (tudo em uma linha)
        target_frame = ctk.CTkFrame(main_frame, corner_radius=8, fg_color=COLORS["bg_card"])
        target_frame.pack(fill=tk.X, pady=(0, 10))
        
        target_inner = ctk.CTkFrame(target_frame, fg_color="transparent")
        target_inner.pack(fill=tk.X, padx=10, pady=8)
        
        # Lado esquerdo: seletores de mês/ano
        left_frame = ctk.CTkFrame(target_inner, fg_color="transparent")
        left_frame.pack(side=tk.LEFT)
        
        ctk.CTkLabel(
            left_frame, 
            text="Mês:", 
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_primary"]
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        target_month_combo = ctk.CTkComboBox(
            left_frame,
            values=[name for _, name in MONTH_CHOICES],
            width=100,
            state="readonly",
            font=ctk.CTkFont(size=10),
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            button_color=COLORS["tool_purple"],
            button_hover_color=COLORS["tool_purple_hover"],
            dropdown_fg_color=COLORS["bg_card"]
        )
        target_month_combo.set(MONTH_NUMBER_TO_NAME[viewed_month])
        target_month_combo.pack(side=tk.LEFT, padx=(0, 8))
        
        ctk.CTkLabel(
            left_frame, 
            text="Ano:", 
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_primary"]
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        target_year_entry = ctk.CTkEntry(
            left_frame, 
            width=60, 
            font=ctk.CTkFont(size=10),
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"]
        )
        target_year_entry.insert(0, str(viewed_year))
        target_year_entry.pack(side=tk.LEFT)
        
        # Lado direito: botão Salvar
        save_btn_top = ctk.CTkButton(
            target_inner,
            text="Salvar",
            command=save_config,
            fg_color=COLORS["pastel_green"],
            hover_color=COLORS["pastel_green_hover"],
            text_color="#1a1a2e",
            width=100,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        save_btn_top.pack(side=tk.RIGHT)
        
        # Frame do calendário com navegação
        calendar_container = ctk.CTkFrame(main_frame, corner_radius=8, fg_color=COLORS["bg_card"])
        calendar_container.pack(fill=tk.X, pady=(0, 10))
        
        ctk.CTkLabel(
            calendar_container, 
            text="Selecione o dia de início da semana:", 
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor=tk.W, padx=10, pady=(8, 4))
        
        # Navegação do calendário
        nav_frame = ctk.CTkFrame(calendar_container, fg_color="transparent")
        nav_frame.pack(fill=tk.X, padx=10)
        
        cal_month_label = tk.StringVar(value="")
        
        def prev_month():
            m = calendar_month.get()
            y = calendar_year.get()
            if m == 1:
                calendar_month.set(12)
                calendar_year.set(y - 1)
            else:
                calendar_month.set(m - 1)
            update_mini_calendar()
        
        def next_month():
            m = calendar_month.get()
            y = calendar_year.get()
            if m == 12:
                calendar_month.set(1)
                calendar_year.set(y + 1)
            else:
                calendar_month.set(m + 1)
            update_mini_calendar()
        
        prev_btn = ctk.CTkButton(
            nav_frame, text="◀", width=40, height=26,
            command=prev_month,
            fg_color=COLORS["tool_purple"],
            hover_color=COLORS["tool_purple_hover"],
            font=ctk.CTkFont(size=10)
        )
        prev_btn.pack(side=tk.LEFT)
        
        month_display = ctk.CTkLabel(
            nav_frame, 
            textvariable=cal_month_label, 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["accent_pink"]
        )
        month_display.pack(side=tk.LEFT, expand=True)
        
        next_btn = ctk.CTkButton(
            nav_frame, text="▶", width=40, height=26,
            command=next_month,
            fg_color=COLORS["tool_purple"],
            hover_color=COLORS["tool_purple_hover"],
            font=ctk.CTkFont(size=10)
        )
        next_btn.pack(side=tk.RIGHT)
        
        # Grid do calendário
        calendar_inner_frame = ctk.CTkFrame(calendar_container, fg_color="transparent")
        calendar_inner_frame.pack(padx=10, pady=5)
        
        # Label de data selecionada
        selected_label = ctk.CTkLabel(
            calendar_container, 
            text="Clique em um dia para selecionar",
            text_color=COLORS["text_secondary"],
            font=ctk.CTkFont(size=9)
        )
        selected_label.pack(pady=(0, 8))
        
        def update_mini_calendar():
            """Atualiza o mini calendário."""
            for widget in calendar_inner_frame.winfo_children():
                widget.destroy()
            calendar_buttons.clear()
            
            month_idx = calendar_month.get()
            year = calendar_year.get()
            
            # Atualiza label do mês
            month_name = MONTH_NUMBER_TO_NAME.get(month_idx, f"Mês {month_idx}")
            cal_month_label.set(f"{month_name} {year}")
            
            # Cabeçalho dos dias
            weekday_labels_header = ["S", "T", "Q", "Q", "S", "S", "D"]
            for col, label in enumerate(weekday_labels_header):
                lbl = ctk.CTkLabel(
                    calendar_inner_frame, 
                    text=label, 
                    font=ctk.CTkFont(size=9, weight="bold"), 
                    width=36,
                    text_color="#495057"
                )
                lbl.grid(row=0, column=col, padx=1, pady=1)
            
            # Obtém dias do mês
            cal = calendar.Calendar(firstweekday=0)
            month_days = cal.monthdayscalendar(year, month_idx)
            
            # Calcula dias do mês anterior
            if month_idx == 1:
                prev_month_num = 12
                prev_year = year - 1
            else:
                prev_month_num = month_idx - 1
                prev_year = year
            
            _, prev_month_last_day = calendar.monthrange(prev_year, prev_month_num)
            
            # Calcula dias do próximo mês
            if month_idx == 12:
                next_month_num = 1
                next_year = year + 1
            else:
                next_month_num = month_idx + 1
                next_year = year
            
            today = date.today()
            
            for row_idx, week in enumerate(month_days, start=1):
                for col_idx, day in enumerate(week):
                    if day == 0:
                        # Dia de outro mês
                        if row_idx == 1:
                            # Primeira semana - dias do mês anterior
                            days_before = week.count(0)
                            actual_day = prev_month_last_day - (days_before - col_idx - 1)
                            actual_month = prev_month_num
                            actual_year = prev_year
                        else:
                            # Última semana - dias do próximo mês
                            zero_count = 0
                            for d in week:
                                if d == 0:
                                    zero_count += 1
                                else:
                                    zero_count = 0
                            actual_day = col_idx - (6 - zero_count)
                            actual_month = next_month_num
                            actual_year = next_year
                        
                        is_other_month = True
                    else:
                        actual_day = day
                        actual_month = month_idx
                        actual_year = year
                        is_other_month = False
                    
                    current_day_date = date(actual_year, actual_month, actual_day)
                    
                    # Define cor do botão
                    if current_day_date == today:
                        fg_color = "#28a745"
                        text_color = "#ffffff"
                        hover_color = "#218838"
                    elif is_other_month:
                        fg_color = "#e9ecef"
                        text_color = "#6c757d"
                        hover_color = "#dee2e6"
                    elif col_idx >= 5:  # Fim de semana
                        fg_color = "#fff3cd"
                        text_color = "#856404"
                        hover_color = "#ffeeba"
                    else:
                        fg_color = "#ffffff"
                        text_color = "#212529"
                        hover_color = "#e2e6ea"
                    
                    btn = ctk.CTkButton(
                        calendar_inner_frame,
                        text=str(actual_day),
                        width=36,
                        height=28,
                        fg_color=fg_color,
                        text_color=text_color,
                        hover_color=hover_color,
                        corner_radius=4,
                        font=ctk.CTkFont(size=9),
                        command=lambda d=actual_day, m=actual_month, y=actual_year: select_date(d, m, y)
                    )
                    btn.grid(row=row_idx, column=col_idx, padx=1, pady=1)
                    calendar_buttons.append((btn, actual_day, actual_month, actual_year, is_other_month, col_idx >= 5))
        
        def select_date(day: int, month: int, year: int):
            """
            Seleciona uma data no mini calendário e salva automaticamente a configuração.
            
            O salvamento automático ocorre quando todos os campos estão preenchidos.
            """
            selected_date = date(year, month, day)
            selected_start_date.set(selected_date.strftime("%Y-%m-%d"))
            
            # Atualiza visual dos botões
            for btn, d, m, y, is_other, is_weekend in calendar_buttons:
                if d == day and m == month and y == year:
                    btn.configure(fg_color="#007bff", text_color="#ffffff")
                else:
                    # Restaura cor original
                    current_day_date = date(y, m, d)
                    today = date.today()
                    
                    if current_day_date == today:
                        fg = "#28a745"
                        tc = "#ffffff"
                    elif is_other:
                        fg = "#e9ecef"
                        tc = "#6c757d"
                    elif is_weekend:
                        fg = "#fff3cd"
                        tc = "#856404"
                    else:
                        fg = "#ffffff"
                        tc = "#212529"
                    
                    btn.configure(fg_color=fg, text_color=tc)
            
            # Atualiza label
            weekday_names = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
            weekday_name = weekday_names[selected_date.weekday()]
            month_name = MONTH_NUMBER_TO_NAME.get(selected_date.month, "")
            
            selected_label.configure(
                text=f"{selected_date.day:02d}/{month_name[:3]}/{selected_date.year} ({weekday_name[:3]}) - Preencha os campos e clique 'Adicionar Semana'",
                text_color="#007bff"
            )
            
            # NÃO salva automaticamente - usuário deve clicar em "Adicionar Semana"
        
        # Frame para configuração da semana
        week_config_frame = ctk.CTkFrame(main_frame, corner_radius=8, fg_color=COLORS["bg_card"])
        week_config_frame.pack(fill=tk.X, pady=(0, 10))
        
        config_inner = ctk.CTkFrame(week_config_frame, fg_color="transparent")
        config_inner.pack(padx=10, pady=8)
        
        # Número da semana no mês
        ctk.CTkLabel(
            config_inner, 
            text="Semana:", 
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, sticky=tk.W, pady=3, padx=(0, 5))
        
        week_number_combo = ctk.CTkComboBox(
            config_inner,
            values=["S1", "S2", "S3", "S4", "S5"],
            width=60,
            state="readonly",
            font=ctk.CTkFont(size=10),
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            button_color=COLORS["tool_purple"],
            button_hover_color=COLORS["tool_purple_hover"],
            dropdown_fg_color=COLORS["bg_card"]
        )
        week_number_combo.set("S1")
        week_number_combo.grid(row=0, column=1, padx=(0, 15), pady=3)
        
        # Quantidade de dias de trabalho
        ctk.CTkLabel(
            config_inner, 
            text="Dias:", 
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=2, sticky=tk.W, pady=3, padx=(0, 5))
        
        work_days_combo = ctk.CTkComboBox(
            config_inner,
            values=["1", "2", "3", "4", "5", "6", "7"],
            width=50,
            state="readonly",
            font=ctk.CTkFont(size=10),
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            button_color=COLORS["tool_purple"],
            button_hover_color=COLORS["tool_purple_hover"],
            dropdown_fg_color=COLORS["bg_card"]
        )
        work_days_combo.set("7")
        work_days_combo.grid(row=0, column=3, pady=3)
        
        # Meta semanal (novo campo)
        ctk.CTkLabel(
            config_inner, 
            text="Meta:", 
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=4, sticky=tk.W, pady=3, padx=(15, 5))
        
        weekly_target_entry = ctk.CTkEntry(
            config_inner,
            width=60,
            height=26,
            justify="center",
            font=ctk.CTkFont(size=10),
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            placeholder_text="0"
        )
        weekly_target_entry.grid(row=0, column=5, pady=3)
        
        # Frame para semanas configuradas
        configured_frame = ctk.CTkFrame(main_frame, corner_radius=8, fg_color=COLORS["bg_card"])
        configured_frame.pack(fill=tk.X, pady=(0, 10))
        
        ctk.CTkLabel(
            configured_frame, 
            text="Semanas Configuradas:", 
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor=tk.W, padx=10, pady=(8, 4))
        
        # Lista de semanas configuradas usando CTkTextbox para melhor visualização
        configured_list_text = ctk.CTkTextbox(
            configured_frame, 
            height=80,
            font=ctk.CTkFont(size=9),
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            corner_radius=4,
            state="disabled"
        )
        configured_list_text.pack(fill=tk.X, padx=10, pady=(0, 8))
        
        # Lista oculta para seleção (usada para deletar)
        configured_list = tk.Listbox(
            configured_frame, 
            height=0,
            font=("Segoe UI", 1),
            bg="#ffffff",
            borderwidth=0,
            highlightthickness=0
        )
        # Não mostra, apenas para manter compatibilidade
        
        # Frame de status/feedback
        status_frame = ctk.CTkFrame(main_frame, corner_radius=6, fg_color=COLORS["bg_input"])
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="Selecione uma data no calendário para configurar a semana",
            text_color=COLORS["text_secondary"],
            font=ctk.CTkFont(size=9)
        )
        status_label.pack(pady=6, padx=10)
        
        def get_target_month_year():
            """Obtém mês e ano alvo da configuração."""
            month_name = target_month_combo.get()
            year_str = target_year_entry.get()
            
            month_idx = MONTH_NAME_TO_NUMBER.get(month_name, viewed_month)
            try:
                year_val = int(year_str)
            except ValueError:
                year_val = viewed_year
            
            return month_idx, year_val
        
        def refresh_configured_list():
            """Atualiza lista de semanas configuradas."""
            configured_list.delete(0, tk.END)
            month_idx, year = get_target_month_year()
            
            configs = self.counter.get_all_week_configs_for_month(year, month_idx)
            
            # Atualiza o textbox
            configured_list_text.configure(state="normal")
            configured_list_text.delete("1.0", tk.END)
            
            if not configs:
                configured_list_text.insert(tk.END, "Nenhuma semana configurada para este mês.\n")
                configured_list_text.insert(tk.END, "Configure selecionando uma data no calendário acima.")
            else:
                month_name = MONTH_NUMBER_TO_NAME.get(month_idx, "")
                configured_list_text.insert(tk.END, f"Configurações para {month_name} {year}:\n\n")
                
                for config in configs:
                    start_date = config.get_start_date()
                    end_date = config.get_end_date()
                    color = WEEK_COLOR_NAMES.get(config.week_in_month, "")
                    
                    # Formata mês da data de início
                    start_month_name = MONTH_NUMBER_TO_NAME.get(start_date.month, "")[:3]
                    end_month_name = MONTH_NUMBER_TO_NAME.get(end_date.month, "")[:3]
                    
                    # Busca meta semanal configurada
                    week_target = self.counter.get_weekly_target(year, month_idx, config.week_in_month)
                    meta_info = f" | Meta: {week_target.expected}" if week_target.expected > 0 else ""
                    
                    text = (
                        f"  S{config.week_in_month} ({color}): "
                        f"{start_date.day:02d}/{start_month_name} → {end_date.day:02d}/{end_month_name} "
                        f"({config.work_days} dias){meta_info}\n"
                    )
                    configured_list_text.insert(tk.END, text)
                    configured_list.insert(tk.END, text.strip())
            
            configured_list_text.configure(state="disabled")
        
        def save_week_config():
            """Salva a configuração da semana e meta automaticamente."""
            if not selected_start_date.get():
                status_label.configure(
                    text="Selecione uma data de início no calendário primeiro", 
                    text_color=COLORS["pastel_red"]
                )
                return
            
            from datetime import datetime
            start_date = datetime.strptime(selected_start_date.get(), "%Y-%m-%d").date()
            
            # Extrai número da semana do combo
            week_text = week_number_combo.get()
            week_selection = int(week_text[1])  # Extrai número de "S1", "S2", etc.
            
            # Extrai dias de trabalho
            work_days = int(work_days_combo.get())  # Agora é só o número
            
            # Obtém mês/ano alvo
            month_idx, year = get_target_month_year()
            
            # Primeiro dia da semana baseado no dia selecionado
            first_weekday = start_date.weekday()
            
            # Salva configuração da semana
            self.counter.set_week_config(
                year=year,
                month=month_idx,
                week_in_month=week_selection,
                start_date=start_date,
                work_days=work_days,
                first_weekday=first_weekday
            )
            
            # Salva meta semanal se informada
            target_text = weekly_target_entry.get().strip()
            if target_text:
                try:
                    target_value = int(target_text)
                    if target_value >= 0:
                        self.counter.set_weekly_target(year, month_idx, week_selection, target_value)
                except ValueError:
                    pass  # Ignora valor inválido
            
            refresh_configured_list()
            
            end_date = start_date + timedelta(days=work_days - 1)
            
            # Feedback visual no status
            meta_info = f" | Meta: {target_text}" if target_text else ""
            success_msg = (
                f"S{week_selection} ({WEEK_COLOR_NAMES.get(week_selection, '')}) salva: "
                f"{start_date.strftime('%d/%m')} → {end_date.strftime('%d/%m')} ({work_days}d){meta_info}"
            )
            status_label.configure(text=success_msg, text_color=COLORS["pastel_green"])
            
            # Limpa seleção do calendário
            selected_start_date.set("")
            weekly_target_entry.delete(0, tk.END)
            selected_label.configure(
                text="Salvo! Selecione outra data ou feche.",
                text_color=COLORS["pastel_green"]
            )
        
        # Variável para armazenar semana selecionada para deletar
        selected_week_to_delete = tk.IntVar(value=0)
        
        def delete_selected_config():
            """Remove configuração selecionada."""
            month_idx, year = get_target_month_year()
            configs = self.counter.get_all_week_configs_for_month(year, month_idx)
            
            if not configs:
                status_label.configure(
                    text="Não há semanas configuradas para remover", 
                    text_color=COLORS["pastel_red"]
                )
                return
            
            # Pega o número da semana do combo
            week_text = week_number_combo.get()
            week_to_delete = int(week_text[1])  # S1, S2, etc.
            
            # Verifica se essa semana está configurada
            config_found = None
            for config in configs:
                if config.week_in_month == week_to_delete:
                    config_found = config
                    break
            
            if not config_found:
                status_label.configure(
                    text=f"S{week_to_delete} não está configurada. Selecione outra semana.", 
                    text_color=COLORS["pastel_orange"]
                )
                return
            
            self.counter.delete_week_config(year, month_idx, week_to_delete)
            refresh_configured_list()
            
            # Feedback visual
            status_label.configure(
                text=f"S{week_to_delete} removida com sucesso!", 
                text_color=COLORS["pastel_red"]
            )
        
        # Botões de ação (apenas Remover - Adicionar foi removido pois salvamento é automático)
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill=tk.X)
        
        # Botão "Adicionar Semana" para salvar a configuração
        add_week_btn = ctk.CTkButton(
            buttons_frame,
            text="Adicionar Semana",
            command=save_week_config,
            fg_color=COLORS["pastel_green"],
            hover_color=COLORS["pastel_green_hover"],
            text_color="#1a1a2e",
            width=140,
            height=30,
            font=ctk.CTkFont(size=10, weight="bold")
        )
        add_week_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_btn = ctk.CTkButton(
            buttons_frame,
            text="Remover Semana",
            command=delete_selected_config,
            fg_color=COLORS["pastel_red"],
            hover_color=COLORS["pastel_red_hover"],
            text_color="#1a1a2e",
            width=140,
            height=30,
            font=ctk.CTkFont(size=10)
        )
        delete_btn.pack(side=tk.LEFT)
        
        # Atualiza quando mês/ano alvo mudar
        def on_target_change(*args):
            refresh_configured_list()
            # Atualiza calendário para o mês/ano alvo
            target_m, target_y = get_target_month_year()
            calendar_month.set(target_m)
            calendar_year.set(target_y)
            update_mini_calendar()
        
        target_month_combo.configure(command=lambda x: on_target_change())
        target_year_entry.bind("<Return>", lambda e: on_target_change())
        target_year_entry.bind("<FocusOut>", lambda e: on_target_change())
        
        # Salvar automaticamente ao fechar
        def on_dialog_close():
            self.counter.save()
            self._render_calendar()
            self._refresh_weekly_info()
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
        
        # Inicializa
        update_mini_calendar()
        refresh_configured_list()
        
        dialog.bind('<Escape>', lambda e: on_dialog_close())
    
    def _rebuild_calendar_headers(self) -> None:
        """Reconstrói os cabeçalhos dos dias da semana com a nova configuração."""
        # Remove cabeçalhos existentes (primeira linha)
        for widget in self.calendar_frame.winfo_children():
            if int(widget.grid_info()['row']) == 0:
                widget.destroy()
        
        # Cria novos cabeçalhos
        weekday_labels = get_weekday_labels(self.counter.first_weekday)
        for col, label in enumerate(weekday_labels):
            header = tk.Label(self.calendar_frame, text=label, font=("Segoe UI", 9, "bold"))
            header.grid(row=0, column=col, padx=3, pady=2)
    
    def _on_closing(self) -> None:
        """Gerencia o fechamento da aplicação."""
        # DEPRECATED - Visualização HTML removida
        # if self.html_viewer:
        #     self.html_viewer.stop()
        #     self.html_viewer.create_close_signal()
        
        # Salva os dados finais
        try:
            self.counter.save()
            current_month = MONTH_NAME_TO_NUMBER[self.month_var.get()]
            self.counter.save_last_period(int(self.year_var.get()), current_month)
        except Exception:
            pass
        
        # Pega o caminho do XLSX usando o export_path configurado pelo usuário
        # Nome: relatorio_rts_{mes}.xlsx
        current_month = MONTH_NAME_TO_NUMBER[self.month_var.get()]
        month_name = self.month_var.get().lower()
        xlsx_path = Path(self.counter.get_export_path(f"relatorio_rts_{month_name}.xlsx"))
        
        if xlsx_path.exists():
            # Mostra diálogo perguntando se quer abrir o relatório
            from tkinter import messagebox
            response = messagebox.askyesno(
                "Relatório Gerado",
                "Deseja abrir o relatório Excel gerado?\n\n"
                f"Arquivo: {xlsx_path}",
                icon="question"
            )
            
            if response:
                # Abre o arquivo XLSX
                try:
                    import os
                    os.startfile(str(xlsx_path))
                except Exception:
                    pass
        
        # Fecha a aplicação
        self.root.destroy()


def run_app(data_path: Path | str | None = None, config_path: Path | str | None = None) -> None:
    """Inicializa o contador gráfico com caminhos personalizados opcionalmente."""
    data_path = Path(data_path) if data_path else Path("contador_retweets.csv")
    config_arg = Path(config_path) if config_path else None
    counter = CalendarCounter(data_path=data_path, config_path=config_arg)
    
    # Usa CustomTkinter para interface moderna
    root = ctk.CTk()
    CounterApp(root, counter)
    root.mainloop()


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
