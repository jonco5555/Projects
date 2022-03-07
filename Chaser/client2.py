# Yonatan Cohen 324842608

import socket
import time
from Player import Player
from Question import Question

IP = '127.0.0.1'
PORT = 8820


def main():
    # create the socket
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((IP, PORT))

    if my_socket.recv(1024).decode() == "0":  # if server already has 3 players
        print("Game is full")
    else:
        # a forever loop until the player wants to stop playing
        while True:
            # noinspection PyBroadException
            try:
                p = Player()
                if stage0(my_socket) is False:  # if player doesn't want to play/play again
                    break

                temp = stage1(my_socket, p)
                if temp is False:  # if player doesn't earn any money on stage 1
                    print("Try again")
                    continue
                time.sleep(2)

                stage2(my_socket, p)
                time.sleep(2)

                won = stage3(my_socket, p)
                if won is True:  # if the player won
                    print("You won the chase! You earned {}$ \n".format(p.money))
                else:
                    print("You lost! The chaser caught you! \n")
            except Exception:
                break
    # closes connection
    my_socket.close()


# receives socket
# would return and sends to the server true if the player wanted to play
def stage0(my_socket):
    msg = my_socket.recv(1024).decode()
    while True:
        ans = input(msg)
        if ans == "y":
            my_socket.send(ans.encode())
            return True
        if ans == "n":
            my_socket.send(ans.encode())
            return False
        print("Invalid input, try again \n")


# receives socket and Player
# would return true if player earned any money, and update his money
def stage1(my_socket, p):
    print(my_socket.recv(1024).decode())  # prints server's welcome message
    for i in range(3):
        # receives question from server
        question, answers, correct_ans, chaser_answer = (my_socket.recv(1024).decode()).split("|")
        answers = answers.split("@")
        q = Question(question, answers, int(correct_ans))
        handling_question(my_socket, p, q, chaser_answer, i)  # sends it to the handle function
    p.money = my_socket.recv(1024).decode()  # receives from server the amount of money the player earned the updates it
    print("You earned " + str(p.money) + "$ in stage 1!")
    time.sleep(2)
    return p.money != "0"


# receives socket and Player
# sends to the server the requested mode
def stage2(my_socket, p):
    msg = my_socket.recv(1024).decode()
    while True:
        mode = input(msg)
        if mode == "1" or mode == "2" or mode == "3":
            my_socket.send(mode.encode())
            break
        print("Invalid input, try again \n")
    # calculates player's location and money by the mode he chose
    p.location += int(mode)
    if mode == "1":
        p.money = int(p.money) * 2
    if mode == "3":
        p.money = int(p.money) / 2


# receives socket and Player
# would return True if the player won
def stage3(my_socket, p):
    # prints server's welcome message
    print("Welcome to stage 3! Beat the chaser to win the money! \nThe goal - location 7! \n")
    time.sleep(1)
    counter = 0  # to number the questions
    print_info(p)  # prints player's details
    while p.location != "7":  # while player haven't won
        # receives question from server
        question, answers, correct_ans, chaser_answer = (my_socket.recv(1024).decode()).split("|")
        answers = answers.split("@")
        q = Question(question, answers, int(correct_ans))
        handling_question(my_socket, p, q, chaser_answer, counter)  # sends it to the handle function
        p.location, p.chaser_location = my_socket.recv(1024).decode().split(" ")  # receives from server new locations
        print_info(p)  # prints player's details
        counter += 1
        time.sleep(0.5)
        if p.chaser_location == p.location:  # would return false if the chaser caught the player
            return False
    return True  # would return true if player arrived to the bank


# receives socket ,question and number
# prints the question and answers, takes answer from player and send it to the server
def handling_question(my_socket, p, q, chaser_answer, i):
    while True:  # until the players choose a valid answer
        print("Question number {}: \n{}".format(i + 1, q.question))  # prints question
        # prints answers and get answer from player
        ans = input("1: {}   2: {}   3: {}   4: {} \nfor help press 0 \n".format(q.answers[0], q.answers[1],
                                                                                 q.answers[2], q.answers[3]))
        if ans == "0" and p.hlp is False:  # if he asks for help but he doesn't have any
            print("Sorry, you don't have any help left, try again \n")
            continue
        if ans == "0" and p.hlp is True:  # if he asks for help and he has one
            answer1 = q.correct_ans
            answer2 = answer1 % 4 + 1  # modulo for answer1 = 4, cause then (answer1 + 1) = 5 - out of bounds
            # prints new answers
            if answer1 < answer2:
                ans = input("{}: {}   {}: {} \n".format(answer1, q.answers[answer1 - 1], answer2
                                                        , q.answers[answer2 - 1]))
            else:
                ans = input("{}: {}   {}: {} \n".format(answer2, q.answers[answer2 - 1], answer1
                                                        , q.answers[answer1 - 1]))
            p.hlp = False  # updates the help variable
            break
        if ans == "1" or ans == "2" or ans == "3" or ans == "4":  # if the answer is valid
            break
        print("Invalid input, try again \n")

    if chaser_answer != "-1":  # prints chaser's answer in stage 3, passes in stage 1
        print("Chaser answer: {} \n".format(chaser_answer))
    my_socket.send(str(ans).encode())  # sends client's answer to server
    right_answer = my_socket.recv(1024).decode()  # receives if it's right
    if right_answer == "1":
        print("You are right! \n")
    else:
        print("You are wrong! The answer is {} \n".format(q.correct_ans))
    my_socket.send("finished".encode())


# receives a Player
# prints Player's money, location, available help and chaser's location
def print_info(p):
    print("You have - {}$ \nYour location - {} \nChaser's location - {} \nHelp - {} \n"
          .format(p.money, p.location, p.chaser_location, p.hlp))


if __name__ == '__main__':
    main()
