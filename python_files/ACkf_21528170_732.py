from collections import defaultdict
import sys, os, math

if __name__ == "__main__":
    #n, m = list(map(int, input().split()))
    n, k = map(int, input().split())
    arr = list(map(int, input().split()))
    ans = 0
    for i in range(1, n):
        if arr[i] < k - arr[i - 1]:
            ans += k - arr[i - 1] - arr[i]
            arr[i] = k - arr[i - 1]
    print(ans)
    print(' '.join(str(i) for i in arr))