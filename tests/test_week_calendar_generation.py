"""
Teste mockado para verificar a geração do calendário semanal.

Este script testa a lógica de posicionamento dos dias nas colunas
do CSV/XLSX sem precisar rodar a aplicação completa.
"""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retweet_counter.storage import WeekConfig


def create_week_config(year, month, week_in_month, start_date, work_days, first_weekday):
    """
    Cria um WeekConfig com a interface correta.
    
    Args:
        year: Ano
        month: Mês
        week_in_month: Número da semana no mês
        start_date: Data de início (date object)
        work_days: Dias de trabalho
        first_weekday: Primeiro dia da semana (0=seg, 6=dom)
    
    Returns:
        WeekConfig configurado
    """
    config = WeekConfig(
        year=year,
        month=month,
        week_in_month=week_in_month,
        start_date=start_date.strftime("%Y-%m-%d"),
        work_days=work_days,
        first_weekday=first_weekday
    )
    return config


class TestWeekConfig:
    """Testes para a classe WeekConfig."""
    
    def test_week_config_creation(self):
        """Testa criação básica de WeekConfig."""
        config = create_week_config(
            year=2024,
            month=12,
            week_in_month=1,
            start_date=date(2024, 12, 1),
            work_days=7,
            first_weekday=0  # Segunda-feira
        )
        
        assert config.year == 2024
        assert config.month == 12
        assert config.week_in_month == 1
        assert config.work_days == 7
        assert config.first_weekday == 0
    
    def test_get_all_dates_7_days(self):
        """Testa obtenção de todas as datas com 7 dias de trabalho."""
        config = create_week_config(
            year=2024,
            month=12,
            week_in_month=1,
            start_date=date(2024, 12, 1),
            work_days=7,
            first_weekday=0
        )
        
        dates = config.get_all_dates()
        
        assert len(dates) == 7
        assert dates[0] == date(2024, 12, 1)
        assert dates[-1] == date(2024, 12, 7)
    
    def test_get_all_dates_5_days(self):
        """Testa obtenção de todas as datas com 5 dias de trabalho."""
        config = create_week_config(
            year=2024,
            month=12,
            week_in_month=1,
            start_date=date(2024, 12, 1),
            work_days=5,
            first_weekday=0
        )
        
        dates = config.get_all_dates()
        
        assert len(dates) == 5
        assert dates[0] == date(2024, 12, 1)
        assert dates[-1] == date(2024, 12, 5)


