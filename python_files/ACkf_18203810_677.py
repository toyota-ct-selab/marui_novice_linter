from collections import defaultdict

if __name__ == "__main__":
    #n, m = list(map(int, input().split()))
    s = input()
    s1 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
    d = defaultdict(int)
    for i in range(64):
        for j in range(64):
            d[s1[i & j]] += 1
    ans = 1
    for ch in s:
        ans = ans * d[ch] % (10 ** 9 + 7)

    print(ans)