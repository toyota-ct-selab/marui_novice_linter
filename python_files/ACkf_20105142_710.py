from collections import defaultdict
import sys, os, math

def gcd(a1, a2):
    if a2 == 0:
        return a1
    else:
        return gcd(a2, a1 % a2)
        
# return (g, x, y) a*x + b*y = gcd(x, y)
def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, x, y = egcd(b % a, a)
        return (g, y - (b // a) * x, x)
if __name__ == "__main__":
    #n, m = list(map(int, input().split()))
    a1, b1, a2, b2, L, R = map(int, input().split())
    a2 *= -1 
    LCM = a1 * a2 // gcd(a1, a2)
    if abs(b1 - b2) % gcd(a1, a2) != 0:
        print(0)
        sys.exit(0)
    L = max([b1, b2, L])
    g, x, y = egcd(a1, a2)
    X = a1 * x * (b2 - b1) // g + b1
    X += LCM * math.ceil((L - X) / LCM)
    if L <= X <= R:
        print(max(0, (R - X) // LCM + 1))
    else:
        print(0)