import sympy as sp


def f3(x0=0.001, *, a, b, c, d, e=1e-6):
    x_n = x0 - ((a * x0 ** 3 + b * x0 ** 2 + c * x0 + d) /
                (3 * a * x0 ** 2 + 2 * b * x0 + c))
    while abs(x_n - x0) > e:
        x0 = x_n
        x_n = x0 - ((a * x0 ** 3 + b * x0 ** 2 + c * x0 + d) /
                    (3 * a * x0 ** 2 + 2 * b * x0 + c))
    return x_n


if __name__ == "__main__":
    # x = f3(a=3, b=0, c=-1, d=-2)
    # print(x)

    x = sp.Symbol('x')
    f = 3*x**3 - x - 2
    x = sp.solve(f)
    print(x)
