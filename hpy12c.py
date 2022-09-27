from decimal import Decimal
from math import log
from typing import List, Optional


def ipmt(
    rate: float,
    per: int,
    nper: int,
    pv: float,
    pfv: float = 0.0,
    end_or_beginning: int = 0,
) -> float:
    vpmt = pmt(rate, nper, pv, pfv, end_or_beginning)
    vfv = fv(rate, (per - 1), vpmt, pv, end_or_beginning) * rate
    temp = vfv / (1 + rate) if (end_or_beginning == 1) else vfv

    return 0.0 if (per == 1 and end_or_beginning == 1) else temp

def ppmt(
    rate: float,
    per: int,
    nper: int,
    pv: float,
    pfv: float = 0.0,
    end_or_beginning: int = 0,
) -> float:
    vpmt = pmt(rate, nper, pv, pfv, end_or_beginning)
    vipmt = ipmt(rate, per, nper, pv, pfv, end_or_beginning)

    return vpmt - vipmt


def fv(
    rate: float, nper: int, pmt: float, pv: float, end_or_beginning: int = 0
) -> float:
    temp = (1 + rate) ** nper
    fact = (1 + rate * end_or_beginning) * (temp - 1) / rate

    return -(pv * temp + pmt * fact)


def pmt(
    rate: float, nper: int, pv: float, fv: float = 0.0, end_or_beginning: int = 0
) -> float:
    temp = (1 + rate) ** nper
    fact = (1 + rate * end_or_beginning) * (temp - 1) / rate

    return -(fv + pv * temp) / fact


def nper(
    rate: float, pmt: float, pv: float, fv: float = 0.0, end_or_beginning: int = 0
) -> float:
    if rate == 0:
        return (-pv - fv) / pmt

    z = pmt * (1 + rate * end_or_beginning) / rate
    temp = log((-fv + z) / (pv + z))

    return temp / log(1 + rate)


def pv(
    rate: float, nper: int, pmt: float, fv: float = 0.0, end_or_beginning: int = 0
) -> float:
    temp = (1 + rate) ** nper
    fact = (1 + rate * end_or_beginning) * (temp - 1) / rate

    return -(fv + pmt * fact) / temp


def npv(discount: float, cashflows: List[float]) -> float:
    total = 0
    for index, cashflow in enumerate(cashflows):
        total += Decimal(cashflow) / (1 + Decimal(discount)) ** (index + 1)

    return float(total)


def irr(
    cashflows: List[float], guess: float = 1.0e-16, max_iterations: int = 30
) -> Optional[float]:
    tolerancy = 1e-6
    x0 = guess

    for i in range(max_iterations):
        vnpv = npv(x0, cashflows)
        dnpv = _dnpv(x0, cashflows)
        x1 = x0 - vnpv / dnpv

        if abs(x1 - x0) <= tolerancy:
            return x1

        x0 = x1


def rate(
    nper: int,
    pmt: float,
    pv: float,
    fv: float = 0.0,
    end_or_beginning: int = 0,
    rate_guess: float = 0.10,
) -> float:
    guess = rate_guess
    tolerancy = 1e-6
    close = False

    while not close:
        temp = _newton_iter(
            guess, nper, float(pmt), float(pv), float(fv), end_or_beginning
        )
        next_guess = round(guess - temp, 20)
        diff = abs(next_guess - guess)
        close = diff < tolerancy
        guess = next_guess

    return next_guess


def _dnpv(discount, cashflows):
    """
    Calculates the derivative of npv method.
    It is used at irr as input for Newton Raphson
    root-finding algorithm
    """

    total = 0
    for index, cashflow in enumerate(cashflows):
        total += (-index) * Decimal(cashflow) / (1 + Decimal(discount)) ** (index - 1)

    return float(total)


def _newton_iter(r, n, p, x, y, w):
    """
    This method was borrowed from the NumPy rate
    formula which was generated by Sage
    """
    t1 = (r + 1) ** n
    t2 = (r + 1) ** (n - 1)
    return (y + t1 * x + p * (t1 - 1) * (r * w + 1) / r) / (
        n * t2 * x
        - p * (t1 - 1) * (r * w + 1) / (r**2)
        + n * p * t2 * (r * w + 1) / r
        + p * (t1 - 1) * w / r
    )
