import sys

from box.gmail.data import prepare_gmail


processes = {
    'gmail': prepare_gmail,
}


def list_of_commands() -> list:
    return list(processes.keys())


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in processes:
        print('All possible commands:')
        print(list_of_commands())
        exit()
    processes[sys.argv[1]]()
