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

# ---------- Configurações de tema -----------
BG = "#0f1720"           # fundo escuro
PANEL = "#071017"        # painel dos botões
NEON_GREEN = "#7CFC00"   # verde neon
NEON_CYAN = "#00FFFF"    # ciano neon
ACCENT = "#9B59B6"       # roxo suave
TEXT = "#E6F9F2"         # texto claro
BUTTON_BG = "#1a2a3a"    # fundo dos botões
BUTTON_ACTIVE = "#2a3a4a" # botão ativo

# Frases aleatórias estilo Rick
RICK_QUOTES = [
    "Wubba Lubba Dub Dub!",
    "Get Schwifty!",
    "I'm Mr. Meeseeks, look at me!",
    "Sometimes science is more art than science.",
    "Existence is pain to a Meeseeks.",
    "Nobody exists on purpose, nobody belongs anywhere.",
    "Grasssss... tastes bad!",
    "Pickle Riiiiick!",
    "I don't get it, and I don't need to.",
    "Show me what you got!"
]

# Frases de erro
ERROR_QUOTES = [
    "Uh oh! Somethin' went wrong, Morty!",
    "This is worse than that time I turned myself into a pickle!",
    "Existence is pain!",
    "W-w-w-what the hell is this?",
    "I'm not programmed for this, Jerry!"
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
    """
    Avalia expressões numéricas de forma segura usando ast.
    Permite números, + - * / ** % e parênteses.
    """
    expr = expr.strip()
    if not expr:
        raise ValueError("Expressão vazia")

    # Verificar se a expressão termina com operador
    if expr[-1] in '+-*/%':
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
        self.geometry("380x560")
        
        # Memória e histórico
        self.memory = 0
        self.history = []
        
        # Ícone opcional
        try:
            if os.path.exists("icon.ico"):
                self.iconbitmap("icon.ico")
        except Exception:
            pass

        # Fonts
        self.big_font = font.Font(family="Helvetica", size=28, weight="bold")
        self.display_font = font.Font(family="Consolas", size=20)
        self.small_font = font.Font(family="Helvetica", size=10, weight="bold")
        self.history_font = font.Font(family="Consolas", size=10)

        # Criar interface
        self.create_widgets()
        
        # Bindings de teclado
        self.setup_keyboard_bindings()

    def create_widgets(self):
        """Cria todos os widgets da interface"""
        
        # Top frame (imagem opcional + frase)
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=(12, 6))

        # Tenta carregar imagem rick.png (opcional)
        self.image_label = tk.Label(top, bg=BG)
        self.image_label.pack()
        if os.path.exists("rick.png"):
            try:
                img = tk.PhotoImage(file="rick.png")
                img = img.subsample(max(1, img.width()//150), max(1, img.height()//100))
                self.image_label.configure(image=img)
                self.image_label.image = img
            except Exception:
                self.image_label.configure(text="🧪 Rick's Lab", fg=NEON_CYAN, bg=BG, font=self.big_font)

        # Frase do Rick
        self.quote_var = tk.StringVar(value=random.choice(RICK_QUOTES))
        quote_label = tk.Label(top, textvariable=self.quote_var, bg=BG, fg=NEON_CYAN, 
                              font=self.small_font, wraplength=350)
        quote_label.pack(pady=(6,0))

        # Display
        self.display_var = tk.StringVar()
        display_frame = tk.Frame(self, bg=PANEL, padx=10, pady=10)
        display_frame.pack(fill="x", padx=12, pady=(8, 12))

        self.display = tk.Entry(display_frame, textvariable=self.display_var,
                              font=self.big_font, justify="right", bd=0, bg=PANEL, fg=TEXT,
                              insertbackground=TEXT, state='readonly')
        self.display.pack(fill="x")
        self.display_var.set("0")

        # Botões
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(padx=12, pady=(0,12))

        buttons = [
            ['MC', 'MR', 'M+', 'M-'],
            ['C', '⌫', '%', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['+/-', '0', '.', '=']
        ]

        for r, row in enumerate(buttons):
            row_frame = tk.Frame(btn_frame, bg=BG)
            row_frame.pack(fill="x", pady=3)
            for c, char in enumerate(row):
                btn = tk.Button(row_frame, text=char, 
                              command=lambda ch=char: self.on_button(ch),
                              font=self.display_font if char not in ['MC', 'MR', 'M+', 'M-'] else self.small_font,
                              bd=0, relief="raised", cursor="hand2",
                              padx=8, pady=8, width=5)
                
                # Estilo por tipo
                if char in "0123456789.":
                    btn.configure(bg="#071e12", fg=NEON_GREEN, 
                                activebackground="#0b341f", activeforeground=NEON_GREEN)
                elif char in "+-*/%":
                    btn.configure(bg="#08202a", fg=NEON_CYAN, 
                                activebackground="#08333b", activeforeground=NEON_CYAN)
                elif char in ['=', 'C', '⌫', '+/-']:
                    btn.configure(bg=ACCENT, fg=TEXT, 
                                activebackground="#6f3f9a", activeforeground=TEXT)
                elif char in ['MC', 'MR', 'M+', 'M-']:
                    btn.configure(bg="#333333", fg="#FFD700", 
                                activebackground="#444444", activeforeground="#FFD700")
                
                btn.pack(side="left", padx=3, expand=True, fill="both")

        # Frame de histórico
        history_frame = tk.Frame(self, bg=BG)
        history_frame.pack(fill="x", padx=12, pady=(0,12))
        
        history_label = tk.Label(history_frame, text="Histórico:", bg=BG, fg=NEON_CYAN, 
                                font=self.small_font)
        history_label.pack(anchor="w")
        
        self.history_text = tk.Text(history_frame, height=2, bg=PANEL, fg=TEXT, 
                                   font=self.history_font, wrap="word", state="disabled")
        self.history_text.pack(fill="x", pady=(2,0))

        # Bottom text
        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="x", padx=12, pady=(0,12))
        hint = tk.Label(bottom, 
                       text="Enter para =  •  ESC limpa  •  Memória: M buttons", 
                       bg=BG, fg="#9aa7a3", font=self.small_font)
        hint.pack(side="left")

    def setup_keyboard_bindings(self):
        """Configura atalhos de teclado"""
        self.bind("<Return>", lambda e: self.on_button("="))
        self.bind("<BackSpace>", lambda e: self.on_button("⌫"))
        self.bind("<Escape>", lambda e: self.on_button("C"))
        self.bind("<Delete>", lambda e: self.on_button("C"))
        self.bind("<Control-c>", lambda e: self.on_button("C"))
        
        for k in "0123456789.":
            self.bind(k, lambda e, ch=k: self.on_button(ch))
        
        # Operadores com e sem shift
        self.bind("+", lambda e: self.on_button("+"))
        self.bind("-", lambda e: self.on_button("-"))
        self.bind("*", lambda e: self.on_button("*"))
        self.bind("/", lambda e: self.on_button("/"))
        self.bind("%", lambda e: self.on_button("%"))
        
        # Bind para qualquer tecla (atualizar frase aleatoriamente)
        self.bind("<Key>", self.on_keypress)

    def on_keypress(self, event):
        """Atualiza frase aleatoriamente ao digitar"""
        if random.random() < 0.02:  # 2% de chance
            self.quote_var.set(random.choice(RICK_QUOTES))

    def validate_expression(self, expr):
        """Valida a expressão antes de avaliar"""
        if not expr or expr in "0":
            return False
        
        # Verificar se há operadores consecutivos
        if re.search(r'[+\-*/%]{2,}', expr):
            return False
        
        # Verificar se termina com operador
        if expr[-1] in '+-*/%':
            return False
        
        return True

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

    def on_button(self, ch):
        cur = self.display_var.get()
        
        # Tratamento dos botões de memória
        if ch == "MC":  # Memory Clear
            self.memory = 0
            self.quote_var.set("Memória zerada, Morty!")
            return
        elif ch == "MR":  # Memory Recall
            self.display_var.set(format_number(self.memory))
            return
        elif ch == "M+":  # Memory Add
            try:
                val = float(cur) if cur != "0" else 0
                self.memory += val
                self.quote_var.set(f"Memória: {format_number(self.memory)}")
            except ValueError:
                pass
            return
        elif ch == "M-":  # Memory Subtract
            try:
                val = float(cur) if cur != "0" else 0
                self.memory -= val
                self.quote_var.set(f"Memória: {format_number(self.memory)}")
            except ValueError:
                pass
            return

        # Reset do display se for "0" e não for operador especial
        if cur == "0" and ch not in ("C", "⌫", "=", "+/-", ".", "MC", "MR", "M+", "M-"):
            cur = ""

        if ch == "C":
            self.display_var.set("0")
            return
            
        if ch == "⌫":
            new = cur[:-1]
            self.display_var.set(new if new else "0")
            return
            
        if ch == "=":
            if not self.validate_expression(cur):
                self.quote_var.set(random.choice(ERROR_QUOTES))
                return
                
            try:
                expr = self.display_var.get()
                result = safe_eval(expr)
                formatted_result = format_number(result)
                self.display_var.set(formatted_result)
                
                # Adicionar ao histórico
                self.add_to_history(expr, formatted_result)
                
                # Frase aleatória
                self.quote_var.set(random.choice([
                    "Science, bitch!",
                    "Boom! Big reveal!",
                    random.choice(RICK_QUOTES)
                ]))
            except Exception as e:
                self.display_var.set("Erro")
                self.quote_var.set(random.choice(ERROR_QUOTES))
                messagebox.showerror("Erro de Cálculo", 
                                   f"Morty, isso não faz sentido!\n{str(e)}")
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
        new = cur + ch
        
        # Prevenir múltiplos pontos decimais no mesmo número
        if ch == '.':
            # Verificar se o último número já tem ponto
            last_number = re.split(r'[+\-*/%]', new)[-1]
            if last_number.count('.') > 1:
                return
        
        # Prevenir operadores consecutivos
        if ch in '+-*/%' and cur and cur[-1] in '+-*/%':
            new = cur[:-1] + ch
        
        self.display_var.set(new)

# ---------- Executa ----------
if __name__ == "__main__":
    app = RickCalculator()
    app.mainloop()
