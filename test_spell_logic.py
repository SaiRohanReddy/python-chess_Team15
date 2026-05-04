"""
Unit tests for Spell Chess game logic.

Run with:
    pytest test_spell_logic.py -v

These tests verify the Spell Chess rules described in SPELL_CHESS_RULES.md.
Each test creates a fresh SpellChessGame, sets up a position, performs an
action, and checks that the result matches the specification.
"""

import chess
from spell_logic import SpellChessGame, squares_in_3x3, squares_in_jump_range


# ------------------------------------------------------------------ #
#  Demo tests — provided to students as examples                      #
# ------------------------------------------------------------------ #

class TestFreezeTarget:
    """Casting Freeze should mark the opponent's color as frozen."""

    def test_freeze_affects_opponent_not_caster(self):
        game = SpellChessGame()
        # White casts freeze
        game.cast_freeze(chess.E5)
        # The frozen color should be Black (the opponent), not White
        assert game.freeze_effect_color == chess.BLACK


class TestNewGameResetsBoard:
    """Calling new_game() should bring the board back to the starting position."""

    def test_board_resets_after_moves(self):
        game = SpellChessGame()
        game.board.push_san("e4")
        game.new_game()
        assert game.board.fen() == chess.STARTING_FEN


# ------------------------------------------------------------------ #
#  YOUR TESTS GO BELOW                                                #
#  Write tests that check the rules from SPELL_CHESS_RULES.md.        #
#  If a test fails, you've found a bug — document it!                 #
# ------------------------------------------------------------------ #
class TestFreezeSpellCastling: 
    """Calling Frezze Spell should be affect 3x3 area which will 9 squares total in middle area"""
    def test_castling_frezze_in_middle(self): 
        game = SpellChessGame()
        game.cast_freeze(chess.E5)
        expected = { 
            chess.E5,
            chess.E6, chess.E4,
            chess.D5, chess.F5,
            chess.D4, chess.F6,
            chess.D6, chess.F4
        }
        assert game.freeze_effect_squares == expected
    def test_castling_frezze_in_edge(self):
        """Calling Freeze Spell should included the center square"""
        game = SpellChessGame()
        game.cast_freeze(chess.A1)
        expected={ 
            chess.A1,
            chess.A2,
            chess.B1,
            chess.B2
        }
        assert game.freeze_effect_squares == expected
    def test_castling_turn(self): 
        """Update spell casted current turn should be return True, since the cast_freeze() has been called"""
        game = SpellChessGame()
        game.cast_freeze(chess.E5)
        assert game.spell_casted_this_turn == True

class TestFreezeSpellEffect:
    def test_freeze_affects_o_not_c(self):
        """Like Example; Castling Freeze should mark opponent color"""
        game = SpellChessGame()
        game.cast_freeze(chess.E5)
        assert game.freeze_effect_color == chess.BLACK

    def test_freeze_unmoveable(self): 
        """Test for unmoveable"""
        game = SpellChessGame()
        game.cast_freeze(chess.E5)
        game.make_move(chess.E2, chess.E4)
        expected = {chess.E5,
            chess.E6, chess.E4,
            chess.D5, chess.F5,
            chess.D4, chess.F6,
            chess.D6, chess.F4
        }
        legal_move_square = {move.from_square for move in game.get_legal_moves()}
        assert legal_move_square != expected
    def test_freeze_expires_after_one_turn(self):
        """Test for expires affect after opponent's turn"""
        game = SpellChessGame()
        game.cast_freeze(chess.D4)
        game.make_move(chess.A2, chess.A3)
        # game.board.turn= chess.BLACK
        black_moves = game.get_legal_moves()
        game.make_move(black_moves[0].from_square, black_moves[0].to_square)
        # game.board.turn = chess.WHITE
        assert game.freeze_effect_plies_left == 0
        assert game.freeze_effect_color is None
        assert len(game.freeze_effect_squares) == 0
    
    def test_frozen_pieces_still_give_check(self):
        """Test for frozen pieces still giving check""" 
        game = SpellChessGame()
        game.board.clear()
        game.board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
        game.board.set_piece_at(chess.E5, chess.Piece(chess.QUEEN, chess.BLACK))
        game.board.turn = chess.WHITE
        game.cast_freeze(chess.E5)
        game.make_move(chess.E1, chess.E2)
        black_moves = game.get_legal_moves()
        queen_moves =[m for m in black_moves if m.from_square == chess.E5]
        assert game.board.is_check() == True
        assert len(queen_moves) == 0

    def test_frozen_pieces_still_block(self): 
        """Test for frozen pieces that block the way"""
        game= SpellChessGame()
        game.board.clear()
        game.board.set_piece_at(chess.E4, chess.Piece(chess.PAWN, chess.WHITE))
        game.board.set_piece_at(chess.E5, chess.Piece(chess.PAWN, chess.BLACK))
        game.board.turn = chess.WHITE
        game.cast_freeze(chess.E6)
        game.board.turn = chess.BLACK
        black_move = game.get_legal_moves()
        pawn_move = [m for m in black_move if m.from_square == chess.E4]
        assert len(pawn_move) == 0 