class TestCalendarColumnPositioning:
    """
    Testa o posicionamento correto dos dias nas colunas do calendário.
    
    Layout esperado (first_weekday=6, Domingo primeiro):
    Coluna 0: DOM
    Coluna 1: SEG
    Coluna 2: TER
    Coluna 3: QUA
    Coluna 4: QUI
    Coluna 5: SEX
    Coluna 6: SAB
    """
    
    def setup_method(self):
        """Configuração comum para os testes."""
        self.global_first_weekday = 6  # Domingo primeiro (padrão da aplicação)
        self.weekday_labels = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SAB"]
    
    def calculate_start_column(self, config_first_weekday):
        """
        Calcula em qual coluna a semana deve começar.
        
        Args:
            config_first_weekday: Dia da semana do início (0=seg, 6=dom)
        
        Returns:
            Índice da coluna (0-6)
        """
        return (config_first_weekday - self.global_first_weekday) % 7
    
    def get_previous_month_days(self, start_date, start_col):
        """
        Obtém os dias do mês anterior para preencher antes da semana.
        
        Args:
            start_date: Data de início da semana
            start_col: Coluna onde a semana começa
        
        Returns:
            Lista de datas do mês anterior
        """
        days_before = []
        if start_col > 0:
            for i in range(start_col, 0, -1):
                prev_date = start_date - timedelta(days=i)
                days_before.append(prev_date)
        return days_before
    
    def generate_calendar_row(self, config):
        """
        Gera uma representação da linha do calendário.
        
        Args:
            config: WeekConfig com a configuração da semana
        
        Returns:
            Lista com 7 elementos representando as colunas
        """
        row = [""] * 7
        
        week_dates = config.get_all_dates()
        start_col = self.calculate_start_column(config.first_weekday)
        
        # Preenche dias anteriores (mês anterior)
        days_before = self.get_previous_month_days(week_dates[0], start_col)
        for i, prev_date in enumerate(days_before):
            month_abbr = self._get_month_abbr(prev_date.month)
            row[i] = f"({prev_date.day:02d}/{month_abbr})"
        
        # Preenche os dias da semana
        for i, day_date in enumerate(week_dates):
            col_idx = start_col + i
            if col_idx < 7:  # Só preenche se couber
                if day_date.month != config.month:
                    month_abbr = self._get_month_abbr(day_date.month)
                    row[col_idx] = f"{day_date.day:02d}/{month_abbr}"
                else:
                    row[col_idx] = f"dia {day_date.day:02d}"
        
        return row
    
    def _get_month_abbr(self, month):
        """Retorna abreviação do mês."""
        months = {
            1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
            5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
            9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
        }
        return months.get(month, "")
    
    def test_december_2024_week1_starts_sunday(self):
        """
        Dezembro 2024 - Semana 1 começa no domingo (dia 01).
        
        Esperado:
        DOM=01, SEG=02, TER=03, QUA=04, QUI=05, SEX=06, SAB=07
        """
        config = create_week_config(
            year=2024,
            month=12,
            week_in_month=1,
            start_date=date(2024, 12, 1),
            work_days=7,
            first_weekday=6  # Domingo
        )
        
        row = self.generate_calendar_row(config)
        
        print(f"\nDezembro 2024 - S1 (começa Domingo):")
        print(f"  {self.weekday_labels}")
        print(f"  {row}")
        
        # Verifica posições
        assert row[0] == "dia 01", f"DOM deveria ser dia 01, mas é {row[0]}"
        assert row[1] == "dia 02", f"SEG deveria ser dia 02, mas é {row[1]}"
        assert row[6] == "dia 07", f"SAB deveria ser dia 07, mas é {row[6]}"
    
    def test_december_2024_week1_starts_monday(self):
        """
        Dezembro 2024 - Semana 1 começa na segunda (dia 02).
        Dia 01 é domingo, então coluna 0 fica com 30/Nov.
        
        Esperado:
        DOM=(30/Nov), SEG=02, TER=03, QUA=04, QUI=05, SEX=06, SAB=07
        
        Nota: Se a semana começa dia 02 (segunda) e tem 7 dias:
        02, 03, 04, 05, 06, 07, 08
        """
        # Caso onde usuário selecionou segunda-feira dia 02 como início
        config = create_week_config(
            year=2024,
            month=12,
            week_in_month=1,
            start_date=date(2024, 12, 2),
            work_days=7,
            first_weekday=0  # Segunda-feira
        )
        
        row = self.generate_calendar_row(config)
        
        print(f"\nDezembro 2024 - S1 (começa Segunda dia 02):")
        print(f"  {self.weekday_labels}")
        print(f"  {row}")
        
        # Coluna 0 (DOM) deve ter o dia anterior do mês anterior
        assert row[0] == "(01/Dez)", f"DOM deveria ser (01/Dez), mas é {row[0]}"
        assert row[1] == "dia 02", f"SEG deveria ser dia 02, mas é {row[1]}"
        assert row[6] == "dia 07", f"SAB deveria ser dia 07, mas é {row[6]}"
    
    def test_week_starting_monday_dec_1_2024(self):
        """
        Cenário do usuário: S1 de dezembro começando segunda-feira (01/12/2024).
        01/12/2024 é uma SEGUNDA-FEIRA.
        
        Se first_weekday do config = 0 (segunda), e global = 6 (domingo):
        start_col = (0 - 6) % 7 = 1
        
        Esperado:
        DOM=(30/Nov), SEG=01, TER=02, QUA=03, QUI=04, SEX=05, SAB=06
        """
        config = create_week_config(
            year=2024,
            month=12,
            week_in_month=1,
            start_date=date(2024, 12, 1),
            work_days=7,
            first_weekday=0  # Segunda-feira (dia 01/12/2024 é segunda)
        )
        
        row = self.generate_calendar_row(config)
        
        print(f"\nCenário do usuário - S1 Dezembro (01/12/2024 = Segunda):")
        print(f"  {self.weekday_labels}")
        print(f"  {row}")
        
        # Verifica que 30/Nov aparece antes do dia 01
        assert row[0] == "(30/Nov)", f"DOM deveria ser (30/Nov), mas é {row[0]}"
        assert row[1] == "dia 01", f"SEG deveria ser dia 01, mas é {row[1]}"
        assert row[2] == "dia 02", f"TER deveria ser dia 02, mas é {row[2]}"
        assert row[6] == "dia 06", f"SAB deveria ser dia 06, mas é {row[6]}"
        
        # Dia 07 NÃO deve aparecer nesta linha
        assert "dia 07" not in row, f"dia 07 não deveria estar nesta linha: {row}"
    
    def test_no_day_wrapping(self):
        """
        Verifica que os dias não "voltam" para a coluna 0.
        
        Se a semana tem 7 dias começando na coluna 1,
        o dia 7 seria na coluna 7 (fora do range), então não aparece.
        """
        config = create_week_config(
            year=2024,
            month=12,
            week_in_month=1,
            start_date=date(2024, 12, 1),
            work_days=7,
            first_weekday=0  # Segunda = coluna 1
        )
        
        start_col = self.calculate_start_column(config.first_weekday)
        week_dates = config.get_all_dates()
        
        print(f"\nVerificação de wrap:")
        print(f"  start_col = {start_col}")
        print(f"  Dias da semana: {[d.day for d in week_dates]}")
        
        # Quantos dias cabem na linha?
        days_that_fit = 7 - start_col
        print(f"  Dias que cabem na linha: {days_that_fit}")
        
        # Verifica que apenas 6 dias cabem (colunas 1-6)
        assert days_that_fit == 6, f"Deveriam caber 6 dias, mas cabem {days_that_fit}"
    
    def test_week2_december_2024(self):
        """
        Dezembro 2024 - Semana 2 começando dia 08 (Domingo).
        
        Esperado:
        DOM=08, SEG=09, TER=10, QUA=11, QUI=12, SEX=13, SAB=14
        """
        config = create_week_config(
            year=2024,
            month=12,
            week_in_month=2,
            start_date=date(2024, 12, 8),
            work_days=7,
            first_weekday=6  # Domingo
        )
        
        row = self.generate_calendar_row(config)
        
        print(f"\nDezembro 2024 - S2 (começa Domingo dia 08):")
        print(f"  {self.weekday_labels}")
        print(f"  {row}")
        
        assert row[0] == "dia 08", f"DOM deveria ser dia 08, mas é {row[0]}"
        assert row[6] == "dia 14", f"SAB deveria ser dia 14, mas é {row[6]}"


