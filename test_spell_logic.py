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
class TestFreezeSpellCastling: 
    def test_castling_frezze_in_middle(self): 
       """Calling Frezze Spell should be affect 3x3 area which will 9 squares total in middle area"""
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
        

class TestFreezeChargesStart:
    """Each user should start the game with 5 freeze charges"""
    def test_freeze_charges_start(self):
        game = SpellChessGame()
        assert game.freeze_remaining[chess.WHITE] == 5
        assert game.freeze_remaining[chess.BLACK] == 5

class TestFreezeChargesDecrement:
    """Each cast costs 1 charge"""
    def test_freeze_charges_decrement(self):
        game = SpellChessGame()
        success = game.cast_freeze(chess.E5) 
        assert success == True #check that freeze was cast properly
        assert game.freeze_remaining[chess.WHITE] == 4
        assert game.freeze_remaining[chess.BLACK] == 5 #check that black was not decremented

class TestFreezeChargesNoCharges:
    """When a player has 0 charges left they cannot cast freeze"""
    def test_freeze_charges_no_charges(self):
        game = SpellChessGame()
        game.freeze_remaining[chess.WHITE] = 0 
        game.freeze_remaining[chess.BLACK] = 0
        success = game.cast_freeze(chess.E5)
        assert success == False #check that it did not cast

class TestFreezeCooldownStart:
    """After freeze spell is cast, the caster enters a 3 turn cooldown"""
    def test_freeze_cooldown_start(self):
        game = SpellChessGame()
        success = game.cast_freeze(chess.E5)
        assert success == True #check that cooldown was cast properly
        assert game.freeze_cooldown[chess.WHITE] == 3
        assert game.freeze_cooldown[chess.BLACK] == 0 #check that blacks cooldown remains at 0

class TestFreezeCooldownDecrement:
    """The cooldown decrements by 1 at the start of each of the caster's turns"""
    def test_freeze_cooldown_decrement(self):
        game = SpellChessGame()
        success = game.cast_freeze(chess.G2)
        cooldown = game.freeze_cooldown[chess.WHITE] #store starting cooldown amount
        assert success == True #check that freeze was cast properly
        success = game.make_move(chess.D2, chess.D4) #perform a turn
        assert success == True #check that turn was performed properly
        success = game.make_move(chess.A2, chess.A4) #perfrorm a turn
        assert success == True #check that turn was performed properly
        success = game.make_move(chess.B2, chess.B4) #perfrom a turn
        assert success == True #check that turn was performed properly
        success = game.make_move(chess.C2, chess.C4) #perfrom a turn
        assert success == True #check that turn was performed properly
        assert game.freeze_cooldown[chess.WHITE] < (cooldown) #check that cooldown is lower than it used to be

class TestFreezeCooldownRecast:
    """The caster cannot Freeze again until the cooldown reaches 0"""
    def test_freeze_cooldown_recast(self):
        game = SpellChessGame()
        success = game.cast_freeze(chess.G7)#white cast freeze
        assert success == True #check that freeze was cast properly
        success = game.make_move(chess.E2, chess.E4) #perfrom a move
        assert success == True #check that turn was performed properly
        success = game.make_move(chess.F2, chess.F4)#perfrom a move
        assert success == True #check that turn was performed properly
        assert game.freeze_cooldown[chess.WHITE] > 0 #make sure cooldwon is still above 0
        success = game.cast_freeze(chess.E5)#cast freeze
        assert success == False #check that freeze was not cast

class TestJumpNewGameResetCharges:
    """Starting a new game should reset the jump charges for both sides"""
    def test_jump_new_game_reset_charges(self):
        game = SpellChessGame()
        game.jump_remaining[chess.WHITE] = 2 #decrement charges
        game.jump_remaining[chess.BLACK] = 1 #decrement charges
        game.new_game() #new game
        assert game.jump_remaining[chess.WHITE] == 3 
        #check that charges were reset
        assert game.jump_remaining[chess.BLACK] == 3

class TestJumpNewGameResetCooldown:
    """Starting a new game should reset the jump charges for both sides"""
    def test_jump_new_game_reset_cooldown(self):
        game = SpellChessGame()
        game.jump_cooldown[chess.WHITE] = 1 #set cooldown
        game.jump_cooldown[chess.BLACK] = 1 #set cooldown
        game.new_game()
        #check that charges were reset
        assert game.jump_cooldown[chess.WHITE] == 0
        assert game.jump_cooldown[chess.BLACK] == 0

