/* ReversiJeffers.cpp : Defines the entry point for the console application.
	Author:Mitchell Jeffers
	Date: 2/24/2016
	Class:438 AI
	project Name: Reversi player
	Description: This program uses a alpha beta search tree along with a hueristic to determine the best move. it is used with the provided reversiinterface.exe  
*/
//#include "stdafx.h"
#include <iostream>
#include <fstream>
#include <iomanip>
#include <ctype.h>
#include <string.h>
#include <string>
#include <stdlib.h>
#include <time.h>
#include <set>
//#include "gamecomm.h"


using namespace std;

int nodecount = 0;
const int maxturn = 1;
const int minturn = -1;
const int maxsucc = 100;
const int VS = -1000000;
const int VL = 1000000;
int blank = 0;
int oppColor= -1;
int myColor= 1;
int board[8][8];
int CornerMulti = 150;
int moveNumMulti = 6;
int OppMoveMulti = 20;
int stabMulti = 70;
int oppStabMulti = 10;
int shitty = 1000;//30//1000
int fmMulti = 1;
string moves;
typedef int stateType;
string best = "0";

//Find Available Moves to make takes in game board and the int representing 'your' pieces and 'mine'
//Returns a String of available moves in the format of "brcrcrcrc" with r representing the row and c representing the column
string availableMoves(int n[8][8], int mine, int yours) {

	string validMove = "b";
	for (int i = 0; i < 8; i++) {//rows
		for (int j = 0; j < 8; j++) {//coloums

			if ((n[i][j] == blank) && (j != 7) && (n[i][j + 1] == yours)) {//check to the right
				for (int k = j + 1; k < 8; k++) {
					if (n[i][k] == mine) {
						string c = to_string(j);
						string r = to_string(i);
						validMove += r;
						validMove += c;
						break;
					}
					if (n[i][k] == blank) {
						break;
					}
				}
			}

			if ((n[i][j] == blank) && (j != 0) && (n[i][j - 1] == yours)) {//check to the left
				for (int k = j - 1; k >= 0; k--) {
					if (n[i][k] == mine) {
						string c = to_string(j);
						string r = to_string(i);
						validMove += r;
						validMove += c;
						break;
					}
					if (n[i][k] == blank) {
						break;
					}
				}
			}
			if ((n[i][j] == blank) && (i != 0) && (n[i - 1][j] == yours)) {//check up
				for (int k = i - 1; k >= 0; k--) {
					if (n[k][j] == mine) {
						string c = to_string(j);
						string r = to_string(i);
						validMove += r;
						validMove += c;
						break;
					}
					if (n[k][j] == blank) {
						break;
					}
				}
			}

			if ((n[i][j] == blank) && (i != 7) && (n[i + 1][j] == yours)) {//check down
				for (int k = i + 1; k < 8; k++) {
					if (n[k][j] == mine) {
						string c = to_string(j);
						string r = to_string(i);
						validMove += r;
						validMove += c;
						break;
					}
					if (n[k][j] == blank) {
						break;
					}
				}
			}
			
            if ((n[i][j] == blank) && (i != 0) && (j != 0) && (n[i - 1][j - 1] == yours)) {//check top left diag
				for (int k = i - 1, l = j - 1; ((k >= 0) && (l >= 0)); k--, l--) {
					if (n[k][l] == mine) {
						string c = to_string(j);
						string r = to_string(i);
						validMove += r;
						validMove += c;
						break;
					}
					if (n[k][l] == blank) {
						break;
					}

				}
			}
			if ((n[i][j] == blank) && (i != 0) && (j != 7) && (n[i - 1][j + 1] == yours)) {//check top right diag
				for (int k = i - 1, l = j + 1; ((k >= 0) && (l <= 7)); k--, l++) {
					if (n[k][l] == mine) {
						string c = to_string(j);
						string r = to_string(i);
						validMove += r;
						validMove += c;
						break;
					}
					if (n[k][l] == blank) {
						break;
					}
				}
			}

			if ((n[i][j] == blank) && (i != 7) && (j != 0) && (n[i + 1][j - 1] == yours)) {//check bottom left diag
				for (int k = i + 1, l = j - 1; ((k <= 7) && (l >= 0)); k++, l--) {
					if (n[k][l] == mine) {
						string c = to_string(j);
						string r = to_string(i);
						validMove += r;
						validMove += c;
						break;
					}
					if (n[k][l] == blank) {
						break;
					}

				}
			}

			if ((n[i][j] == blank) && (i != 7) && (j != 7) && (n[i + 1][j + 1] == yours)) {//check bottom right diag
				for (int k = i + 1, l = j + 1; ((k <= 7) && (l <= 7)); k++, l++) {
					if (n[k][l] == mine) {
						string c = to_string(j);
						string r = to_string(i);
						validMove += r;
						validMove += c;
						break;
					}
					if (n[k][l] == blank) {
						break;
					}
				}
			}
		}
	}
	return validMove;
}
int Stability(int n[8][8], int  mine, int yours) {
	int yStab = 0;
	int xStab = 0;
	int neStab = 0;
	int nwStab = 0;
	int oppyStab = 0;
	int oppxStab = 0;
	int oppneStab = 0;
	int oppnwStab = 0;
	int value = 0;
	for (int i = 0; i < 8; i++) {
		for (int j = 0; j < 8; j++) {
			if (n[i][j] == mine) {
				for (int k = i; k >= 0; k--) {//check up
					yStab = 1;
					if (n[k][j] != mine) {
						yStab = 0;
						break;
					}
				}
				if (!yStab) {
					yStab = 1;
					for (int k = i; k < 8; k++) {//check dwn
						if (n[k][j] != mine) {
							yStab = 0;
							break;
						}
					}
				}
				for (int l = j; l >= 0; l--) {//check lft
					xStab = 1;
					if (n[i][l] != mine) {
						xStab = 0;
						break;
					}
				}
				if (!xStab) {
					xStab = 1;
					for (int l = j; l < 8; l++) {//check rgt
						if (n[i][l] != mine) {
							xStab = 0;
							break;
						}
					}
				}
				for (int k = i, l = j; ((l >= 0) && (k >= 0)); k--, l--) {//check tp lft
					neStab = 1;
					if (n[i][l] != mine) {
						neStab = 0;
						break;
					}
				}
				if (!neStab) {
					neStab = 1;
					for (int k = i, l = j; ((k < 8) && (l < 8)); k++, l++) {//check rgt
						if (n[i][l] != mine) {
							neStab = 0;
							break;
						}
					}
				}
				for (int k = i, l = j; ((l < 8) && (k >= 0)); k--, l++) {//check tp lft
					nwStab = 1;
					if (n[i][l] != mine) {
						nwStab = 0;
						break;
					}
				}
				if (!nwStab) {
					nwStab = 1;
					for (int k = i, l = j; ((k < 8) && (l >= 0)); k++, l--) {//check rgt
						if (n[i][l] != mine) {
							nwStab = 0;
							break;
						}
					}
				}
			}
			else if (n[i][j] == yours) {
				for (int k = i; k >= 0; k--) {//check up
					oppyStab = 1;
					if (n[k][j] != yours) {
						oppyStab = 0;
						break;
					}
				}
				if (!oppyStab) {
					oppyStab = 1;
					for (int k = i; k < 8; k++) {//check dwn
						if (n[k][j] != yours) {
							oppyStab = 0;
						}
					}
				}
				for (int l = j; l >= 0; l--) {//check lft
					oppxStab = 1;
					if (n[i][l] != yours) {
						oppxStab = 0;
						break;
					}
				}
				if (!oppxStab) {
					oppxStab = 1;
					for (int l = j; l < 8; l++) {//check rgt
						if (n[i][l] != yours) {
							oppxStab = 0;
							break;
						}
					}
				}
				for (int k = i, l = j; ((l >= 0) && (k >= 0)); k--, l--) {//check tp lft
					oppneStab = 1;
					if (n[i][l] != yours) {
						oppneStab = 0;
						break;
					}
				}
				if (!oppneStab) {
					oppneStab = 1;
					for (int k = i, l = j; ((k < 8) && (l < 8)); k++, l++) {//check rgt
						if (n[i][l] != yours) {
							oppneStab = 0;
							break;
						}
					}
				}
				for (int k = i, l = j; ((l <8) && (k >= 0)); k--, l++) {//check tp lft
					oppnwStab = 1;
					if (n[i][l] != yours) {
						oppnwStab = 0;
						break;
					}
				}
				if (!oppnwStab) {
					oppnwStab = 1;
					for (int k = i, l = j; ((k < 8) && (l >= 0)); k++, l--) {//check rgt
						if (n[i][l] != yours) {
							oppnwStab = 0;
							break;
						}
					}
				}


			}

			value = value + (yStab + xStab + neStab + nwStab)*(yStab + xStab + neStab + nwStab) - (oppyStab + oppxStab + oppneStab + oppyStab)*(oppyStab + oppxStab + oppneStab + oppyStab);

		}
	}

	return value;
}
int Corner(int n[8][8], int mine, int yours) {//checks who the corners belong to
	signed int value = 0;
	if (n[0][0] == mine) {
		value++;
	}
	else if (n[0][0] == yours) {
		value--;
	}
	if (n[0][8] == mine) {
		value++;
	}
	else if (n[0][8] == yours) {
		value--;
	}
	if (n[8][0] == mine) {
		value++;
	}
	else if (n[8][0] == yours) {
		value--;
	}
	if (n[8][8] == mine) {
		value++;
	}
	else if (n[8][8] == yours) {
		value--;
	}
	
	return value;
}
int shittySquares(int n[8][8], int mine, int yours) {
	int value = 0;
	value = -1 * (-5 * n[0][0] + n[1][0] + n[0][1] + 3 * n[1][1] + -5*n[0][7]+n[0][6] + n[1][7] + 3*n[1][6] + -5*n[7][0]+n[6][0] + 3 * n[6][1] + n[7][1] +  -5*n[7][7]+n[7][6] + 3 * n[6][6] + n[6][7]);
	return value;
}

