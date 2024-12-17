import random
import time

import pygame
import pygame_widgets

from src.astar import solve_astar
from src.bfs import solve_bfs
from src.events import *
from src.game import Game
from src.generator import generate
from src.utils import play_solution
from src.widgets import sidebar_widgets

# Set the seed for random number generation to ensure reproducibility.
random.seed(6)  

def play_game(window, level=1, random_game=False, random_seed=None, **widgets):
    moves = runtime = 0
    show_solution = False
    widgets['paths'].transparency = False
    
    # If random_game is True, generate a new random puzzle
    if random_game:
        if not random_seed:
            random_seed = random.randint(0, 99999)  # Generate a random seed if one is not provided
        generate(window, seed=random_seed, visualizer=widgets['toggle'].getValue())
    
    # Show or hide navigation buttons based on the current level,
    # Level from 1 through 17
    if level <= 1:
        widgets['prev_button'].hide()
    else:
        widgets['prev_button'].show()
    
    if level >= 17:
        widgets['next_button'].hide()
    else:
        widgets['next_button'].show()
    
    # Update the label to show either the level number or the seed used for the random game
    if random_game or level == 0:
        widgets['label'].set_text(f'Seed {random_seed}', 18)  # Show seed for random game, font size 18
    else:
        widgets['label'].set_text(f'Level {level}', 30)  # Show current level number, font size 30
    
    # Initialize the game with the given level
    game = Game(level=level, window=window)
    game_loop = True
    
    while game_loop:
        events = pygame.event.get()  # Retrieve all the events from the event queue
        
        for event in events:
            if event.type == pygame.QUIT:
                game_loop = False
                return {
                    'keep_playing': False,
                    'reset': -1, 
                    'random_game': False,
                }
            elif event.type == RESTART_EVENT:
                game_loop = False
                print(f'Restarting level {level}\n')
                window.fill((0, 0, 0, 0))  # Clear the screen
                return {
                    'keep_playing': True,
                    'reset': level, 
                    'random_game': random_game,
                    'random_seed': random_seed,
                }
            elif event.type == PREVIOUS_EVENT:
                game_loop = False
                print(f'Previous level {level - 1}\n')
                window.fill((0, 0, 0, 0))  # Clear the screen
                return {
                    'keep_playing': True,
                    'reset': level - 1, 
                    'random_game': False
                }
            elif event.type == NEXT_EVENT:
                game_loop = False
                print(f'Next level {level + 1}\n')
                window.fill((0, 0, 0, 0))  # Clear the screen
                return {
                    'keep_playing': True,
                    'reset': level + 1, 
                    'random_game': False
                }
            elif event.type == RANDOM_GAME_EVENT:
                game_loop = False
                print('Loading a random puzzle\n')
                window.fill((0, 0, 0, 0))  # Clear the screen
                new_seed = None
                try:
                    new_seed = int(widgets['seedbox'].getText())  # Get seed from the input box
                    if new_seed < 1 or new_seed > 99999: # 1 <= seed <= 99999
                        new_seed = None
                        raise ValueError('Seed must be between 1 and 99999')
                except ValueError as e:
                    print(e)
                return {
                    'keep_playing': True,
                    'reset': 0, 
                    'random_game': True,
                    'random_seed': new_seed
                }
            elif event.type == SOLVE_BFS_EVENT:
                print('Finding a solution for the puzzle\n')
                widgets['paths'].reset('Solving with [BFS]')
                show_solution = True
                start = time.time()  # Record start time
                solution, depth = solve_bfs(
                    game.get_matrix(), 
                    widget=widgets['paths'], 
                    visualizer=widgets['toggle'].getValue()
                )
                runtime = round(time.time() - start, 5)  # Calculate runtime
                if solution:
                    widgets['paths'].solved = True
                    widgets['paths'].transparency = True
                    widgets['paths'].set_text(
                        f'[BFS] Solution Found in {runtime}s!\n{solution}',
                        20,
                    )
                    moves = play_solution(solution, game, widgets, show_solution, moves)
                else:
                    widgets['paths'].solved = False
                    widgets['paths'].set_text(
                        '[BFS] Solution Not Found!\n' + 
                        ('Deadlock Found!' if depth < 0 else f'Depth {depth}'), 
                        20,
                    )
            elif event.type == SOLVE_ASTARMAN_EVENT:
                print('Finding a solution for the puzzle\n')
                widgets['paths'].reset('Solving with [A*]')
                show_solution = True
                start = time.time()  # Record start time
                solution, depth = solve_astar(
                    game.get_matrix(), 
                    widget=widgets['paths'], 
                    visualizer=widgets['toggle'].getValue(),
                    heuristic='manhattan',
                )
                runtime = round(time.time() - start, 5)  # Calculate runtime
                if solution:
                    widgets['paths'].solved = True
                    widgets['paths'].transparency = True
                    widgets['paths'].set_text(
                        f'[A*] Solution Found in {runtime}s!\n{solution}',
                        20,
                    )
                    moves = play_solution(solution, game, widgets, show_solution, moves)
                else:
                    widgets['paths'].solved = False
                    widgets['paths'].set_text(
                        '[A*] Solution Not Found!\n' + 
                        ('Deadlock Found!' if depth < 0 else f'Depth {depth}'), 
                        20,
                    )
            elif event.type == SOLVE_DIJKSTRA_EVENT:
                print('Finding a solution for the puzzle\n')
                widgets['paths'].reset('Solving with [Dijkstra]')
                show_solution = True
                start = time.time()  # Record start time
                solution, depth = solve_astar(
                    game.get_matrix(), 
                    widget=widgets['paths'], 
                    visualizer=widgets['toggle'].getValue(),
                    heuristic='dijkstra',
                )
                runtime = round(time.time() - start, 5)  # Calculate runtime
                if solution:
                    widgets['paths'].solved = True
                    widgets['paths'].transparency = True
                    widgets['paths'].set_text(
                        f'[Dijkstra] Solution Found in {runtime}s!\n{solution}',
                        20
                    )
                    moves = play_solution(solution, game, widgets, show_solution, moves)
                else:
                    widgets['paths'].solved = False
                    widgets['paths'].set_text(
                        '[Dijkstra] Solution Not Found!\n' + 
                        ('Deadlock Found!' if depth < 0 else f'Depth {depth}'), 
                        20,
                    )
            elif event.type == pygame.KEYDOWN:
                # Handle player movement based on key presses
                if event.key in (pygame.K_d, pygame.K_RIGHT):
                    moves += game.player.update(key='R')  # Move player right
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    moves += game.player.update(key='L')  # Move player left
                elif event.key in (pygame.K_w, pygame.K_UP):
                    moves += game.player.update(key='U')  # Move player up
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    moves += game.player.update(key='D')  # Move player down
        
        # Draw game objects and update the display
        game.floor_group.draw(window)
        game.goal_group.draw(window)
        game.object_group.draw(window)
        pygame_widgets.update(events)
        widgets['label'].draw()
        widgets['seed'].draw()
        widgets['visualizer'].draw()
        widgets['moves_label'].set_moves(f' Moves = {moves} ', 20)
        if show_solution:
            widgets['paths'].draw()
        pygame.display.update()
        
        # Check if the level is completed
        if game.is_level_complete():
            print(f'Level Complete! - {moves} moves')
            widgets['level_clear'].draw()
            pygame.display.update()
            game_loop = False
            wait = True
            while wait:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        wait = False
    del game
    print('Objects cleared!\n')
    return {
        'keep_playing': True,
        'reset': 0 if random_game else -1, 
        'random_game': random_game,
    }

