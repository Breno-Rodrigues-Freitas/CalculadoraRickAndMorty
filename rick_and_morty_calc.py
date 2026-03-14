#!/usr/bin/env python3
"""
Rick & Morty Themed Calculator (tkinter) - Versão Melhorada
Salve como: rick_and_morty_calc.py
Execute: python rick_and_morty_calc.py
"""

import tkinter as tk
from tkinter import font, messagebox
import ast
import operator
import random
import os
import re

# ---------- Configurações de tema (MAIS CONTRASTE) -----------
BG = "#000000"           # fundo preto (maior contraste)
PANEL = "#1a1a1a"        # painel cinza escuro
NEON_GREEN = "#00FF00"   # verde neon mais brilhante
NEON_CYAN = "#00FFFF"    # ciano neon
ACCENT = "#FF00FF"       # magenta (mais visível)
TEXT = "#FFFFFF"         # texto branco puro
BUTTON_BG = "#333333"    # fundo dos botões
BUTTON_ACTIVE = "#555555" # botão ativo

# Frases aleatórias estilo Rick (mais curtas para caber)
RICK_QUOTES = [
    "Wubba Lubba Dub Dub!",
    "Get Schwifty!",
    "I'm Mr. Meeseeks!",
    "Science, bitch!",
    "Pickle Riiick!",
    "Show me what you got!",
    "AIDS!",
    "Grasssss...",
    "And that's the waaaaay the news goes!",
    "Hit the sack, Jack!"
]

# Frases de erro
ERROR_QUOTES = [
    "Uh oh! Erro, Morty!",
    "W-w-what happened?",
    "Existence is pain!",
    "This is worse than Pickle Rick!",
    "Calculator broke!"
]

# ---------- Avaliador seguro de expressões ----------
ALLOWED_BINOP = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}

ALLOWED_UNARYOP = {
    ast.UAdd: lambda x: x,
    ast.USub: operator.neg,
}

def safe_eval(expr: str):
    """Avalia expressões numéricas de forma segura usando ast."""
    expr = expr.strip()
    if not expr:
        raise ValueError("Expressão vazia")

    # Verificar se a expressão termina com operador
    if expr and expr[-1] in '+-*/%':
        expr = expr[:-1]
    
    try:
        node = ast.parse(expr, mode='eval')
    except SyntaxError:
        raise ValueError("Expressão inválida")

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)
            if op_type in ALLOWED_BINOP:
                return ALLOWED_BINOP[op_type](left, right)
            raise ValueError(f"Operador não permitido: {op_type}")
        if isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            op_type = type(node.op)
            if op_type in ALLOWED_UNARYOP:
                return ALLOWED_UNARYOP[op_type](operand)
            raise ValueError(f"Unary op não permitido: {op_type}")
        if isinstance(node, ast.Num):  # para Python < 3.8
            return node.n
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Constante não-numérica")
        if isinstance(node, ast.Call):
            raise ValueError("Chamadas de função não são permitidas")
        raise ValueError(f"Node não permitido: {type(node)}")

    return _eval(node)

def format_number(num):
    """Formata número removendo .0 quando inteiro"""
    if isinstance(num, float):
        if num.is_integer():
            return str(int(num))
        # Limitar casas decimais
        return f"{num:.10f}".rstrip('0').rstrip('.') if '.' in f"{num:.10f}" else str(num)
    return str(num)