void possibleMove(int orig[8][8], int n[8][8],int r, int c, int mine, int yours) {//creates new board based upon move
	for (int i = 0; i < 8; i++) {
		for (int j = 0; j < 8; j++) {
			n[i][j] = orig[i][j];
		}
	}
	n[r][c] = mine;
	int flipCounter = 0;
	//check for turnings
	for (int i = r - 1; i >= 0; i--) { //check up
		if (n[i][c] == yours) {
			flipCounter++;
		}
		else if (n[i][c] == blank) {
			flipCounter = 0;
			break;
		}
		else if (n[i][c] == mine) {
			for (int i = r - 1; flipCounter != 0; i--) {//flips all moves
				n[i][c] = mine;
				flipCounter--;
			}break;
		}
	}
	flipCounter = 0;

	for (int i = r + 1; i<8; i++) { //check dwn
		if (n[i][c] == yours) {
			flipCounter++;
		}
		else if (n[i][c] == blank) {
			flipCounter = 0;
			break;
		}
		else if (n[i][c] == mine) {
			for (int i = r + 1; flipCounter != 0; i++) {//flips all moves
				n[i][c] = mine;
				flipCounter--;
			}break;
		}
	}
	flipCounter = 0;

	for (int i = c - 1; i >= 0; i--) { //check left
		if (n[r][i] == yours) {
			flipCounter++;
		}
		else if (n[r][i] == blank) {
			flipCounter = 0;
			break;
		}
		else if (n[r][i] == mine) {
			for (int i = c - 1; flipCounter != 0; i--) {//flips all moves
				n[r][i] = mine;
				flipCounter--;
				
			}break;
		}
	}
	flipCounter = 0;

	for (int i = c + 1; i <8; i++) { //check rgt
		if (n[r][i] == yours) {
			flipCounter++;
		}
		else if (n[r][i] == blank) {
			flipCounter = 0;
			break;
		}
		else if (n[r][i] == mine) {
			for (int i = c + 1; flipCounter != 0; i++) {//flips all moves
				n[r][i] = mine;
				flipCounter--;
			}break;
		}
	}
	flipCounter = 0;

	for (int i = r - 1, j = c - 1; ((i >= 0) && (j >= 0)); i--, j--) { //check nw
		if (n[i][j] == yours) {
			flipCounter++;
		}
		else if (n[i][j] == blank) {
			flipCounter = 0;
			break;
		}
		else if (n[i][j] == mine) {
			for (int i = r - 1, j = c - 1; flipCounter != 0; i--, j--) {//flips all moves
				n[i][j] = mine;
				flipCounter--;
			}break;
		}
	}
	flipCounter = 0;

	for (int i = r + 1, j = c - 1; ((i < 8) && (j >= 0)); i++, j--) { //check se
		if (n[i][j] == yours) {
			flipCounter++;
		}
		else if (n[i][j] == blank) {
			flipCounter = 0;
			break;
		}
		else if (n[i][j] == mine) {
			for (int i = r + 1, j = c - 1; flipCounter != 0; i++, j--) {//flips all moves
				n[i][j] = mine;
				flipCounter--;
			}break;
		}
	}
	flipCounter = 0;

	for (int i = r - 1, j = c + 1; ((i >= 0) && (j < 8)); i--, j++) { //check nw
		if (n[i][j] == yours) {
			flipCounter++;
		}
		else if (n[i][j] == blank) {
			flipCounter = 0;
			break;
		}
		else if (n[i][j] == mine) {
			for (int i = r - 1, j = c + 1; flipCounter != 0; i--, j++) {//flips all moves
				n[i][j] = mine;
				flipCounter--;
			}break;
		}
	}
	flipCounter = 0;

	for (int i = r + 1, j = c + 1; ((i < 8) && (j < 8)); i++, j++) { //check se
		if (n[i][j] == yours) {
			flipCounter++;
		}
		else if (n[i][j] == blank) {
			flipCounter = 0;
			break;
		}
		else if (n[i][j] == mine) {
			for (int i = r + 1, j = c + 1; flipCounter != 0; i++, j++) {//flips all moves
				n[i][j] = mine;
				flipCounter--;
			}break;
		}
	}
	flipCounter = 0;

	return;
}
int futureMoves(int n[8][8], int turn, int yours) {
	int value = 0;
	for (int i = 0; i < 8; i++) {
		for (int j = 0; j < 8; j++) {
			if (n[i][j] == blank){
				if ((i > 0) && (n[i - 1][j]==yours)) {//check up
					value++;
				}
				if ((i < 7) && (n[i + 1][j] == yours)){//check dwn
					value++;
				}
				if ((j > 0) && (n[i][j-1] == yours)) {//check left
					value++;
				}
				if ((j<7) && (n[i][j+1] == yours)) {//check right
					value++;
				}
				if (((i > 0)&&(j > 0)) && (n[i-1][j-1] == yours)){//check top left
					value++;
				}
				if (((i > 0) && (j <7)) && (n[i-1][j+1] == yours)){//check top right
					value++;
				}
				if (((i<7)&&(j>0))&&(n[i+1][j-1] == yours)) {//check bottom left
					value++;
				}
				if (((i<7)&&(j<7)) && (n[i+1][j+1] == yours)) {//check bottom right
					value++;
				}
			}
		}
	}

	return value;
}
bool isterminal(int state[8][8], int t)
{
	moves = availableMoves(state, t, t*-1);
	if (moves == "b") {
		return 1;
	}
	/*for (int i = 0; i < 8; i++) {
		for (int j = 0; j < 8; j++) {
			if (state[i][j] != blank) {
				return 0;
			}
		}
	}
	*/
	return 0;
}
int moveNum(stateType n[8][8], int mine, int yours, int refind) {//counts the number of available moves for mine
	if (refind) {
		int num = (availableMoves(n, mine,yours).length() - 1) / 2;
		return num;
	}
	else {
		int num = (moves.length() - 1) / 2;
		return num;
	}
	
	
	
}
void expand(stateType state[8][8], string  successor[], int &sn, int turn)
{
	
	sn = moveNum(state, turn , turn*-1, 0);
	
	for (int k = 0; k < sn; k++) {
		string rc = moves.substr(moves.length()-2, moves.length() - 1);
		moves = moves.substr(0, moves.length() - 2);
		successor[k] = rc;
	}
	//	if (turn==maxturn)
	//	swap(successor[0],successor[2]);

}
int Eval(int n[8][8], int turn) { //Evaluate the State of the board. Return a value representing  
	int s = stabMulti * Stability(n, turn, turn*-1) - oppStabMulti * Stability(n, -1*turn, turn);
	int c = CornerMulti*Corner(n, turn, turn*-1);
	int m = moveNumMulti * moveNum(n, turn, turn*-1, 1);

	int o = -OppMoveMulti * moveNum(n, -1*turn, turn, 1);
	int ss = shitty * shittySquares(n, turn, turn*-1);
	//int fm = fmMulti* futureMoves(n, turn, turn*-1);
	/*cout << "movenum " << m << endl;
	cout << "fm " << fm << endl;
	cout << "stability" << s << endl;
	cout << "Corner" << c << endl;
	cout << "OppositeMoves" << o << endl;
	cout << "Shitty"<< ss <<endl;
	*/
	int v =s + c + m + o + ss;
	
	return v;
}

