export declare const WHITE = "w";
export declare const BLACK = "b";
export declare const PAWN = "p";
export declare const KNIGHT = "n";
export declare const BISHOP = "b";
export declare const ROOK = "r";
export declare const QUEEN = "q";
export declare const KING = "k";
export declare type Color = 'w' | 'b';
export declare type PieceSymbol = 'p' | 'n' | 'b' | 'r' | 'q' | 'k';
export declare type Square = 'a8' | 'b8' | 'c8' | 'd8' | 'e8' | 'f8' | 'g8' | 'h8' | 'a7' | 'b7' | 'c7' | 'd7' | 'e7' | 'f7' | 'g7' | 'h7' | 'a6' | 'b6' | 'c6' | 'd6' | 'e6' | 'f6' | 'g6' | 'h6' | 'a5' | 'b5' | 'c5' | 'd5' | 'e5' | 'f5' | 'g5' | 'h5' | 'a4' | 'b4' | 'c4' | 'd4' | 'e4' | 'f4' | 'g4' | 'h4' | 'a3' | 'b3' | 'c3' | 'd3' | 'e3' | 'f3' | 'g3' | 'h3' | 'a2' | 'b2' | 'c2' | 'd2' | 'e2' | 'f2' | 'g2' | 'h2' | 'a1' | 'b1' | 'c1' | 'd1' | 'e1' | 'f1' | 'g1' | 'h1';
export declare const DEFAULT_POSITION = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
export declare type Piece = {
    color: Color;
    type: PieceSymbol;
};
declare type InternalMove = {
    color: Color;
    from: number;
    to: number;
    piece: PieceSymbol;
    captured?: PieceSymbol;
    promotion?: PieceSymbol;
    flags: number;
};
export declare type Move = {
    color: Color;
    from: string;
    to: string;
    piece: PieceSymbol;
    captured?: PieceSymbol;
    promotion?: PieceSymbol;
    flags: string;
    san: string;
};
export declare const SQUARES: Square[];
export declare function validateFen(fen: string): {
    valid: boolean;
    errorNumber: number;
    error: string;
};
export declare class Chess {
    private _board;
    private _turn;
    private _header;
    private _kings;
    private _epSquare;
    private _halfMoves;
    private _moveNumber;
    private _history;
    private _comments;
    private _castling;
    constructor(fen?: string);
    clear(keepHeaders?: boolean): void;
    load(fen: string, keepHeaders?: boolean): boolean;
    fen(): string;
    private _updateSetup;
    reset(): void;
    get(square: Square): Piece;
    put({ type, color }: {
        type: PieceSymbol;
        color: Color;
    }, square: Square): boolean;
    remove(square: Square): Piece;
    _attacked(color: Color, square: number): boolean;
    private _isKingAttacked;
    isCheck(): boolean;
    inCheck(): boolean;
    isCheckmate(): boolean;
    isStalemate(): boolean;
    isInsufficientMaterial(): boolean;
    isThreefoldRepetition(): boolean;
    isDraw(): boolean;
    isGameOver(): boolean;
    moves({ verbose, square, }?: {
        verbose?: boolean;
        square?: Square;
    }): string[] | Move[];
    _moves({ legal, piece, square, }?: {
        legal?: boolean;
        piece?: PieceSymbol;
        square?: Square;
    }): InternalMove[];
    move(move: string | {
        from: string;
        to: string;
        promotion?: string;
    }, { sloppy }?: {
        sloppy?: boolean;
    }): Move | null;
    _push(move: InternalMove): void;
    private _makeMove;
    undo(): Move | null;
    private _undoMove;
    pgn({ newline, maxWidth, }?: {
        newline?: string;
        maxWidth?: number;
    }): string;
    header(...args: string[]): Record<string, string>;
    loadPgn(pgn: string, { sloppy, newlineChar, }?: {
        sloppy?: boolean;
        newlineChar?: string;
    }): boolean;
    private _moveToSan;
    private _moveFromSan;
    ascii(): string;
    perft(depth: number): number;
    private _makePretty;
    turn(): Color;
    board(): ({
        square: Square;
        type: PieceSymbol;
        color: Color;
    } | null)[][];
    squareColor(square: Square): "light" | "dark" | null;
    history({ verbose }?: {
        verbose?: boolean;
    }): (string | Move)[];
    private _pruneComments;
    getComment(): string;
    setComment(comment: string): void;
    deleteComment(): string;
    getComments(): {
        fen: string;
        comment: string;
    }[];
    deleteComments(): {
        fen: string;
        comment: string;
    }[];
}
export {};
