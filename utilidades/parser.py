"""Gramática matemática cerrada que construye objetos SymPy directamente."""
from collections.abc import Callable
from dataclasses import dataclass
import math
import re

import sympy as sp

from utilidades.validaciones import evaluar

TOKEN = re.compile(r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?|[A-Za-z]+|[()+*/^-]")
FUNCIONES = {"sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "exp": sp.exp,
             "log": sp.log, "ln": sp.log, "sqrt": sp.sqrt, "abs": sp.Abs}
CONSTANTES = {"pi": sp.pi, "e": sp.E}
OPERACIONES = {"+": sp.Add, "-": lambda a, b: sp.Add(a, sp.Mul(-1, b, evaluate=False), evaluate=False),
               "*": sp.Mul, "/": lambda a, b: sp.Mul(a, sp.Pow(b, -1, evaluate=False), evaluate=False),
               "^": sp.Pow}


@dataclass(frozen=True)
class Expresion:
    simbolica: sp.Expr
    variables: tuple[sp.Symbol, ...]
    numerica: Callable[..., float]

    def __call__(self, *puntos: float) -> float:
        return evaluar(self.numerica, *puntos)

    def derivada(self, orden: int = 1) -> "Expresion":
        return compilar(sp.diff(self.simbolica, self.variables[0], orden),
                        self.variables)


def compilar(expr: sp.Expr, variables: tuple[sp.Symbol, ...]) -> Expresion:
    """Convierte un árbol simbólico interno a evaluadores aritméticos."""
    posiciones = {v: i for i, v in enumerate(variables)}
    funciones = {sp.sin: math.sin, sp.cos: math.cos, sp.tan: math.tan,
                 sp.exp: math.exp, sp.log: math.log, sp.Abs: abs}

    def construir(nodo: sp.Expr) -> Callable:
        if nodo.is_Symbol:
            posicion = posiciones[nodo]
            return lambda args: args[posicion]
        if nodo.is_Atom and nodo.is_number:
            constante = float(nodo) if nodo.is_real else math.nan
            return lambda args: constante
        hijos = tuple(map(construir, nodo.args))
        if nodo.func == sp.Add:
            return lambda args: math.fsum(h(args) for h in hijos)
        if nodo.func == sp.Mul:
            return lambda args: math.prod(h(args) for h in hijos)
        if nodo.func == sp.Pow:
            return lambda args: math.pow(hijos[0](args), hijos[1](args))
        if nodo.func == sp.sign:
            def signo(args: tuple) -> float:
                valor = hijos[0](args)
                return float((valor > 0) - (valor < 0))
            return signo
        if nodo.func in funciones:
            funcion = funciones[nodo.func]
            return lambda args: funcion(hijos[0](args))
        raise ValueError("La expresión simbólica requiere una operación no disponible.")

    evaluar_arbol = construir(expr)
    return Expresion(expr, variables, lambda *args: evaluar_arbol(args))


class Gramatica:
    """Analizador descendente con precedencia y potencia asociativa a derecha."""

    def __init__(self, tokens: list[str], variables: dict[str, sp.Symbol]):
        self.tokens = iter(tokens)
        self.actual = next(self.tokens, "")
        self.variables = variables

    def tomar(self) -> str:
        token = self.actual
        self.actual = next(self.tokens, "")
        return token

    def exigir(self, token: str) -> None:
        if self.actual != token:
            raise ValueError(f"Se esperaba '{token}'.")
        self.tomar()

    def expresion(self, minima: int = 0) -> sp.Expr:
        token = self.tomar()
        if token in ("+", "-"):
            valor = self.expresion(30)
            izquierda = valor if token == "+" else sp.Mul(-1, valor, evaluate=False)
        elif token == "(":
            izquierda = self.expresion()
            self.exigir(")")
        elif token in self.variables or token in CONSTANTES:
            izquierda = self.variables.get(token, CONSTANTES.get(token))
        elif token in FUNCIONES:
            self.exigir("(")
            argumento = self.expresion()
            self.exigir(")")
            izquierda = (sp.Pow(argumento, sp.S.Half, evaluate=False) if token == "sqrt"
                         else FUNCIONES[token](argumento, evaluate=False))
        elif token and (token[0].isdigit() or token[0] == "."):
            if len(token) > 35 or not math.isfinite(float(token)):
                raise ValueError("Literal numérico fuera de rango.")
            if "e" in token.lower() and abs(int(token.lower().split("e")[1])) > 300:
                raise ValueError("Exponente del literal fuera de rango.")
            izquierda = sp.Rational(token)
        else:
            raise ValueError(f"Símbolo inesperado: {token or 'fin de expresión'}.")

        precedencia = {"+": 10, "-": 10, "*": 20, "/": 20, "^": 40}
        while self.actual and self.actual != ")":
            operador = self.actual if self.actual in precedencia else "*"
            nivel = precedencia[operador]
            if nivel < minima:
                break
            if self.actual in precedencia:
                self.tomar()
            derecha = self.expresion(nivel + (operador != "^"))
            if operador in ("-", "/"):
                izquierda = OPERACIONES[operador](izquierda, derecha)
            else:
                izquierda = OPERACIONES[operador](izquierda, derecha, evaluate=False)
        return izquierda


def interpretar(texto: str, variables: tuple[str, ...] = ("x",)) -> Expresion:
    """Acepta operadores matemáticos y funciones de la lista blanca."""
    tokens = []
    posicion = 0
    if not texto.strip() or len(texto) > 400:
        raise ValueError("Ingrese una expresión de 1 a 400 caracteres.")
    while posicion < len(texto):
        if texto[posicion].isspace():
            posicion += 1
            continue
        coincidencia = TOKEN.match(texto, posicion)
        if coincidencia is None:
            raise ValueError(f"Carácter no permitido en posición {posicion + 1}.")
        tokens.append(coincidencia[0])
        posicion = coincidencia.end()
    if len(tokens) > 100 or tokens.count("(") > 24:
        raise ValueError("La expresión supera el límite de complejidad.")
    simbolos = {nombre: sp.Symbol(nombre, real=True) for nombre in variables}
    lector = Gramatica(tokens, simbolos)
    expr = lector.expresion()
    if lector.actual:
        raise ValueError("Hay un paréntesis de cierre inesperado.")
    return compilar(expr, tuple(simbolos.values()))
