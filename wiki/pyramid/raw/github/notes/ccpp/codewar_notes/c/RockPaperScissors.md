## DESCRIPTION:

Rock Paper Scissors
Let's play! You have to return which player won! In case of a draw return Draw!.

Examples(Input1, Input2 --> Output):
```
"scissors", "paper" --> "Player 1 won!"
"scissors", "rock" --> "Player 2 won!"
"paper", "paper" --> "Draw!"
```

## Solution

```c
enum tool {ROCK, PAPER, SCISSORS};
enum outcome {P1_WON, P2_WON, DRAW};

enum outcome rps (enum tool p1, enum tool p2)
{
  if (p1 == p2) return DRAW;
  else {
    switch(p1) {
        case ROCK:
          if (p2 == PAPER) return P2_WON;
          else break;
        case PAPER:
          if (p2 == SCISSORS) return P2_WON;
          else break;
        case SCISSORS:
          if (p2 == ROCK) return P2_WON;
          else break;
    }
    
    return P1_WON;
  }
  
}
```
思路： 直接遍历比较。

### Best Practice

```c
enum tool {ROCK, PAPER, SCISSORS};
enum outcome {P1_WON, P2_WON, DRAW};

enum outcome rps (enum tool p1, enum tool p2)
{
	return (enum outcome [3][3]) {
		[ROCK]     = {[ROCK] = DRAW,   [PAPER] = P2_WON, [SCISSORS] = P1_WON},
		[PAPER]    = {[ROCK] = P1_WON, [PAPER] = DRAW,   [SCISSORS] = P2_WON},
		[SCISSORS] = {[ROCK] = P2_WON, [PAPER] = P1_WON, [SCISSORS] = DRAW},
	}[p1][p2];
}
```

直接查表， 快速简介.