class TestJumpChargesStart:
    """Each user should start the game with 3 jump charges"""
    def test_jump_charges_start(self):
        game = SpellChessGame()
        assert game.jump_remaining[chess.WHITE] == 3
        assert game.jump_remaining[chess.BLACK] == 3

class TestJumpChargesDecrement:
    """Each cast costs 1 charge"""
    def test_jump_charges_decrement(self):
        game = SpellChessGame()
        success = game.cast_jump(chess.E2, chess.E5)
        assert success == True #check that jump was cast successfully
        assert game.jump_remaining[chess.WHITE] == 2
        assert game.jump_remaining[chess.BLACK] == 3 #check that black did not get decremented

class TestJumpChargesNoCharges:
    """When a player has 0 charges left they cannot cast freeze"""
    def test_jump_charges_no_charges(self):
        game = SpellChessGame()
        #set charges to 0
        game.jump_remaining[chess.WHITE] = 0
        game.jump_remaining[chess.BLACK] = 0
        success = game.cast_jump(chess.E2, chess.E5)
        assert success == False #check that it did not cast jump



class TestTurnLogic:
    """Game should switch to other players turn after move"""
    def test_turn_logic(self):
        game = SpellChessGame()
        success = game.make_move(chess.E2, chess.E4) #white move
        assert success == True #make sure that the move went through properly
        color = game.board.turn
        assert color == chess.BLACK 

class TestPieceMovement:
    def test_piece_movement_works(self):
        """test that you can move a piece"""
        game = SpellChessGame()

        assert game.make_move(chess.E2, chess.E4) is True

        assert game.board.piece_at(chess.E2) is None #check that it no longer has a piece at E2
        assert game.board.piece_at(chess.E4).piece_type == chess.PAWN #check that it now has a pawn at E4
        assert game.board.piece_at(chess.E4).color == chess.WHITE

class TestCheck:
    """test if the game can detect a check"""
    def test_check_is_detected(self):
        game = SpellChessGame()
        game.board.clear_board()
        #set up a check
        game.board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
        game.board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
        game.board.set_piece_at(chess.E7, chess.Piece(chess.ROOK, chess.WHITE))
        game.board.turn = chess.BLACK

        assert game.board.is_check() is True

class TestCheckmate2:
    """test if the game can recognize a checkmate"""
    def test_checkmate2(self):
        game = SpellChessGame()
        #set up checkamte
        game.board.clear_board()
        game.board.set_piece_at(chess.A8, chess.Piece(chess.KING, chess.BLACK))
        game.board.set_piece_at(chess.E7, chess.Piece(chess.QUEEN, chess.WHITE))
        game.board.set_piece_at(chess.H1, chess.Piece(chess.KING, chess.WHITE))
        game.board.set_piece_at(chess.B3, chess.Piece(chess.ROOK, chess.WHITE))
        game.board.set_piece_at(chess.C8, chess.Piece(chess.ROOK, chess.WHITE))
        game.board.turn = chess.BLACK
        #check if the game recognizes a checkmate
        assert game.is_game_over() == True
        outcome = game.outcome()
        assert outcome is not None
        assert outcome.winner == chess.WHITE
        assert outcome.termination == chess.Termination.CHECKMATE

class TestCheckmate:
    def test_checkmate(self):
        game = SpellChessGame()
        #set up checkmate
        game.board.clear_board()
        game.board.set_piece_at(chess.G7, chess.Piece(chess.QUEEN, chess.BLACK))
        game.board.set_piece_at(chess.F6, chess.Piece(chess.KING, chess.BLACK))
        game.board.set_piece_at(chess.H8, chess.Piece(chess.KING, chess.WHITE))
        game.board.turn = chess.WHITE
        #check if the game recognizes a checkmate
        assert game.is_game_over() == True
        outcome = game.outcome()
        assert outcome is not None
        assert outcome.winner == chess.BLACK
        assert outcome.termination == chess.Termination.CHECKMATE

