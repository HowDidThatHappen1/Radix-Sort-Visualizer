def counting_sort(arr, exp, steps_callback=None):
    n = len(arr)
    output = [-1] * n
    count = [0] * 10

    for num in arr:
        digit = (num // exp) % 10
        count[digit] += 1

    if steps_callback:
        steps_callback(
            exp=exp,
            original=arr.copy(),
            output=[-1] * n,
            count=count.copy(),
            phase="Counting Digits",
            highlight=None,
        )

    for i in range(1, 10):
        count[i] += count[i - 1]

    if steps_callback:
        steps_callback(
            exp=exp,
            original=arr.copy(),
            output=[-1] * n,
            count=count.copy(),
            phase="Cumulative Count",
            highlight=None,
        )

    temp_output = [-1] * n
    for i in range(n - 1, -1, -1):
        digit = (arr[i] // exp) % 10
        pos = count[digit] - 1
        temp_output[pos] = arr[i]
        count[digit] -= 1

        if steps_callback:
            steps_callback(
                exp=exp,
                original=arr.copy(),
                output=temp_output.copy(),
                count=count.copy(),
                phase=f"Placing {arr[i]}",
                highlight=pos,
            )

    for i in range(n):
        arr[i] = temp_output[i]


def radix_sort(arr, steps_callback=None):
    if not arr:
        return

    max_num = max(arr)
    exp = 1

    while max_num // exp > 0:
        counting_sort(arr, exp, steps_callback)
        exp *= 10
