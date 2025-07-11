import pygame
import random
import sys
import os
import json
from datetime import datetime



# 初期化
pygame.init()

# 色の定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # I: シアン
    (255, 255, 0),  # O: 黄色
    (128, 0, 128),  # T: 紫
    (0, 255, 0),    # S: 緑
    (255, 0, 0),    # Z: 赤
    (0, 0, 255),    # J: 青
    (255, 165, 0),  # L: オレンジ
]

# ゲーム設定
TILE_SIZE = 30  # ブロック1つのサイズ（ピクセル）
FIELD_WIDTH = 10  # フィールドの幅（ブロック数）
FIELD_HEIGHT = 20  # フィールドの高さ（ブロック数）
GAME_WIDTH = FIELD_WIDTH * TILE_SIZE  # ゲーム画面の幅（ピクセル）
GAME_HEIGHT = FIELD_HEIGHT * TILE_SIZE  # ゲーム画面の高さ（ピクセル）
INFO_WIDTH = 200  # 情報表示部分の幅（ピクセル）
SCREEN_WIDTH = GAME_WIDTH + INFO_WIDTH
SCREEN_HEIGHT = GAME_HEIGHT

# ゲーム画面の設定
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

# テトリミノの形状定義
TETROMINOS = [
    # I
    [
        [[0, 0, 0, 0],
         [1, 1, 1, 1],
         [0, 0, 0, 0],
         [0, 0, 0, 0]],
        
        [[0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0]]
    ],
    # O
    [
        [[1, 1],
         [1, 1]]
    ],
    # T
    [
        [[0, 1, 0],
         [1, 1, 1],
         [0, 0, 0]],
        
        [[0, 1, 0],
         [0, 1, 1],
         [0, 1, 0]],
        
        [[0, 0, 0],
         [1, 1, 1],
         [0, 1, 0]],
        
        [[0, 1, 0],
         [1, 1, 0],
         [0, 1, 0]]
    ],
    # S
    [
        [[0, 1, 1],
         [1, 1, 0],
         [0, 0, 0]],
        
        [[0, 1, 0],
         [0, 1, 1],
         [0, 0, 1]]
    ],
    # Z
    [
        [[1, 1, 0],
         [0, 1, 1],
         [0, 0, 0]],
        
        [[0, 0, 1],
         [0, 1, 1],
         [0, 1, 0]]
    ],
    # J
    [
        [[1, 0, 0],
         [1, 1, 1],
         [0, 0, 0]],
        
        [[0, 1, 1],
         [0, 1, 0],
         [0, 1, 0]],
        
        [[0, 0, 0],
         [1, 1, 1],
         [0, 0, 1]],
        
        [[0, 1, 0],
         [0, 1, 0],
         [1, 1, 0]]
    ],
    # L
    [
        [[0, 0, 1],
         [1, 1, 1],
         [0, 0, 0]],
        
        [[0, 1, 0],
         [0, 1, 0],
         [0, 1, 1]],
        
        [[0, 0, 0],
         [1, 1, 1],
         [1, 0, 0]],
        
        [[1, 1, 0],
         [0, 1, 0],
         [0, 1, 0]]
    ]
]