class TestCaptures:
    """test that captures work"""
    def test_pawn_capture(self):
        game = SpellChessGame()
        assert game.make_move(chess.E2, chess.E4) == True
        game.board.turn = chess.BLACK #manualy change the turn since changing turns is bugged
        assert game.make_move(chess.D7, chess.D5) == True
        game.board.turn = chess.WHITE #manualy change the turn since changing turns is bugged
        assert game.make_move(chess.E4, chess.D5)
        assert game.board.piece_at(chess.D5).piece_type == chess.PAWN
        assert game.board.piece_at(chess.D5).color == chess.WHITE
        #check that it no longer still has a black pawn there
        #move the white pawn out of the way
        game.board.turn = chess.WHITE
        assert game.make_move(chess.D5, chess.D6) == True
        assert game.board.piece_at(chess.D5) == None

class TestStalemates:
    """check that the game recognizes stalemates"""
    def test_stalemate(self):
        game = SpellChessGame()
        #set up stalemate
        game.board.clear_board()
        game.board.set_piece_at(chess.H8, chess.Piece(chess.KING, chess.BLACK))
        game.board.set_piece_at(chess.F7, chess.Piece(chess.KING, chess.WHITE))
        game.board.set_piece_at(chess.G6, chess.Piece(chess.QUEEN, chess.WHITE))
        game.board.turn = chess.BLACK
        #check game end conditions
        assert game.is_game_over() == True
        outcome = game.outcome()
        assert outcome is not None
        assert outcome.winner == None
        assert outcome.termination == chess.Termination.STALEMATE

class TestCastling:
    """check that the game properly performs castling"""
    def test_castling_pawn(self):
        game = SpellChessGame()
        #move pieces out of the way
        assert game.make_move(chess.G1, chess.H3) == True
        assert game.make_move(chess.E2, chess.E4) == True
        assert game.make_move(chess.F1, chess.E2) == True
        #perform castle
        assert game.make_move(chess.E1, chess.G1) == True
        #check that pieces were moved to correct postitions and are correct color
        assert game.board.piece_at(chess.G1).piece_type == chess.KING
        assert game.board.piece_at(chess.F1).piece_type == chess.ROOK
        assert game.board.piece_at(chess.G1).color == chess.WHITE
        assert game.board.piece_at(chess.F1).color == chess.WHITE

class TestEnPassant:
    """test en passant special move"""
    def test_en_passant(self):
        game = SpellChessGame()
        #move white pawn into position
        assert game.make_move(chess.A2, chess.A4) == True
        assert game.make_move(chess.A4, chess.A5) == True #still whites turn due to change color bug
        game.board.turn = chess.BLACK #manually change color to black due to color change bug
        assert game.make_move(chess.B7, chess.B5) == True #move black pawn into position
        game.board.turn = chess.WHITE #manually change color to black due to color change bug
        assert game.make_move(chess.A5, chess.B6) == True #perfrom en passant
        #check board state
        assert game.board.piece_at(chess.B5) == None
        pawn = game.board.piece_at(chess.B6)
        assert pawn is not None
        assert pawn.piece_type == chess.PAWN
        assert pawn.color == chess.WHITE

class TestPawnPromotion:
    """test pawn promotion special move"""
    def test_pawn_promotion_queen(self):
        game = SpellChessGame()
        #move pieces out of the way
        assert game.make_move(chess.H2, chess.H4) == True
        assert game.make_move(chess.H1, chess.H3) == True
        assert game.make_move(chess.H3, chess.F3) == True
        game.board.turn = chess.BLACK
        assert game.make_move(chess.G7, chess.G5) == True
        game.board.turn = chess.WHITE
        assert game.make_move(chess.H4, chess.G5) == True
        #move black pawn to position
        game.board.turn = chess.BLACK
        assert game.make_move(chess.H7, chess.H5) == True
        assert game.make_move(chess.H5, chess.H4) == True
        assert game.make_move(chess.H4, chess.H3) == True
        assert game.make_move(chess.H3, chess.H2) == True

        assert game.make_move(chess.H2, chess.H1, promotion=chess.QUEEN) == True #perform the promotion
        piece = game.board.piece_at(chess.H1)
        assert piece is not None
        assert piece.piece_type == chess.QUEEN
        assert piece.color == chess.BLACK
        #check that pawn is no longer there
        assert game.make_move(chess.H1, chess.H2) == True
        assert game.board.piece_at(chess.H1) is None