//Perform Alpha-Beta Pruning 
int alphabeta(stateType state[8][8], int maxDepth, int curDepth, int alpha, int beta)
{
	nodecount++;
	int succnum, turn;
	if (curDepth % 2 == 0) // This is a MAX node 
		turn = maxturn;
	else
		turn = minturn;
	//cout << "entetring " << state << endl;
	if (curDepth == maxDepth || isterminal(state, turn)) // CUTOFF test
	{
		int UtilV = Eval(state, turn);
		//cout << state << " [" << UtilV << "]\n";
		return UtilV;  // eval returns the heuristic value of state
	}
	string successor[maxsucc];
	expand(state, successor, succnum, turn); // find all successors of state

	if (turn == maxturn) // This is a MAX node 
						 // since MAX has depth of: 0, 2, 4, 6, ...
	{
		alpha = VS; // initialize to some very small value 
		for (int k = 0; k<succnum; k++)
		{
			// recursively find the value of each successor
			int c = successor[k].at(successor[k].length() - 1) - '0';
			int r = successor[k].at(successor[k].length() - 2) - '0';
			int n[8][8];
			possibleMove(state,n, r, c, turn, turn*-1);
			int curvalue = alphabeta(n, maxDepth, curDepth + 1, alpha, beta);
			//alpha = max(alpha,curvalue); // update alpha
			if (curvalue>alpha || curvalue == alpha && time(0) % 2 == 0)
			{
				alpha = curvalue;
				if (curDepth == 0)
					best = successor[k];
			}
			if (alpha >= beta) return alpha; // best = successor[k];
		}
		//cout << state << " [" << alpha << "]\n";
		return alpha;
	}
	else // A MIN node
	{
		beta = VL;  // initialize to some very large value
		for (int k = 0; k<succnum; k++)
		{
			// recursively find the value of each successor
			int c = successor[k].at(successor[k].length() - 1) - '0';
			int r = successor[k].at(successor[k].length() - 2) - '0';
			int n[8][8];
			possibleMove(state, n, r, c, turn, turn*-1);
			int curvalue = alphabeta(n, maxDepth, curDepth + 1, alpha, beta);
			if (beta > curvalue) {// update beta
				beta = curvalue;
			}
			if (alpha >= beta) return beta;
		}
		//cout << state << " [" << beta << "]\n";
		return beta;
	}
	
}

int main()
{
	//int n[8][8] = { 0 };

    //Test board 1 represents Self -1 represents opponent
	int n[8][8] = {
        {0,0,0,0,0,0,0,0},
        {0,0,0,0,0,0,0,0},
        {0,0,0,0,1,0,0,0},
        {0,0,0,1,1,0,0,0},
        {0,0,0,-1,1,0,0,0},
        {0,0,0,0,0,0,0,0},
        {0,0,0,0,0,0,0,0},
        {0,0,0,0,0,0,0,0}};
	//n[3][3] = oppColor;
	//n[4][4] = oppColor;
	//n[3][4] = myColor;
	//n[4][3] = myColor;
    //String UserInput;
	//cin >> UserInput;
    //n int(UserInput)
    //getGameBoard(n);
	int value = alphabeta(n, 4, 0, VS, VL);
	cout << "best value " << value  << endl;
	cout << "move " << best << endl;
	cout << nodecount << endl;
	//int r;
	//int c;
   
	
	//system("pause");
	int r = best.at(best.length() - 2)- '0';
	int c = best.at(best.length() - 1)- '0';
	//putMove(r, c);
    
}