# ---------- GUI ----------
class RickCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rick & Morty Calculator")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.geometry("400x600")
        
        # Sempre no topo para facilitar visualização
        self.attributes('-topmost', True)
        
        # Memória e histórico
        self.memory = 0
        self.history = []
        
        # Ícone opcional
        try:
            if os.path.exists("icon.ico"):
                self.iconbitmap("icon.ico")
        except Exception:
            pass

        # Fonts (MAIORES)
        self.big_font = font.Font(family="Arial", size=32, weight="bold")
        self.display_font = font.Font(family="Courier", size=24, weight="bold")
        self.medium_font = font.Font(family="Arial", size=16, weight="bold")
        self.small_font = font.Font(family="Arial", size=12, weight="bold")

        # Criar interface
        self.create_widgets()
        
        # Bindings de teclado
        self.setup_keyboard_bindings()

    def create_widgets(self):
        """Cria todos os widgets da interface"""
        
        # Top frame (frase do Rick)
        top = tk.Frame(self, bg=BG, height=60)
        top.pack(fill="x", pady=(10, 5))
        top.pack_propagate(False)

        # Frase do Rick (MAIOR)
        self.quote_var = tk.StringVar(value=random.choice(RICK_QUOTES))
        quote_label = tk.Label(top, textvariable=self.quote_var, bg=BG, fg=NEON_CYAN, 
                              font=self.medium_font, wraplength=380)
        quote_label.pack(expand=True, fill="both")

        # Display (MAIOR)
        self.display_var = tk.StringVar()
        display_frame = tk.Frame(self, bg=PANEL, padx=15, pady=15)
        display_frame.pack(fill="x", padx=15, pady=(5, 15))

        self.display = tk.Entry(display_frame, textvariable=self.display_var,
                              font=self.big_font, justify="right", bd=3, 
                              bg="#222222", fg=NEON_GREEN,
                              insertbackground=NEON_GREEN, relief="sunken")
        self.display.pack(fill="x", ipady=10)
        self.display_var.set("0")

        # Botões
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(padx=15, pady=(0, 10), expand=True, fill="both")

        buttons = [
            ['MC', 'MR', 'M+', 'M-'],
            ['C', '←', '%', '/'],
            ['7', '8', '9', '×'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['+/-', '0', '.', '=']  # '=' está aqui!
        ]

        # Mapeamento de caracteres para operações
        self.op_map = {
            '×': '*',
            '÷': '/',
            '←': '⌫'
        }

        for r, row in enumerate(buttons):
            row_frame = tk.Frame(btn_frame, bg=BG)
            row_frame.pack(fill="both", expand=True, pady=3)
            
            for c, char in enumerate(row):
                # Determinar o comando real
                cmd = self.op_map.get(char, char)
                
                btn = tk.Button(row_frame, text=char, 
                              command=lambda ch=cmd, original=char: self.on_button(ch, original),
                              font=self.display_font if char not in ['MC', 'MR', 'M+', 'M-'] else self.medium_font,
                              bd=3, relief="raised", cursor="hand2",
                              bg=self.get_button_color(char),
                              fg=self.get_button_text_color(char),
                              activebackground=self.get_button_active_color(char),
                              activeforeground=TEXT)
                
                btn.pack(side="left", padx=3, expand=True, fill="both")

        # Frame de histórico (maior)
        history_frame = tk.Frame(self, bg=BG)
        history_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        history_label = tk.Label(history_frame, text="HISTÓRICO:", bg=BG, fg=NEON_CYAN, 
                                font=self.small_font)
        history_label.pack(anchor="w")
        
        self.history_text = tk.Text(history_frame, height=2, bg="#222222", fg=TEXT, 
                                   font=self.small_font, wrap="word", state="disabled")
        self.history_text.pack(fill="x", pady=(2,0))

        # Bottom text (maior)
        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="x", padx=15, pady=(0, 10))
        hint = tk.Label(bottom, 
                       text="ENTER = Resultado  •  ESC = Limpar  •  MEM = M+ M- MR MC", 
                       bg=BG, fg="#AAAAAA", font=self.small_font)
        hint.pack(side="left")

    def get_button_color(self, char):
        """Retorna cor do botão baseado no caractere"""
        if char in "0123456789.":
            return "#006600"  # verde escuro
        elif char in "+-×÷%":
            return "#000066"  # azul escuro
        elif char in ['=', 'C', '←', '+/-']:
            return "#660066"  # roxo escuro
        elif char in ['MC', 'MR', 'M+', 'M-']:
            return "#444444"  # cinza escuro
        return "#333333"

    def get_button_text_color(self, char):
        """Retorna cor do texto do botão"""
        if char in "0123456789.":
            return NEON_GREEN
        elif char in "+-×÷%":
            return NEON_CYAN
        elif char in ['=', 'C', '←', '+/-']:
            return TEXT
        elif char in ['MC', 'MR', 'M+', 'M-']:
            return "#FFD700"  # dourado
        return TEXT

    def get_button_active_color(self, char):
        """Retorna cor do botão quando ativo"""
        if char in "0123456789.":
            return "#008800"
        elif char in "+-×÷%":
            return "#000088"
        elif char in ['=', 'C', '←', '+/-']:
            return "#880088"
        elif char in ['MC', 'MR', 'M+', 'M-']:
            return "#666666"
        return "#555555"

    def setup_keyboard_bindings(self):
        """Configura atalhos de teclado"""
        self.bind("<Return>", lambda e: self.on_button("="))
        self.bind("<BackSpace>", lambda e: self.on_button("⌫"))
        self.bind("<Escape>", lambda e: self.on_button("C"))
        self.bind("<Delete>", lambda e: self.on_button("C"))
        
        for k in "0123456789.":
            self.bind(k, lambda e, ch=k: self.on_button(ch))
        
        # Operadores
        self.bind("+", lambda e: self.on_button("+"))
        self.bind("-", lambda e: self.on_button("-"))
        self.bind("*", lambda e: self.on_button("*"))
        self.bind("/", lambda e: self.on_button("/"))
        self.bind("%", lambda e: self.on_button("%"))

    def on_button(self, ch, original=None):
        """Manipula clique nos botões"""
        cur = self.display_var.get()
        
        # Tratamento dos botões de memória
        if ch == "MC":
            self.memory = 0
            self.quote_var.set("Memória zerada!")
            return
        elif ch == "MR":
            self.display_var.set(format_number(self.memory))
            return
        elif ch == "M+":
            try:
                val = float(cur) if cur != "0" else 0
                self.memory += val
                self.quote_var.set(f"M: {format_number(self.memory)}")
            except ValueError:
                pass
            return
        elif ch == "M-":
            try:
                val = float(cur) if cur != "0" else 0
                self.memory -= val
                self.quote_var.set(f"M: {format_number(self.memory)}")
            except ValueError:
                pass
            return

        # Reset do display se for "0" e não for operador especial
        if cur == "0" and ch not in ("C", "⌫", "=", "+/-", ".", "MC", "MR", "M+", "M-"):
            cur = ""

        if ch == "C":
            self.display_var.set("0")
            self.quote_var.set(random.choice(RICK_QUOTES))
            return
            
        if ch == "⌫":
            new = cur[:-1]
            self.display_var.set(new if new else "0")
            return
            
        if ch == "=":
            if not cur or cur == "0" or cur in "+-*/%":
                self.quote_var.set("Digite algo, Morty!")
                return
                
            try:
                expr = self.display_var.get()
                # Converter × para * se necessário
                expr = expr.replace('×', '*')
                result = safe_eval(expr)
                formatted_result = format_number(result)
                self.display_var.set(formatted_result)
                
                # Adicionar ao histórico
                self.add_to_history(expr, formatted_result)
                
                # Frase de sucesso
                self.quote_var.set(random.choice([
                    "Boom!",
                    "Science!",
                    "Calculado!",
                    random.choice(RICK_QUOTES)
                ]))
            except Exception as e:
                self.display_var.set("ERRO")
                self.quote_var.set(random.choice(ERROR_QUOTES))
                messagebox.showerror("Erro!", 
                                   f"Deu ruim, Morty!\n{str(e)}")
            return
            
        if ch == "+/-":
            try:
                if cur.startswith("-"):
                    self.display_var.set(cur[1:])
                elif cur != "0":
                    self.display_var.set("-" + cur)
            except Exception:
                pass
            return

        # Para números e operadores
        if ch in '0123456789.':
            # Prevenir múltiplos pontos
            if ch == '.':
                last_number = re.split(r'[+\-*/%]', cur)[-1]
                if '.' in last_number:
                    return
        
        # Adicionar caractere
        new = cur + ch
        self.display_var.set(new)

    def add_to_history(self, expression, result):
        """Adiciona ao histórico"""
        self.history.append(f"{expression} = {result}")
        if len(self.history) > 5:
            self.history.pop(0)
        
        # Atualizar display do histórico
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, tk.END)
        for item in self.history:
            self.history_text.insert(tk.END, item + "\n")
        self.history_text.config(state="disabled")

# ---------- Executa ----------
if __name__ == "__main__":
    app = RickCalculator()
    app.mainloop()
