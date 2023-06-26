import signal


class TimeoutError(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutError("Timeout occurred.")


def run_with_timeout(func, timeout_seconds):
    # Set the timeout handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)

    try:
        result = func()
        signal.alarm(0)  # Cancel the alarm
        return result
    except TimeoutError:
        print("Function timed out.")
        return None


# Example usage
def my_function():
    # Code to execute
    pass


def split_list(lst, n):
    k, m = divmod(len(lst), n)  # Calculate quotient and remainder
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]
