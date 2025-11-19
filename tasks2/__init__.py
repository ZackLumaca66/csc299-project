from .core import TaskManager, Task

def main():
    tm = TaskManager()
    tm.add("Write report")
    tm.add("Read book")
    tm.complete("Write report")
    print("All:", tm.list())
    print("Pending:", tm.pending())
    print("Completed:", tm.completed())

if __name__ == "__main__":
    main()