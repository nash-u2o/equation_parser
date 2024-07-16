from math import cos, e, log, log10, pi, sin, sqrt, tan

import pytest

import equation_parser


@pytest.mark.parametrize(
    "equation",
    [
        ("(8 - sqrt(8^2 - 4*1*12))/(2*1)"),
        ("(8 + sqrt(8^2 - 4*1*12))/(2*1)"),
        ("(e^(17.625 * 115/(243.04 + 115))/e^(17.625 * 87/(243.04 + 87)))*100"),
        ("e^(5^3 - 3*5^2 + 2*5 - 1) + 1/(5^2 + 1) - (5^5 - 5*5^3 + 4*5)^(1/3)"),
        (
            " log(  sqrt(2^2 + 3 ^         2)) / (log( 2+3    ) - log10(4 - 3)) + e^(2 + 3) / (2^2 - (-(-4-(-(-3^2))-85248+3+(-88))))"
        ),
        ("(5^(1/3) + 6^(1/4))^2 - sqrt(-7^2 + (-8)^2)"),
        ("(3^3 - 3*10 + 2) / (4^2 - 1) + (5^3 + 3*6 - 2) / (7^2 + 1)"),
        ("-cos(pi) + sin(pi/2) - tan(pi + .5) + cos(-sin(-pi/2))"),
        ("-cos(pi) / (sin(pi/2)) / ((tan(pi + .5) / cos(-sin(-pi/2))))"),
    ],
)
def test_equation_parser(equation):
    eval_eq = equation.replace("^", "**")

    # speed test
    # for i in range(10000):
    #     ans = equation_parser.process_equation(equation)

    ans = equation_parser.process_equation(equation)
    assert pytest.approx(ans, 0.000000000000001) == eval(eval_eq)
