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

class TestJumpSpell:
    #done
    def test_player_can_jump_own_non_king_piece_to_empty_square(self):
        game = SpellChessGame()

        assert game.cast_jump(chess.B1, chess.C3) is True

        assert game.board.piece_at(chess.B1) is None
        piece = game.board.piece_at(chess.C3)
        assert piece is not None
        assert piece.color == chess.WHITE
        assert piece.piece_type == chess.KNIGHT

    #done
    def test_jump_only_once_per_turn(self):
        game = SpellChessGame()

        assert game.cast_jump(chess.B1, chess.C3) is True
        assert game.cast_jump(chess.G1, chess.H3) is False

    #done
    def test_jump_must_be_cast_before_making_move(self):
        game = SpellChessGame()

        assert game.make_move(chess.E2, chess.E4) is True

        game.board.turn = chess.WHITE
        assert game.cast_jump(chess.G1, chess.H3) is False

    #done
    def test_jump_can_only_be_cast_on_own_piece(self):
        game = SpellChessGame()

        assert game.cast_jump(chess.B8, chess.C6) is False

        assert game.board.piece_at(chess.B8) is not None
        assert game.board.piece_at(chess.C6) is None

    #done
    def test_jump_destination_must_be_empty(self):
        game = SpellChessGame()

        assert game.cast_jump(chess.B1, chess.D2) is False

        assert game.board.piece_at(chess.B1) is not None
        assert game.board.piece_at(chess.D2).piece_type == chess.PAWN

    #done
    def test_king_cannot_jump(self):
        game = SpellChessGame()
        game.board.remove_piece_at(chess.E2)

        assert game.cast_jump(chess.E1, chess.E2) is False

        assert game.board.piece_at(chess.E1) is not None
        assert game.board.piece_at(chess.E2) is None

    #done
    def test_jump_destination_must_be_within_chebyshev_distance_two(self):
        game = SpellChessGame()

        assert game.cast_jump(chess.B1, chess.B4) is False

        assert game.board.piece_at(chess.B1) is not None
        assert game.board.piece_at(chess.B4) is None

class TestJumpDestinationMustBeEmpty:
    #done
    def test_jump_cannot_land_on_own_piece(self):
        game = SpellChessGame()

        assert game.cast_jump(chess.B1, chess.D2) is False

        assert game.board.piece_at(chess.B1).piece_type == chess.KNIGHT
        assert game.board.piece_at(chess.D2).piece_type == chess.PAWN
    #done
    def test_jump_cannot_land_on_opponent_piece(self):
        game = SpellChessGame()

        game.board.set_piece_at(chess.C3, chess.Piece(chess.PAWN, chess.BLACK))

        assert game.cast_jump(chess.B1, chess.C3) is False

        assert game.board.piece_at(chess.B1).piece_type == chess.KNIGHT
        assert game.board.piece_at(chess.C3).piece_type == chess.PAWN
        assert game.board.piece_at(chess.C3).color == chess.BLACK
    #done
    def test_jump_cannot_capture_piece(self):
        game = SpellChessGame()

        game.board.set_piece_at(chess.C3, chess.Piece(chess.BISHOP, chess.BLACK))

        assert game.cast_jump(chess.B1, chess.C3) is False

        start_piece = game.board.piece_at(chess.B1)
        dest_piece = game.board.piece_at(chess.C3)

        assert start_piece is not None
        assert start_piece.piece_type == chess.KNIGHT
        assert start_piece.color == chess.WHITE

        assert dest_piece is not None
        assert dest_piece.piece_type == chess.BISHOP
        assert dest_piece.color == chess.BLACK

class TestJumpCooldown:
    def test_jump_starts_two_turn_cooldown_after_casting(self):
        game = SpellChessGame()

        assert game.cast_jump(chess.B1, chess.C3) is True
        assert game.jump_cooldown[chess.WHITE] == 2

    def test_cooldown_decreases_by_one_at_start_of_casters_turn(self):
        game = SpellChessGame()

        assert game.cast_jump(chess.B1, chess.C3) is True
        assert game.jump_cooldown[chess.WHITE] == 2

        game.board.turn = chess.BLACK
        game.make_move(chess.E7, chess.E5)

        assert game.board.turn == chess.WHITE
        assert game.jump_cooldown[chess.WHITE] == 1

    def test_caster_cannot_jump_while_cooldown_is_not_zero(self):
        game = SpellChessGame()

        assert game.cast_jump(chess.B1, chess.C3) is True

        game.board.turn = chess.BLACK
        game.make_move(chess.E7, chess.E5)

        assert game.jump_cooldown[chess.WHITE] == 1
        assert game.cast_jump(chess.G1, chess.H3) is False

    def test_caster_can_jump_again_when_cooldown_reaches_zero(self):
        game = SpellChessGame()

        assert game.cast_jump(chess.B1, chess.C3) is True

        game.board.turn = chess.BLACK
        game.make_move(chess.E7, chess.E5)

        game.on_turn_start()

        assert game.jump_cooldown[chess.WHITE] == 0
        assert game.cast_jump(chess.G1, chess.H3) is True

class TestGameStateDisplay:
    def test_status_text_displays_whose_turn_it_is(self):
        game = SpellChessGame()

        assert game.status_text() == "Turn: White."

        game.board.turn = chess.BLACK
        assert game.status_text() == "Turn: Black."

    def test_status_text_displays_when_current_player_is_in_check(self):
        game = SpellChessGame()
        game.board.clear_board()

        game.board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
        game.board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
        game.board.set_piece_at(chess.E7, chess.Piece(chess.ROOK, chess.WHITE))
        game.board.turn = chess.BLACK

        assert game.status_text() == "Turn: Black (check)."


class TestFreezeDisplay:
    def test_freeze_label_shows_current_players_remaining_charges(self):
        game = SpellChessGame()
        game.freeze_remaining[chess.WHITE] = 4
        game.freeze_remaining[chess.BLACK] = 2

        game.board.turn = chess.WHITE
        assert game.freeze_info_text() == "Freeze: 4"

        game.board.turn = chess.BLACK
        assert game.freeze_info_text() == "Freeze: 2"

    def test_freeze_label_shows_current_players_cooldown(self):
        game = SpellChessGame()
        game.freeze_remaining[chess.WHITE] = 4
        game.freeze_cooldown[chess.WHITE] = 3
        game.board.turn = chess.WHITE

        assert game.freeze_info_text() == "Freeze: 4  (cooldown 3)"

    def test_freeze_label_shows_frozen_note_when_active(self):
        game = SpellChessGame()

        game.board.turn = chess.BLACK
        game.freeze_effect_color = chess.BLACK
        game.freeze_effect_squares = {chess.E7}
        game.freeze_effect_plies_left = 1

        assert game.freeze_info_text() == "Freeze: 5  — pieces in area are frozen"


class TestJumpDisplay:
    def test_jump_label_shows_current_players_remaining_charges(self):
        game = SpellChessGame()
        game.jump_remaining[chess.WHITE] = 2
        game.jump_remaining[chess.BLACK] = 1

        game.board.turn = chess.WHITE
        assert game.jump_info_text() == "Jump: 2"

        game.board.turn = chess.BLACK
        assert game.jump_info_text() == "Jump: 1"

    def test_jump_label_shows_current_players_cooldown(self):
        game = SpellChessGame()
        game.jump_remaining[chess.WHITE] = 2
        game.jump_cooldown[chess.WHITE] = 2
        game.board.turn = chess.WHITE

        assert game.jump_info_text() == "Jump: 2  (cooldown 2)"
