# Andy

Experimentální Python projekt společnosti Jill Production. Jednoduchá kalkulačka
se čtyřmi operacemi, unit testy a GitHub Actions CI.

## Požadavky

Python 3.11 nebo novější. Projekt používá pouze standardní knihovnu; není nutné
instalovat žádné závislosti.

## Použití

Z kořenového adresáře repozitáře spusťte Python a importujte potřebné funkce:

```python
from calculator import add, subtract, multiply, divide

print(add(2, 3))        # 5
print(subtract(7, 2))   # 5
print(multiply(3, 4))   # 12
print(divide(7, 2))     # 3.5
```

Funkce pracují s čísly `int` a `float` podle standardní aritmetiky Pythonu.
Dělení nulou včetně `0.0` a `-0.0` vyvolá `ZeroDivisionError`. U desetinných
čísel platí běžná omezení přesnosti typu `float`.

## Testy

```bash
python -m unittest discover -s tests -v
```

Testy pokrývají základní operace, záporná a desetinná čísla, nulu a dělení nulou.
GitHub Actions spouští stejný příkaz při každém pushi a pull requestu na Pythonu
3.11, 3.12 a 3.13. Workflow má pouze oprávnění ke čtení obsahu a nic nenasazuje.