def test_freeze_no_valid_moves_when_all_pieces_frozen(self):
    """Test that player has no valid moves when all their pieces are on frozen squares."""
    game = SpellChessGame()
    
    game.board.clear()
    
    game.board.set_piece_at(chess.E5, chess.Piece(chess.KING, chess.WHITE))
    game.board.set_piece_at(chess.E4, chess.Piece(chess.PAWN, chess.WHITE))
    game.board.set_piece_at(chess.E6, chess.Piece(chess.PAWN, chess.WHITE))
    game.board.set_piece_at(chess.D5, chess.Piece(chess.PAWN, chess.WHITE))
    game.board.set_piece_at(chess.F5, chess.Piece(chess.PAWN, chess.WHITE))
    game.board.set_piece_at(chess.D4, chess.Piece(chess.PAWN, chess.WHITE))
    game.board.set_piece_at(chess.D6, chess.Piece(chess.PAWN, chess.WHITE))
    game.board.set_piece_at(chess.F4, chess.Piece(chess.PAWN, chess.WHITE))
    game.board.set_piece_at(chess.F6, chess.Piece(chess.PAWN, chess.WHITE))
    
    game.board.turn = chess.WHITE
    
    game.cast_freeze(chess.E5)
    
    frozen_squares = {chess.E5, chess.E6, chess.E4, chess.D5, 
                    chess.F5, chess.D4, chess.F6, chess.D6, chess.F4}
    game.board.turn = chess.BLACK
    
    white_pieces = game.board.pieces(chess.PAWN, chess.WHITE) | game.board.pieces(chess.KING, chess.WHITE)
    for square in white_pieces:
        assert square in frozen_squares
        assert game.is_frozen(square, chess.WHITE)
        assert len(game.get_legal_moves()) == 0

class TestFreezeNewGame: 
    def test_new_game_reset_board(self): 
        """Reset the board to make the board to be bacnh to starting state of board"""
        game = SpellChessGame()
        game.make_move(chess.E2, chess.E4)
        game.make_move(chess.E7, chess.E5)


        game.new_game()

        assert game.board.fen() == chess.STARTING_FEN

    def test_reset_freeze_cooldown(self):
        """Reset the freeze cooldown after called new game function"""
        game = SpellChessGame()
        game.make_move(chess.E2, chess.E4)
        game.make_move(chess.E7, chess.E5)

        game.cast_freeze(chess.D4)
        game.freeze_cooldown[chess.WHITE] = 2
        game.freeze_cooldown[chess.BLACK] = 1

        game.new_game()

        assert game.freeze_cooldown[chess.WHITE] == 0
        assert game.freeze_cooldown[chess.BLACK] == 0

    def test_reset_freeze_remaining(self): 
        """Reset the freeze charges after called new game function"""
        game = SpellChessGame()
        game.make_move(chess.E2, chess.E4)
        game.make_move(chess.E7, chess.E5)

        game.cast_freeze(chess.D4)

        game.freeze_remaining[chess.WHITE] = 3
        game.freeze_remaining[chess.BLACK] = 4

        game.new_game()


        assert game.freeze_remaining[chess.WHITE] == 5
        assert game.freeze_remaining[chess.BLACK] == 5

    def test_reset_freeze_effect(self): 
        """Reset the freeze effects after called new game function"""
        game = SpellChessGame()
        game.make_move(chess.E2, chess.E4)
        game.make_move(chess.E7, chess.E5)

        game.cast_freeze(chess.D4)

        game.freeze_effect_color = chess.BLACK
        game.freeze_effect_squares = {chess.E2, chess.E3, chess.E4}
        game.freeze_effect_plies_left = 2
         
        game.new_game()

        assert game.freeze_effect_color is None
        assert len(game.freeze_effect_squares) == 0
        assert game.freeze_effect_plies_left == 0

    def test_reset_freeze_flag(self):
        """Reset the freeze flag that currently active after called new game function"""

        game = SpellChessGame()
        game.make_move(chess.E2, chess.E4)
        game.make_move(chess.E7, chess.E5)

        game.cast_freeze(chess.D4)


        game.spell_casted_this_turn = True
        game.freeze_targeting = True

        game.new_game()

        assert not game.spell_casted_this_turn
        assert not game.freeze_targeting
        
