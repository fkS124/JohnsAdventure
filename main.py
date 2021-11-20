'''
    Welcome to John's Adventure! Hope you like my new game!

    Please be patient with some pieces of the code, it will take some time to clean the code ;')

'''


from data.scripts.world import main
import sys

if __name__ == '__main__':
    if sys.argv[-1] != "main.py" and sys.argv[-1] != "--debug":
        main(debug=("--debug" in sys.argv), first_state=sys.argv[-1])
    else:
        main(debug=("--debug" in sys.argv))