def run_statistics():
    algorithms = [
        ('A*manhattan', lambda game: solve_astar(game.get_matrix(), heuristic='manhattan')),
        ('Dijkstra', lambda game: solve_astar(game.get_matrix(), heuristic='dijkstra')),
        ('BFS', lambda game: solve_bfs(game.get_matrix()))
    ]
    
    with open('stat/ statistics.txt', 'w') as f:
        f.write("Level, Algorithm, Runtime, Depth\n")
        
        for algo_name, algo_func in algorithms:
            for level in range(1, 31):
                game = Game(level=level)
                start_time = time.time()
                _, depth = algo_func(game)
                runtime = round(time.time() - start_time, 5)
                
                f.write(f"{level}, {algo_name}, {runtime}, {depth}\n")
                print(f"Completed {algo_name} for level {level}")
    
    print("Statistics saved to statistics.txt")

def main():
    pygame.init()
    displayIcon = pygame.image.load('img/icon.png')  # Load the game icon
    pygame.display.set_icon(displayIcon)  # Set the game icon
    window = pygame.display.set_mode((1216, 640))  # Set the size of the game window
    pygame.display.set_caption('Sokoban Solver - 20241IT6094003 - Group 5')  # Set the title of the window
    level = 1
    keep_playing = True
    random_game = False
    random_seed = None
    widgets = sidebar_widgets(window)  # Initialize sidebar widgets
    
    while keep_playing:
        print(f'Loading level {level}\n' if level > 0 else 'Loading random game')
        game_data = play_game(window, level, random_game, random_seed, **widgets)
        keep_playing = game_data.get('keep_playing', False)
        if not keep_playing:
            pygame.quit()  
            quit()
        reset = game_data.get('reset', -1)
        random_game = game_data.get('random_game', False)
        random_seed = game_data.get('random_seed')
        # Move to the next level or handle random game
        # If reset = -1, lv + 1, max = 17
        level = reset if reset >= 0 else min(level + 1, 17)  

if __name__ == '__main__':
    # wall: +, box: @, player: *, goal: X, box on goal: $, player on goal: %, empty: -
    main()