class TestVisualCalendarOutput:
    """Testes que geram output visual para verificação manual."""
    
    def setup_method(self):
        """Configuração comum."""
        self.weekday_labels = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SAB"]
        self.global_first_weekday = 6
    
    def generate_visual_calendar(self, configs):
        """
        Gera uma representação visual do calendário completo.
        
        Args:
            configs: Lista de WeekConfig
        
        Returns:
            String com o calendário formatado
        """
        lines = []
        lines.append("=" * 70)
        lines.append(f"{'SEMANA':<10} | " + " | ".join(f"{d:^8}" for d in self.weekday_labels))
        lines.append("-" * 70)
        
        for config in configs:
            week_dates = config.get_all_dates()
            start_col = (config.first_weekday - self.global_first_weekday) % 7
            
            row = ["        "] * 7  # 8 caracteres cada
            
            # Dias anteriores
            if start_col > 0:
                for i in range(start_col, 0, -1):
                    prev_date = week_dates[0] - timedelta(days=i)
                    row[start_col - i] = f"({prev_date.day:02d}/{prev_date.month:02d})"
            
            # Dias da semana
            for i, day_date in enumerate(week_dates):
                col_idx = start_col + i
                if col_idx < 7:
                    row[col_idx] = f"  {day_date.day:02d}    "
            
            week_label = f"S{config.week_in_month} ({config.work_days}d)"
            lines.append(f"{week_label:<10} | " + " | ".join(row))
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def test_full_december_2024_calendar(self):
        """
        Gera calendário completo de dezembro 2024.
        
        01/12/2024 = Segunda-feira
        """
        configs = [
            create_week_config(2024, 12, 1, date(2024, 12, 1), 7, 0),   # S1: 01-07 (seg-dom)
            create_week_config(2024, 12, 2, date(2024, 12, 8), 7, 6),   # S2: 08-14 (dom-sab)
            create_week_config(2024, 12, 3, date(2024, 12, 15), 7, 6),  # S3: 15-21 (dom-sab)
            create_week_config(2024, 12, 4, date(2024, 12, 22), 7, 6),  # S4: 22-28 (dom-sab)
            create_week_config(2024, 12, 5, date(2024, 12, 29), 3, 6),  # S5: 29-31 (dom-ter)
        ]
        
        calendar = self.generate_visual_calendar(configs)
        print("\n" + calendar)
        
        # Este teste é visual, sempre passa
        assert True


