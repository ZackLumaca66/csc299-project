from tasks2.core import TaskManager

def inc(n: int) -> int:
    return n + 1


def main():
    tm = TaskManager()
    tm.add("Alpha")
    tm.add("Beta")
    tm.complete("Alpha")
    print("inc(5) =>", inc(5))
    print("Pending:", tm.pending())
    print("Completed:", tm.completed())

if __name__ == "__main__":
    main()