class Tetris:
    def __init__(self):
        self.field = [[0 for _ in range(FIELD_WIDTH)] for _ in range(FIELD_HEIGHT)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.show_ranking = False
        self.font = pygame.font.SysFont('Arial', 24)
        self.player_name = ""
        self.name_input_active = False
        self.rankings = self.load_rankings()
        
        # 新しいテトリミノを生成
        self.new_tetromino()
        
        # キー設定
        self.key_repeat_delay = 70  # キーリピートの遅延（ミリ秒）
        self.down_key_delay = 50  # 下キーリピートの遅延（ミリ秒）
        self.key_left_pressed = 0
        self.key_right_pressed = 0
        self.key_down_pressed = 0
        
        # ゲームタイミング
        self.last_fall_time = pygame.time.get_ticks()
        self.fall_speed = 500  # 落下速度（ミリ秒）
        
        # プレビュー用の次のテトリミノ
        self.next_tetromino_type = random.randint(0, 6)
        self.next_tetromino_rotation = 0
    
    def new_tetromino(self):
        # 次のテトリミノを現在のテトリミノにセット
        if hasattr(self, 'next_tetromino_type'):
            self.tetromino_type = self.next_tetromino_type
            self.tetromino_rotation = self.next_tetromino_rotation
        else:
            # 初回のみランダム生成
            self.tetromino_type = random.randint(0, 6)
            self.tetromino_rotation = 0
        
        # 次のテトリミノを新しく生成
        self.next_tetromino_type = random.randint(0, 6)
        self.next_tetromino_rotation = 0
        
        # テトリミノの初期位置
        self.tetromino_x = FIELD_WIDTH // 2 - len(TETROMINOS[self.tetromino_type][self.tetromino_rotation][0]) // 2
        self.tetromino_y = 0
        
        # 生成時に衝突する場合はゲームオーバー
        if self.check_collision():
            self.game_over = True
    
    def rotate_tetromino(self):
        # 現在のローテーション状態を保存
        old_rotation = self.tetromino_rotation
        
        # ローテーションを次に進める
        self.tetromino_rotation = (self.tetromino_rotation + 1) % len(TETROMINOS[self.tetromino_type])
        
        # 衝突チェック
        if self.check_collision():
            # 衝突する場合は元に戻す
            self.tetromino_rotation = old_rotation
    
    def check_collision(self):
        # 現在のテトリミノの形状を取得
        tetromino = TETROMINOS[self.tetromino_type][self.tetromino_rotation]
        
        for y in range(len(tetromino)):
            for x in range(len(tetromino[y])):
                if tetromino[y][x] == 0:
                    # 空白マスは衝突チェック不要
                    continue
                
                # フィールド上の座標
                field_x = self.tetromino_x + x
                field_y = self.tetromino_y + y
                
                # フィールド外への衝突チェック
                if field_x < 0 or field_x >= FIELD_WIDTH or field_y >= FIELD_HEIGHT:
                    return True
                
                # 他のブロックとの衝突チェック (床より上の場合のみ)
                if field_y >= 0 and self.field[field_y][field_x] != 0:
                    return True
        
        return False
    
    def lock_tetromino(self):
        # 現在のテトリミノをフィールドに固定
        tetromino = TETROMINOS[self.tetromino_type][self.tetromino_rotation]
        
        for y in range(len(tetromino)):
            for x in range(len(tetromino[y])):
                if tetromino[y][x] == 0:
                    continue
                
                field_y = self.tetromino_y + y
                field_x = self.tetromino_x + x
                
                # フィールド内に収まる場合のみ設定
                if 0 <= field_y < FIELD_HEIGHT and 0 <= field_x < FIELD_WIDTH:
                    self.field[field_y][field_x] = self.tetromino_type + 1
    
    def clear_lines(self):
        # 消去する行をカウント
        lines_to_clear = 0
        
        for y in range(FIELD_HEIGHT):
            # 行が全て埋まっているかチェック
            if all(self.field[y]):
                lines_to_clear += 1
                
                # 上の行を下に移動
                for y2 in range(y, 0, -1):
                    self.field[y2] = self.field[y2 - 1][:]
                
                # 最上段を空にする
                self.field[0] = [0 for _ in range(FIELD_WIDTH)]
        
        # スコア計算
        if lines_to_clear > 0:
            self.lines_cleared += lines_to_clear
            self.score += [0, 100, 300, 500, 800][lines_to_clear] * self.level
            
            # レベルアップ判定
            self.level = min(10, 1 + self.lines_cleared // 10)
            
            # 速度調整（レベルが上がると速くなる）
            self.fall_speed = max(100, 500 - (self.level - 1) * 40)
    
    def move(self, dx, dy):
        # 移動前の位置を保存
        old_x = self.tetromino_x
        old_y = self.tetromino_y
        
        # 移動
        self.tetromino_x += dx
        self.tetromino_y += dy
        
        # 衝突チェック
        if self.check_collision():
            # 衝突した場合は元の位置に戻す
            self.tetromino_x = old_x
            self.tetromino_y = old_y
            
            # 下方向への移動で衝突した場合は固定処理
            if dy > 0:
                self.lock_tetromino()
                self.clear_lines()
                self.new_tetromino()
                
            return False
        
        return True
    
    def hard_drop(self):
        # テトリミノを一気に落下させる
        while self.move(0, 1):
            pass
    
    def update(self):
        if self.game_over or self.paused:
            return
        
        # キーリピート処理
        current_time = pygame.time.get_ticks()
        
        # 左移動
        if self.key_left_pressed and current_time - self.key_left_pressed > self.key_repeat_delay:
            self.move(-1, 0)
            self.key_left_pressed = current_time
        
        # 右移動
        if self.key_right_pressed and current_time - self.key_right_pressed > self.key_repeat_delay:
            self.move(1, 0)
            self.key_right_pressed = current_time
        
        # 下移動
        if self.key_down_pressed and current_time - self.key_down_pressed > self.down_key_delay:
            self.move(0, 1)
            self.key_down_pressed = current_time
        
        # 自然落下
        if current_time - self.last_fall_time > self.fall_speed:
            self.move(0, 1)
            self.last_fall_time = current_time
    
    def reset(self):
        # ランキングを保持しつつゲームをリセットする
        rankings = self.rankings
        self.__init__()
        self.rankings = rankings
        
    def load_rankings(self):
        # ランキングをファイルから読み込む
        rankings_file = "tetris_rankings.json"
        if os.path.exists(rankings_file):
            try:
                with open(rankings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_rankings(self):
        # ランキングをファイルに保存
        rankings_file = "tetris_rankings.json"
        with open(rankings_file, "w", encoding="utf-8") as f:
            json.dump(self.rankings, f, ensure_ascii=False)
    
    def add_to_rankings(self, name):
        # スコアをランキングに追加
        today = datetime.now().strftime("%Y/%m/%d")
        new_record = {
            "name": name,
            "score": self.score,
            "lines": self.lines_cleared,
            "level": self.level,
            "date": today
        }
        
        # ランキングに追加して降順でソート
        self.rankings.append(new_record)
        self.rankings = sorted(self.rankings, key=lambda x: x["score"], reverse=True)
        
        # 最大10件まで保存
        if len(self.rankings) > 10:
            self.rankings = self.rankings[:10]
        
        # ランキングを保存
        self.save_rankings()
        
        # ランキング表示に切り替え
        self.show_ranking = True
    
    def draw(self):
        # 背景を黒で塗りつぶす
        screen.fill(BLACK)
        
        # ランキング表示画面
        if self.show_ranking:
            self.draw_rankings()
            return
            
        # 名前入力画面
        if self.name_input_active:
            self.draw_name_input()
            return
        
        # フィールドの枠線
        pygame.draw.rect(screen, WHITE, (0, 0, GAME_WIDTH, GAME_HEIGHT), 1)
        
        # フィールド内のブロックを描画
        for y in range(FIELD_HEIGHT):
            for x in range(FIELD_WIDTH):
                if self.field[y][x] != 0:
                    # ブロックの色を取得
                    color_index = self.field[y][x] - 1
                    color = COLORS[color_index]
                    
                    # ブロックを描画
                    pygame.draw.rect(
                        screen, 
                        color, 
                        (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    )
                    pygame.draw.rect(
                        screen, 
                        WHITE, 
                        (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 
                        1
                    )
        
        # 現在落下中のテトリミノを描画
        if not self.game_over:
            tetromino = TETROMINOS[self.tetromino_type][self.tetromino_rotation]
            for y in range(len(tetromino)):
                for x in range(len(tetromino[y])):
                    if tetromino[y][x] != 0:
                        # 画面内のブロックのみ描画
                        field_x = self.tetromino_x + x
                        field_y = self.tetromino_y + y
                        
                        if field_y >= 0:  # 画面上部の見えない部分は描画しない
                            pygame.draw.rect(
                                screen, 
                                COLORS[self.tetromino_type], 
                                (field_x * TILE_SIZE, field_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                            )
                            pygame.draw.rect(
                                screen, 
                                WHITE, 
                                (field_x * TILE_SIZE, field_y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 
                                1
                            )
        
        # 情報表示エリア
        info_area = pygame.Rect(GAME_WIDTH, 0, INFO_WIDTH, GAME_HEIGHT)
        pygame.draw.rect(screen, BLACK, info_area)
        pygame.draw.rect(screen, WHITE, info_area, 1)
        
        # スコア表示
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (GAME_WIDTH + 10, 10))
        
        # レベル表示
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        screen.blit(level_text, (GAME_WIDTH + 10, 50))
        
        # 消去ライン数表示
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        screen.blit(lines_text, (GAME_WIDTH + 10, 90))
        
        # 次のテトリミノのプレビュー
        next_text = self.font.render("Next:", True, WHITE)
        screen.blit(next_text, (GAME_WIDTH + 10, 150))
        
        # 次のテトリミノを描画
        next_tetromino = TETROMINOS[self.next_tetromino_type][self.next_tetromino_rotation]
        
        # プレビューの位置調整（中央に表示）
        preview_size = TILE_SIZE * 0.8  # 少し小さめに表示
        preview_width = len(next_tetromino[0]) * preview_size
        preview_height = len(next_tetromino) * preview_size
        preview_x = GAME_WIDTH + (INFO_WIDTH - preview_width) // 2
        preview_y = 190
        
        for y in range(len(next_tetromino)):
            for x in range(len(next_tetromino[y])):
                if next_tetromino[y][x] != 0:
                    pygame.draw.rect(
                        screen, 
                        COLORS[self.next_tetromino_type], 
                        (preview_x + x * preview_size, preview_y + y * preview_size, 
                         preview_size, preview_size)
                    )
                    pygame.draw.rect(
                        screen, 
                        WHITE, 
                        (preview_x + x * preview_size, preview_y + y * preview_size, 
                         preview_size, preview_size), 
                        1
                    )
        
        # ランキングボタン
        rank_button = pygame.Rect(GAME_WIDTH + 20, SCREEN_HEIGHT - 80, INFO_WIDTH - 40, 30)
        pygame.draw.rect(screen, GRAY, rank_button)
        pygame.draw.rect(screen, WHITE, rank_button, 1)
        rank_text = self.font.render("Ranking", True, WHITE)
        rank_text_x = GAME_WIDTH + 20 + (INFO_WIDTH - 40 - rank_text.get_width()) // 2
        rank_text_y = SCREEN_HEIGHT - 80 + (30 - rank_text.get_height()) // 2
        screen.blit(rank_text, (rank_text_x, rank_text_y))
        
        # ゲームオーバー表示
        if self.game_over:
            # 半透明の黒いオーバーレイ
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            # ゲームオーバーテキスト
            game_over_font = pygame.font.SysFont('Arial', 48)
            game_over_text = game_over_font.render("GAME OVER", True, WHITE)
            
            # 画面中央に表示
            text_x = (SCREEN_WIDTH - game_over_text.get_width()) // 2
            text_y = (SCREEN_HEIGHT - game_over_text.get_height()) // 2 - 50
            screen.blit(game_over_text, (text_x, text_y))
            
            # スコア表示
            final_score_font = pygame.font.SysFont('Arial', 36)
            final_score_text = final_score_font.render(f"Score: {self.score}", True, WHITE)
            score_x = (SCREEN_WIDTH - final_score_text.get_width()) // 2
            score_y = text_y + game_over_text.get_height() + 10
            screen.blit(final_score_text, (score_x, score_y))
            
            # 名前入力案内
            name_font = pygame.font.SysFont('Arial', 24)
            name_text = name_font.render("Enter your name for ranking", True, WHITE)
            name_x = (SCREEN_WIDTH - name_text.get_width()) // 2
            name_y = score_y + final_score_text.get_height() + 20
            screen.blit(name_text, (name_x, name_y))
            
            # 名前入力ボタン
            input_button = pygame.Rect((SCREEN_WIDTH - 200) // 2, name_y + name_text.get_height() + 10, 200, 40)
            pygame.draw.rect(screen, GRAY, input_button)
            pygame.draw.rect(screen, WHITE, input_button, 1)
            input_text = self.font.render("Enter Name", True, WHITE)
            input_x = (SCREEN_WIDTH - input_text.get_width()) // 2
            input_y = input_button.y + (input_button.height - input_text.get_height()) // 2
            screen.blit(input_text, (input_x, input_y))
            
            # リトライボタン
            retry_button = pygame.Rect((SCREEN_WIDTH - 200) // 2, input_button.y + input_button.height + 20, 200, 40)
            pygame.draw.rect(screen, GRAY, retry_button)
            pygame.draw.rect(screen, WHITE, retry_button, 1)
            retry_text = self.font.render("Retry Without Saving", True, WHITE)
            retry_x = (SCREEN_WIDTH - retry_text.get_width()) // 2
            retry_y = retry_button.y + (retry_button.height - retry_text.get_height()) // 2
            screen.blit(retry_text, (retry_x, retry_y))
        
        # 一時停止表示
        if self.paused:
            # 半透明の黒いオーバーレイ
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            # 一時停止テキスト
            pause_font = pygame.font.SysFont('Arial', 48)
            pause_text = pause_font.render("PAUSED", True, WHITE)
            
            # 画面中央に表示
            text_x = (SCREEN_WIDTH - pause_text.get_width()) // 2
            text_y = (SCREEN_HEIGHT - pause_text.get_height()) // 2
            screen.blit(pause_text, (text_x, text_y))
    
    def draw_name_input(self):
        # 名前入力画面を描画
        screen.fill(BLACK)
        
        # タイトル
        title_font = pygame.font.SysFont('Arial', 36)
        title_text = title_font.render("Enter Your Name", True, WHITE)
        title_x = (SCREEN_WIDTH - title_text.get_width()) // 2
        title_y = 100
        screen.blit(title_text, (title_x, title_y))
        
        # 名前入力フィールド
        input_rect = pygame.Rect((SCREEN_WIDTH - 300) // 2, 180, 300, 40)
        pygame.draw.rect(screen, GRAY, input_rect)
        pygame.draw.rect(screen, WHITE, input_rect, 2)
        
        # 入力中の名前表示
        name_text = self.font.render(self.player_name, True, WHITE)
        name_x = input_rect.x + 10
        name_y = input_rect.y + (input_rect.height - name_text.get_height()) // 2
        screen.blit(name_text, (name_x, name_y))
        
        # カーソル点滅（0.5秒ごと）
        if pygame.time.get_ticks() % 1000 < 500:
            cursor_x = name_x + name_text.get_width() + 2
            pygame.draw.line(screen, WHITE, (cursor_x, name_y), (cursor_x, name_y + name_text.get_height()), 2)
        
        # 決定ボタン
        submit_rect = pygame.Rect((SCREEN_WIDTH - 200) // 2, 260, 200, 40)
        pygame.draw.rect(screen, GRAY, submit_rect)
        pygame.draw.rect(screen, WHITE, submit_rect, 1)
        submit_text = self.font.render("Submit", True, WHITE)
        submit_x = submit_rect.x + (submit_rect.width - submit_text.get_width()) // 2
        submit_y = submit_rect.y + (submit_rect.height - submit_text.get_height()) // 2
        screen.blit(submit_text, (submit_x, submit_y))
        
        # 説明
        info_font = pygame.font.SysFont('Arial', 18)
        info_text = info_font.render("Press ENTER to submit or ESC to cancel", True, WHITE)
        info_x = (SCREEN_WIDTH - info_text.get_width()) // 2
        info_y = 320
        screen.blit(info_text, (info_x, info_y))
    
    def draw_rankings(self):
        # ランキング画面の描画
        screen.fill(BLACK)
        
        # タイトル
        title_font = pygame.font.SysFont('Arial', 36)
        title_text = title_font.render("Tetris Ranking", True, WHITE)
        title_x = (SCREEN_WIDTH - title_text.get_width()) // 2
        title_y = 30
        screen.blit(title_text, (title_x, title_y))
        
        # ヘッダー
        header_y = 90
        header_font = pygame.font.SysFont('Arial', 20)
        
        rank_text = header_font.render("Rank", True, WHITE)
        screen.blit(rank_text, (50, header_y))
        
        name_text = header_font.render("Name", True, WHITE)
        screen.blit(name_text, (120, header_y))
        
        score_text = header_font.render("Score", True, WHITE)
        screen.blit(score_text, (250, header_y))
        
        level_text = header_font.render("Level", True, WHITE)
        screen.blit(level_text, (350, header_y))
        
        lines_text = header_font.render("Lines", True, WHITE)
        screen.blit(lines_text, (420, header_y))
        
        date_text = header_font.render("Date", True, WHITE)
        screen.blit(date_text, (490, header_y))
        
        # 区切り線
        pygame.draw.line(screen, WHITE, (30, header_y + 30), (SCREEN_WIDTH - 30, header_y + 30), 1)
        
        # ランキングデータ
        if not self.rankings:
            no_data_text = self.font.render("No Records Yet", True, WHITE)
            no_data_x = (SCREEN_WIDTH - no_data_text.get_width()) // 2
            no_data_y = header_y + 70
            screen.blit(no_data_text, (no_data_x, no_data_y))
        else:
            data_y = header_y + 50
            for i, record in enumerate(self.rankings):
                # 順位
                rank_text = self.font.render(f"{i + 1}", True, WHITE)
                screen.blit(rank_text, (50, data_y))
                
                # 名前
                name_text = self.font.render(record["name"], True, WHITE)
                screen.blit(name_text, (120, data_y))
                
                # スコア
                score_text = self.font.render(f"{record['score']}", True, WHITE)
                screen.blit(score_text, (250, data_y))
                
                # レベル
                level_text = self.font.render(f"{record['level']}", True, WHITE)
                screen.blit(level_text, (350, data_y))
                
                # ライン数
                lines_text = self.font.render(f"{record['lines']}", True, WHITE)
                screen.blit(lines_text, (420, data_y))
                
                # 日付
                date_text = self.font.render(f"{record['date']}", True, WHITE)
                screen.blit(date_text, (490, data_y))
                
                data_y += 30
        
        # 戻るボタン
        back_rect = pygame.Rect((SCREEN_WIDTH - 200) // 2, SCREEN_HEIGHT - 80, 200, 40)
        pygame.draw.rect(screen, GRAY, back_rect)
        pygame.draw.rect(screen, WHITE, back_rect, 1)
        back_text = self.font.render("Back to Game", True, WHITE)
        back_x = back_rect.x + (back_rect.width - back_text.get_width()) // 2
        back_y = back_rect.y + (back_rect.height - back_text.get_height()) // 2
        screen.blit(back_text, (back_x, back_y))

# メインゲームループ
def main():
    clock = pygame.time.Clock()
    game = Tetris()
    
    # 操作説明
    print("=== テトリス操作方法 ===")
    print("左矢印キー: 左に移動")
    print("右矢印キー: 右に移動")
    print("下矢印キー: 下に移動（ソフトドロップ）")
    print("上矢印キー: 回転")
    print("スペース: ハードドロップ（一気に落下）")
    print("P: 一時停止/再開")
    print("R: ランキング表示")
    print("ESC: 終了")
    
    while True:
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # マウスクリックイベント
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左クリック
                mouse_pos = pygame.mouse.get_pos()
                
                # ランキング画面
                if game.show_ranking:
                    # 戻るボタン
                    back_rect = pygame.Rect((SCREEN_WIDTH - 200) // 2, SCREEN_HEIGHT - 80, 200, 40)
                    if back_rect.collidepoint(mouse_pos):
                        game.show_ranking = False
                
                # 名前入力画面
                elif game.name_input_active:
                    # 決定ボタン
                    submit_rect = pygame.Rect((SCREEN_WIDTH - 200) // 2, 260, 200, 40)
                    if submit_rect.collidepoint(mouse_pos):
                        if game.player_name:  # 名前が入力されている場合
                            game.add_to_rankings(game.player_name)
                            game.name_input_active = False
                
                # ゲームオーバー画面
                elif game.game_over:
                    # 名前入力ボタン
                    input_button = pygame.Rect((SCREEN_WIDTH - 200) // 2, 
                                            (SCREEN_HEIGHT - 50) // 2 + 40, 200, 40)
                    if input_button.collidepoint(mouse_pos):
                        game.name_input_active = True
                    
                    # リトライボタン
                    retry_button = pygame.Rect((SCREEN_WIDTH - 200) // 2, 
                                            input_button.y + input_button.height + 20, 200, 40)
                    if retry_button.collidepoint(mouse_pos):
                        game.reset()
                
                # 通常画面
                else:
                    # ランキングボタン
                    rank_button = pygame.Rect(GAME_WIDTH + 20, SCREEN_HEIGHT - 80, INFO_WIDTH - 40, 30)
                    if rank_button.collidepoint(mouse_pos):
                        game.show_ranking = True
            
            elif event.type == pygame.KEYDOWN:
                # 名前入力画面
                if game.name_input_active:
                    if event.key == pygame.K_RETURN:  # Enter
                        if game.player_name:  # 名前が入力されている場合
                            game.add_to_rankings(game.player_name)
                            game.name_input_active = False
                    
                    elif event.key == pygame.K_ESCAPE:  # ESC
                        game.name_input_active = False
                    
                    elif event.key == pygame.K_BACKSPACE:  # バックスペース
                        game.player_name = game.player_name[:-1]
                    
                    else:
                        # 20文字以内で入力制限
                        if len(game.player_name) < 20 and event.unicode.isprintable():
                            game.player_name += event.unicode
                
                # ランキング画面
                elif game.show_ranking:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        game.show_ranking = False
                
                # 通常画面
                else:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    
                    if game.game_over:
                        if event.key == pygame.K_r:
                            game.reset()
                    
                    elif event.key == pygame.K_p:
                        game.paused = not game.paused
                    
                    elif event.key == pygame.K_r:
                        game.show_ranking = True
                    
                    elif not game.paused:
                        if event.key == pygame.K_LEFT:
                            game.move(-1, 0)
                            game.key_left_pressed = pygame.time.get_ticks()
                        
                        elif event.key == pygame.K_RIGHT:
                            game.move(1, 0)
                            game.key_right_pressed = pygame.time.get_ticks()
                        
                        elif event.key == pygame.K_DOWN:
                            game.move(0, 1)
                            game.key_down_pressed = pygame.time.get_ticks()
                        
                        elif event.key == pygame.K_UP:
                            game.rotate_tetromino()
                        
                        elif event.key == pygame.K_SPACE:
                            game.hard_drop()
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    game.key_left_pressed = 0
                elif event.key == pygame.K_RIGHT:
                    game.key_right_pressed = 0
                elif event.key == pygame.K_DOWN:
                    game.key_down_pressed = 0
        
        # ゲーム状態の更新（名前入力中とランキング表示中は更新しない）
        if not game.name_input_active and not game.show_ranking:
            game.update()
        
        # 描画
        game.draw()
        pygame.display.flip()
        
        # フレームレート
        clock.tick(60)

if __name__ == "__main__":
    main()