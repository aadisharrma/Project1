**Description**
Develop a client-side application that engages with a server to play a custom version of the trending game, Wordle. 
Utilizing socket programming, the client interacts with the server by making word guesses and receiving feedback on the
accuracy of those guesses. Upon correctly identifying the server's secret word, the client is awarded a unique 
identification flag.

**Methodology**
Initializing Word List
The word list is read from a text file and stored in a Python list, which serves as the basis for the game's word 
guesses.

**Server Connection**
The program employs argparse to parse command-line arguments, specifying port and SSL settings, among other details. 
Two essential functions are used to establish a socket connection: establish_socket_connection initiates the socket and 
handles SSL wrapping if necessary, while send_initial_hello sends an introductory message to the server.

**Game Mechanics**
The program initially retrieves a game ID from the server, which is crucial for the gameplay session. It then kicks 
off the game with a predetermined initial guess of "least." Two key functions govern the game logic:

calculate_similarity_marks evaluates how closely a word guess matches potential words by generating a similarity score.
filter_matching_words filters the word list based on the similarity score, refining future word guesses.

These functions continue to iterate until the correct word is identified. Upon success, the unique flag returned by the
server is displayed.

**Server Communication**
Messages to and from the server are JSON-encoded and handled by send_message and receive_message functions. These
methods handle UTF-8 encoding and ensure message integrity.

**Challenges and Learning Experiences**
The most challenging part of the project was grasping the underlying concepts related to socket programming and game 
algorithm design. Despite being in an advanced course, the initial learning curve was steep. However, I was able to
overcome these hurdles through self-directed learning, including watching YouTube tutorials and reading various 
resources online. This approach not only helped in understanding the technical aspects but also proved valuable in 
algorithmic problem-solving. Collaborating with peers further enriched the learning experience and contributed to the
project's success.