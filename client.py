import argparse
import json
import socket
import ssl

# Save all the words from text file to a list to use it afterwards
f = open('words.txt', 'r')
wordsList = []
for line in f:
    wordsList.append(line[:5])
f.close()


# Socket Connection methods
def parse_arguments():
    argument_parser = argparse.ArgumentParser(
        usage='./client <-p port> <-s> [hostname] [Northeastern-Username]')
    argument_parser.add_argument('-p', type=int, required=False, dest='port')
    argument_parser.add_argument('-s', action='store_true', required=False,
                                 help='if the socket is encrypted with TLS/SSL', dest='ssl')
    argument_parser.add_argument('hostname', type=str)
    argument_parser.add_argument('northeastern_used_id', type=str, metavar='Northeastern-Username')
    return argument_parser.parse_args()


def establish_socket_connection(args):
    # Initializing a socket
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Wrap the socket with TLS/SSL encryption if specified
    if args.ssl:
        my_socket = ssl.wrap_socket(my_socket)

    # Determine the port to use (default 27993 for non-SSL, 27994 for SSL)
    port = args.port if args.port is not None else (27994 if args.ssl else 27993)

    # Connecting to the game server
    my_socket.connect((args.hostname, port))
    return my_socket


def send_initial_hello(my_socket, northeastern_username):
    initial_msg = json.dumps({"type": "hello", "northeastern_username": northeastern_username}) + '\n'
    send_message(my_socket, initial_msg)


# Send a UTF-8 encoded message over a given socket
def send_message(my_socket, message):
    message = bytes(message, 'utf-8')
    total_msg_sent = 0
    while total_msg_sent < len(message):
        msg_sent = my_socket.send(message)
        if msg_sent == 0:
            raise RuntimeError("The socket connection is broken")
        total_msg_sent += msg_sent


# Receive a message from a given socket, expecting a UTF-8 encoded string terminated by a newline character.
def receive_message(my_socket):
    ended = False
    message = ''
    while not ended:
        message = my_socket.recv(1024).decode()
        if message.endswith('\n'):
            ended = True
    return message


# Extract the game ID from a JSON-formatted message.
def get_game_id(message):
    message = json.loads(message)
    return message['id']


# Send the initial guess to start the game, typically using a predetermined word.
def get_initial_guess(game_id, sock):
    message = json.dumps({"type": "guess", "id": str(game_id), "word": "least"}) + '\n'
    send_message(sock, message)
    return 'least'


# Calculate similarity marks between two words based on their letter positions.
def calculate_similarity_marks(my_word, words_from_list):
    new_similarity_marks = []
    letter_not_in_word = set()

    # First pass to identify exact matches and collect unmatched letters and positions
    for i, (first_letter, second_letter) in enumerate(zip(my_word, words_from_list)):
        if first_letter == second_letter:
            new_similarity_marks.append('2')
        else:
            new_similarity_marks.append('0')
            letter_not_in_word.add(second_letter)

    # Second pass to identify partial matches
    for i, letter in enumerate(my_word):
        if new_similarity_marks[i] == '0' and letter in letter_not_in_word:
            new_similarity_marks[i] = '1'
            letter_not_in_word.remove(letter)

    return "".join(new_similarity_marks)


# Filter out words from a list that do not match the given marks when compared to another word.
def filter_matching_words(word_list, word, marks):
    new_possible_words_list = []
    for wo in word_list:
        if calculate_similarity_marks(word, wo) == marks:
            new_possible_words_list.append(wo)
    return new_possible_words_list


# Process the server's response to determine the next set of possible words and the next word to guess.
def process_server_response(message, last_word, prev_words):
    message = json.loads(message)
    guesses = message['guesses']
    final_guess = guesses[-1]
    guess_marks = ''.join(str(guess) for guess in final_guess['marks'])  # Get the marks as a string
    more_words = filter_matching_words(prev_words, last_word, guess_marks)
    return more_words, more_words[0]


# Check if the received server message indicates the end of the game.
def is_game_over(message):
    message = json.loads(message)
    message_type = message['type']
    return message_type != 'bye'


# Main function to start and play the game
def main():
    args = parse_arguments()
    my_socket = establish_socket_connection(args)
    send_initial_hello(my_socket, str(args.northeastern_used_id))

    # Receive the first message from the server
    message = receive_message(my_socket)

    # Extract and store the game ID
    game_id = get_game_id(message)

    # Send the initial word guess and process the server's response
    final_word = get_initial_guess(game_id, my_socket)
    answer_message = receive_message(my_socket)

    # Process the second set of words
    next_words, new_word = process_server_response(answer_message, final_word, wordsList)
    new_message = json.dumps({"type": "guess", "id": str(game_id), "word": str(new_word)}) + '\n'
    final_word = new_word
    send_message(my_socket, new_message)

    # Continuously choose and send word guesses until the game is over
    while True:
        answer_message = receive_message(my_socket)
        # Check if the game is over
        if not is_game_over(answer_message):
            answer_message = json.loads(answer_message)
            print(answer_message['flag'])
            break

        next_words, new_word = process_server_response(answer_message, final_word, next_words)
        new_message = json.dumps({"type": "guess", "id": str(game_id), "word": str(new_word)}) + '\n'
        send_message(my_socket, new_message)
        final_word = new_word


if __name__ == '__main__':
    main()
