# Yonatan Cohen 324842608

import socket
import threading
import random
import time
from Question import Question

SERVER_IP = '0.0.0.0'
SERVER_PORT = 8820
MAX_PLAYERS = 3
current_players = 0
QUESTIONS = [Question("How many soccer players should each team have on the field at the start of each match?",
                      ["11", "10", "9", "12"], 1),
             Question("When Michael Jordan played for the Chicago Bulls, how many NBA Championships did he win?",
                      ["0", "2", "6", "10"], 3),
             Question("What country won the very first FIFA World Cup in 1930?",
                      ["Spain", "Uruguay", "Brazil", "Germany"], 2),
             Question("What year was the very first model of the iPhone released?",
                      ["2007", "2005", "2010", "2008"], 1),
             Question("What’s the shortcut for the “copy” function on most computers?",
                      ["ctrl x", "ctrl z", "ctrl v", "ctrl c"], 4),
             Question("What part of the atom has no electric charge?",
                      ["Proton", "Electron", "Neutron", "All of them"], 3),
             Question("What is the symbol for potassium?",
                      ["L", "K", "P", "T"], 2),
             Question("Which planet is the hottest in the solar system?",
                      ["Venus", "Jupiter", "Mercury", "Mars"], 1),
             Question("Which animal can be seen on the Porsche logo?",
                      ["Lion", "Horse", "Jaguar", "Snake"], 2),
             Question("How many parts (screws and bolts included) does the average car have?",
                      ["1000000", "500000", "5000", "30000"], 4),
             Question("Which country produces the most coffee in the world?",
                      ["USA", "Belgium", "Switzerland", "Brazil"], 4),
             Question("Which kind of alcohol is Russia is notoriously known for?",
                      ["Whisky", "Wine", "Vodka", "Rum"], 3),
             Question("Which bone are babies born without?",
                      ["Knee cap", "Teeth", "Fingers", "Skull"], 1),
             Question("How many times does the heartbeat per day?",
                      ["10000", "100000", "1000000", "1000"], 2),
             Question("Which American state is the largest (by area)?",
                      ["USA", "Brazil", "Canada", "Alaska"], 4),
             Question("What is the smallest country in the world?",
                      ["Monaco", "Israel", "Vatican", "Nauru"], 3),
             ]


def main():
    # create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    print("Socket bind to port", SERVER_PORT)

    # put the socket into listening mode
    sock.listen(5)
    print("Socket is listening")

    global current_players  # global variable to monitor players' number

    # a forever loop to receive clients
    while True:
        c_sock = sock.accept()[0]

        if current_players == MAX_PLAYERS:  # if we have 3 players
            c_sock.send("0".encode())  # game is full
            c_sock.close()
        else:  # if we have less than 3 players
            c_sock.send("1".encode())  # allow to join
            current_players += 1  # update players number
            print("Socket connected - num of players: " + str(current_players))
            threading.Thread(target=manage_game, args=(c_sock,)).start()  # creating a new thread


# main loop. receives socket
# calls to all stages' functions and manages the game
def manage_game(client_socket):
    global current_players
    while True:
        # noinspection PyBroadException
        try:
            if not stage0(client_socket):  # if player doesn't want to play/play again
                break

            available_questions = list(range(16))  # holds list of available questions for the player
            if not stage1(client_socket, available_questions):  # if player doesn't earn any money on stage 1
                continue

            mode = stage2(client_socket)  # selects mode for the game (risky, normal or safe)

            stage3(client_socket, available_questions, 1 + int(mode))
        except Exception:  # would prevent error if client disconnected unwillingly
            break

    # closes connection
    client_socket.close()
    current_players -= 1
    print("Socket disconnected - num of players: " + str(current_players))


# receives a question
# returns an answer in prob of 0.75 to be right
def chaser(q):
    prob = [25/3, 25/3, 25/3, 25/3]
    prob[q.correct_ans - 1] = 75
    return random.choices([1, 2, 3, 4], weights=prob, k=1)[0]


# receives socket
# returns True if the player wants to play
def stage0(client_socket):
    client_socket.send("Do you want to play?(y/n) \n".encode())
    answer = client_socket.recv(1024).decode()
    return answer == "y"


# receives socket and list of available questions
# chooses random questions and sends them to the player. returns True if he answered at least one question right
def stage1(client_socket, available_questions):
    client_socket.send("Welcome to stage 1! Answer 3 questions to earn money \n".encode())
    right_answers = 0
    for i in range(3):
        question_number = random.choices(available_questions)[0]  # chooses random question
        available_questions.remove(question_number)  # removes it from the available questions list
        question = QUESTIONS[question_number]
        # sends question and answers to the client
        client_socket.send("{}|{}|{}|-1".format(question.question, '@'.join(question.answers), question.correct_ans)
                           .encode())
        answer = client_socket.recv(1024).decode()  # receives answer from client
        if answer == str(question.correct_ans):  # if the answer is right
            right_answers += 1
            client_socket.send("1".encode())
        else:  # if answer is wrong
            client_socket.send("0".encode())
        temp = client_socket.recv(1024).decode()
    time.sleep(1)
    client_socket.send(str(5000*right_answers).encode())  # sends to the client how much money he earned at this stage
    return right_answers != 0  # would return false if player didn't earn any money


# receives socket
# returns the mode the player chose
def stage2(client_socket):
    # sends to client possible modes to choose
    time.sleep(1)
    client_socket.send("Choose mode for stage 3: Risky - 1, Regular - 2, Safe - 3 \n".encode())
    return client_socket.recv(1024).decode()


# receives socket, list of available questions and player's location
# sends questions to the player, comparing his answers the the chaser's answers and returns True if the player won
def stage3(client_socket, available_questions, location):
    chaser_location = 0
    while location != 7:
        question_number = random.choices(available_questions)[0]  # chooses random question
        available_questions.remove(question_number)  # removes it from the available questions list
        question = QUESTIONS[question_number]
        chaser_answer = chaser(question)  # chaser chooses answer
        # sends question and answers to the client
        client_socket.send("{}|{}|{}|{}".format(question.question, '@'.join(question.answers), question.correct_ans,
                                                chaser_answer).encode())
        answer = client_socket.recv(1024).decode()  # receives answer from client
        if answer == str(question.correct_ans):  # if the answer is right
            location += 1
            client_socket.send("1".encode())
        else:  # if the answer is wrong
            client_socket.send("0".encode())
        if chaser_answer == question.correct_ans:  # if chaser's answer is right
            chaser_location += 1
        temp = client_socket.recv(1024).decode()
        time.sleep(1)
        client_socket.send("{} {}".format(location, chaser_location).encode())  # sends to client new locations
        if chaser_location == location:  # would return false if the chaser caught the player
            return False
        if not available_questions:
            available_questions = list(range(16))  # updates the questions if they're done
    return True  # would return true if player arrived to the bank


if __name__ == '__main__':
    main()