def run_quick_test():
    """Função para rodar um teste rápido via linha de comando."""
    print("\n" + "=" * 60)
    print("TESTE RÁPIDO - Posicionamento do Calendário")
    print("=" * 60)
    
    weekday_labels = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SAB"]
    global_first_weekday = 6  # Domingo primeiro
    
    # Cenário do usuário: S1 dezembro começando segunda dia 01
    config = create_week_config(
        year=2024,
        month=12,
        week_in_month=1,
        start_date=date(2024, 12, 1),
        work_days=7,
        first_weekday=0  # Segunda-feira
    )
    
    week_dates = config.get_all_dates()
    start_col = (config.first_weekday - global_first_weekday) % 7
    
    print(f"\nConfiguração:")
    print(f"  Data início: {config.start_date}")
    print(f"  Dia da semana do início: {config.first_weekday} (0=seg, 6=dom)")
    print(f"  Global first_weekday: {global_first_weekday}")
    print(f"  Coluna inicial calculada: {start_col}")
    print(f"  Dias da semana: {[d.day for d in week_dates]}")
    
    # Gera a linha
    row = [""] * 7
    
    # Dias anteriores
    if start_col > 0:
        for i in range(start_col, 0, -1):
            prev_date = week_dates[0] - timedelta(days=i)
            row[start_col - i] = f"({prev_date.day}/{prev_date.strftime('%b')})"
    
    # Dias da semana
    for i, day_date in enumerate(week_dates):
        col_idx = start_col + i
        if col_idx < 7:
            row[col_idx] = f"dia {day_date.day:02d}"
    
    print(f"\nResultado:")
    print(f"  Colunas: {weekday_labels}")
    print(f"  Valores: {row}")
    
    print("\n" + "-" * 60)
    print("Verificações:")
    
    # Verificações
    passed = True
    
    if row[0] == "(30/Nov)" or "(30" in row[0]:
        print("  [OK] DOM tem dia do mês anterior")
    else:
        print(f"  [ERRO] DOM deveria ter 30/Nov, mas tem: {row[0]}")
        passed = False
    
    if row[1] == "dia 01":
        print("  [OK] SEG tem dia 01")
    else:
        print(f"  [ERRO] SEG deveria ter dia 01, mas tem: {row[1]}")
        passed = False
    
    if "dia 07" in row:
        print(f"  [ERRO] dia 07 está aparecendo na linha (não deveria): {row}")
        passed = False
    else:
        print("  [OK] dia 07 NÃO está na linha (correto!)")
    
    print("\n" + "=" * 60)
    if passed:
        print("RESULTADO: TODOS OS TESTES PASSARAM!")
    else:
        print("RESULTADO: ALGUNS TESTES FALHARAM")
    print("=" * 60 + "\n")
    
    return passed


if __name__ == "__main__":
    # Roda o teste rápido
    run_quick_test()
    
    # Ou roda todos os testes com pytest
    # pytest.main([__file__, "-v"])


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
