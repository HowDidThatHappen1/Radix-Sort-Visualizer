def counting_sort(arr, exp, steps_callback=None):

    n = len(arr)

    output = [0] * n
    count = [0] * 10

    for num in arr:

        digit = (num // exp) % 10
        count[digit] += 1

    if steps_callback:

        steps_callback(
            exp,
            arr.copy(),
            output.copy(),
            count.copy(),
            "Counting Digits",
            None
        )

    for i in range(1, 10):

        count[i] += count[i - 1]

    if steps_callback:

        steps_callback(
            exp,
            arr.copy(),
            output.copy(),
            count.copy(),
            "Cumulative Count",
            None
        )

    for i in range(n - 1, -1, -1):

        digit = (arr[i] // exp) % 10

        position = count[digit] - 1

        output[position] = arr[i]

        count[digit] -= 1

        if steps_callback:

            steps_callback(
                exp,
                arr.copy(),
                output.copy(),
                count.copy(),
                f"Placing {arr[i]}",
                position
            )

    for i in range(n):

        arr[i] = output[i]


def radix_sort(arr, steps_callback=None):

    if not arr:
        return

    max_num = max(arr)
    exp = 1

    while max_num // exp > 0:
        counting_sort(arr, exp, steps_callback)

        exp *= 10
