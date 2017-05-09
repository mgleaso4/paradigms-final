PyGame and Twisted Final Project
Authors: Maddie Gleason and Ben Gunning
Date: May 10, 2017

Two Player Snake
	Our final project is a two player snake game that allows players to compete via a network connection. A player's goal is to have the longer snake when the opponent's snake dies. 

Set Up
	To set up our game simply open two processes on ash. Player 1 should first run client1.py to listen on port 40139. Player 2 should run client2.py to establish the complete game connection. Upon connection, player 1 controls the blue snake and player 2 controls the red snake. 

Game Play 
	The object of this game is to move the snake around the screen (using the up, down, left, and right arrow keys) to eat food without coliding into the opponent. The snake increases in length after consuming food (white rectangles). Upon an inevitable collision, the player with the longer snake wins the game. Thus, players should avoid collisions with their opponent's snake, the border of the game window, and their own snakes. The game ends when a player wins and the user exits or escapes the game. 

Collisions 
	There are several types of collision that will end the game: 
	1) If a collision occurs between both snakes, the player with the longer snake wins. 
	2) If a snake collides with the game window, the opponent's snake wins. 
	3) If a snake collides with itself, the opponent's snake wins.
	Upon any collision and "Game Over" screen is displayed with the winner of the game. After three seconds, the pygame window closes and the program exits.

Coding
	The code in client1.py and client2.py is predominantly similar. We used pygame to display our images and twisted to control network connections. We treated client1.py as our master client. Therefore, upon connection client1.py writes "go" across the connection, starting the main game loop. We used lineReceived and our own update function to write information across the connection with a deferred queue. While the players update each other on their own positions, client1.py controls randomly positioning the fuel object in the window. 