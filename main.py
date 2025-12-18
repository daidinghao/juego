import tkinter as tk
import random  
import time
from collections import deque  
from tkinter import messagebox

# 棋盘大小 (Max 20x20)
Fila = 10
Columna = 10
NumMina = 10

DIRS = [(-1,-1), (-1,0), (-1,1),
        ( 0,-1),         ( 0,1),
        ( 1,-1), ( 1,0), ( 1,1)]


class JuegoBuscaMina:

    # ----------------- 创建看板 -----------------
    def Crear_Junta(self, Fila, Columna):
        return [[0 for _ in range(Columna)] for _ in range(Fila)]

    # ----------------- 绑定左右键 -----------------
    def bind_button(self, boton, fila, columna):
        boton.bind("<Button-1>", lambda e: self.cuando_click(fila, columna))
        boton.bind("<Button-3>", lambda e: self.on_right_click(fila, columna))
    
    # ----------------- 查找临近地雷数量 -----------------
    def contar_minas_vecinas(self, Junta, fila, columna):
        contador = 0
        for df, dc in DIRS:
            nf, nc = fila + df, columna + dc
            if 0 <= nf < Fila and 0 <= nc < Columna and Junta[nf][nc] == -1:
                contador += 1
        return contador

    # ----------------- 确认是否存在雷 -----------------
    def Confirmar_exista(self, Junta):
        for fila in range(Fila):
            for columna in range(Columna):
                if Junta[fila][columna] == -1:
                    continue
                Junta[fila][columna] = self.contar_minas_vecinas(Junta, fila, columna)

    # ----------------- 构造函数 -----------------
    def __init__(self, master):
        self.master = master
        master.title("BuscaMina")

        # 顶部信息栏
        self.top_frame = tk.Frame(master, height=40)
        self.top_frame.grid(row=0, column=0, columnspan=Columna, sticky="we")

        # 时间显示
        self.time_label = tk.Label(
            self.top_frame, text="Time: 0", font=("Arial", 12)
        )
        self.time_label.pack(side="left", padx=10)

        # 雷数显示
        self.mine_label = tk.Label(
            self.top_frame, text=f"Mines: {NumMina}", font=("Arial", 12)
        )
        self.mine_label.pack(side="right", padx=10)

        # 创建空地图
        self.junta = self.Crear_Junta(Fila, Columna)
        
        # 计时相关
        self.start_time = None
        self.timer_running = False
        self.elapsed_time = 0
        
        # 插旗计数
        self.flag_count = NumMina
        # 游戏是否结束
        self.game_over = False  

        # 标记：是否是第一次点击
        self.primer_click = True

        # 记录每个格子是否已经被翻开
        self.visible = [[False for _ in range(Columna)] for _ in range(Fila)]

        # 哪些格子被插了旗
        self.flags = [[False for _ in range(Columna)] for _ in range(Fila)]

        # 记录玩家翻开的格子数（不包括雷）
        self.contador_descubiertos = 0

        # 用来保存按钮对象的二维列表
        self.botones = [[None for _ in range(Columna)] for _ in range(Fila)]

        # 创建按钮并绑定左右键
        for f in range(Fila):
            for c in range(Columna):
                b = tk.Button(master, width=3, height=1)
                self.bind_button(b, f, c)
                b.grid(row=f+1, column=c, padx=1, pady=1)
                self.botones[f][c] = b
  
    # ----------------- 生成 -----------------
    def generar_tablero_en_primer_click(self, fila, columna):
            """
            玩家第一次点击时才生成雷+数字。
            保证第一次点击的格子（以及优先它的邻居）尽量不被放雷，从而保证被点击格为 0（或尽可能为 0）。
            如果严格排除邻居导致可选格不足，会退化为仅排除中心格。
            使用多次尝试以尽量确保中心为 0。
            """
            # 所有格子
            all_cells = [(f, c) for f in range(Fila) for c in range(Columna)]

            # 构造禁止放雷集合：包含点击格及其 8 邻域
            forbidden = set()
            for df, dc in DIRS + [(0, 0)]:
                nf, nc = fila + df, columna + dc
                if 0 <= nf < Fila and 0 <= nc < Columna:
                    forbidden.add((nf, nc))

            # 首选从排除了邻居的集合中放雷
            candidates = [cell for cell in all_cells if cell not in forbidden]

            # 如果可选位置太少（NumMina 太多），回退到只排除中心格
            if len(candidates) < NumMina:
                candidates = [cell for cell in all_cells if cell != (fila, columna)]

            # 生成板并尝试多次直到保证中心为 0（最多尝试 100 次）
            for attempt in range(100):
                # 重新创建空板
                tablero = self.Crear_Junta(Fila, Columna)
                # 随机选雷位
                minas = random.sample(candidates, NumMina)
                for (mf, mc) in minas:
                    tablero[mf][mc] = -1
                # 计算数字
                self.Confirmar_exista(tablero)
                # 如果点击格为 0，接收这个棋盘
                if tablero[fila][columna] == 0:
                    self.junta = tablero
                    return
            # 如果尝试多次仍不能（极少发生），退而求其次：确保点击格不是雷
            tablero = self.Crear_Junta(Fila, Columna)
            minas = random.sample([cell for cell in all_cells if cell != (fila, columna)], NumMina)
            for (mf, mc) in minas:
                tablero[mf][mc] = -1
            self.Confirmar_exista(tablero)
            self.junta = tablero
    
    # ----------------- UI 视觉更新 -----------------
    def mostrar_casilla(self, fila, columna):
        
        btn = self.botones[fila][columna]
        valor = self.junta[fila][columna]

        # 显示数字或空白
        if valor == 0:
            btn.config(text="")
        else:
            btn.config(text=str(valor))

        # 视觉效果（变成凹下去）
        btn.config(state="disabled",relief="sunken")

        # 禁用右键插旗
        btn.unbind("<Button-3>")

    # ----------------- 定时更新 UI -----------------
    def update_timer(self):
        if not self.timer_running:
            return

        self.elapsed_time = int(time.time() - self.start_time)
        self.time_label.config(text=f"Time: {self.elapsed_time}")

        # 每 1000ms 更新一次
        self.master.after(1000, self.update_timer)
    
    # ----------------- 更新雷数显示 -----------------
    def update_mine_label(self):
        self.mine_label.config(text=f"Mines: {self.flag_count}")

    # ----------------- 右键：插旗/取消插旗 -----------------
    def on_right_click(self, fila, columna):
        # 已经翻开的格子不能插旗
        if self.visible[fila][columna]:
            return "break"  # 阻止默认右键其它行为

        if not self.flags[fila][columna]:
            # 插旗
            self.flags[fila][columna] = True
            self.botones[fila][columna].config(text="F", fg="blue")
            if self.flag_count > 1:
                self.flag_count -= 1
        else:
            # 取消旗
            self.flags[fila][columna] = False
            self.botones[fila][columna].config(text="", fg="black")
            if self.flag_count < 10:
                self.flag_count += 1
        self.update_mine_label()

    # ----------------- 左键点击主逻辑 -----------------
    def cuando_click(self, fila, columna):
        if self.game_over:
            return

        # 如果已经翻开过，则可能进行 chord（连动）操作
        if self.visible[fila][columna]:
            valor = self.junta[fila][columna]
            if valor > 0:
                self.chord(fila, columna)
            return

        # 首次点击：生成地图并直接展开（尽量保证中心为0）
        if self.primer_click:
            self.primer_click = False
            
            # 启动计时
            self.start_time = time.time()
            self.timer_running = True
            self.update_timer()

            self.generar_tablero_en_primer_click(fila, columna)
            nuevas = self.revelar_zona(fila, columna)
            if nuevas > 0:
                self.verificar_victoria()
            return

        # 非首次点击且未翻开的普通点击
        # 如果被插旗则忽略左键（需要先取消旗）
        if self.flags[fila][columna]:
            return

        valor = self.junta[fila][columna]
        # 踩雷：显示所有雷并结束
        if valor == -1:
            self.finalizar_juego(False)
            self.botones[fila][columna].config(text="X", bg="red")
            messagebox.showinfo("Game Over", "BOOM! 你踩到雷了。")
            return

        # 若为数字且 > 0，只显示自己
        if valor > 0:
            self.visible[fila][columna] = True
            self.contador_descubiertos += 1
            self.mostrar_casilla(fila, columna)
            self.verificar_victoria()
            return

        # 若为 0，则展开
        nuevas = self.revelar_zona(fila, columna)
        if nuevas > 0:
            self.verificar_victoria()

    # ----------------- 展开区域（BFS） -----------------
    def revelar_zona(self, fila_inicial, columna_inicial):
        """
        BFS 展开：从 (fila_inicial, columna_inicial) 开始，展开连续的 0 区域，并显示边缘数字。
        """

        if self.flags[fila_inicial][columna_inicial] or self.game_over:
            return 0

        filas = Fila
        columnas = Columna
        cola = deque()
        nuevas_abiertas = 0

        cola.append((fila_inicial, columna_inicial))
        
        if not self.visible[fila_inicial][columna_inicial]:
            self.visible[fila_inicial][columna_inicial] = True
            self.contador_descubiertos += 1
            nuevas_abiertas += 1
            self.mostrar_casilla(fila_inicial, columna_inicial)

        while cola:
            f, c = cola.popleft()
            valor = self.junta[f][c]

            self.mostrar_casilla(f, c)

            if valor != 0:
                continue

            # 扩散到周围未被翻开的格子（跳过地雷）
            for df, dc in DIRS:
                nf, nc = f + df, c + dc
                if 0 <= nf < filas and 0 <= nc < columnas:
                    if self.visible[nf][nc] or self.flags[nf][nc]:
                        continue
                    if self.junta[nf][nc] == -1:
                        continue
                    # 标记并计数，再加入队列
                    self.visible[nf][nc] = True
                    self.contador_descubiertos += 1
                    nuevas_abiertas += 1
                    cola.append((nf, nc))
        
        return nuevas_abiertas
 
    # ----------------- 数字点击 -----------------
    def chord(self, fila, columna):
        """
        扫雷双击功能：
        若周围旗子数 == 数字，则自动翻开其它未标记格子。
        若未标记的格子中有雷，则失败。
        """
        valor = self.junta[fila][columna]
        if self.game_over:
            return

        valor = self.junta[fila][columna]

        if valor <= 0 or not self.visible[fila][columna]:
            return

        vecinos = []
        flag_count = 0

        # 统计周围格子 + 旗子数量
        for df, dc in DIRS:
            nf, nc = fila + df, columna + dc
            if 0 <= nf < Fila and 0 <= nc < Columna:
                vecinos.append((nf, nc))
                if self.flags[nf][nc]:
                    flag_count += 1
                
        # 条件不满足 → 不双击
        if flag_count != valor:
            return
        
        total_nuevas = 0
        # 条件满足 → 展开未标记的邻居
        for nf, nc in vecinos:
            # 跳过旗子、已翻开格
            if self.flags[nf][nc] or self.visible[nf][nc]:
                continue

            # 未标记的格子里如果有雷 = 失败
            if self.junta[nf][nc] == -1:
                self.finalizar_juego(False)
                self.botones[nf][nc].config(text="X", bg="red")
                messagebox.showinfo("Game Over", "BOOM! 标记错误，触发了地雷。")
                return

            nuevas = self.revelar_zona(nf, nc)
            total_nuevas += nuevas

        if total_nuevas > 0:
            self.verificar_victoria()

    # ----------------- 胜利检测 -----------------
    def verificar_victoria(self):

        if self.game_over:
            return

        total_seguras = Fila * Columna - NumMina
        if self.contador_descubiertos == total_seguras:
            self.finalizar_juego(True)
            messagebox.showinfo("Game Over", "¡Victoria! 你赢了。")

    # ----------------- 游戏结束 -----------------
    def finalizar_juego(self, gano):
        if self.game_over:
            return
        
        self.game_over = True
        self.timer_running = False

        for f in range(Fila):
            for c in range(Columna):
                btn = self.botones[f][c]
                # 锁定所有按钮
                btn.config(state="disabled")
                if not self.visible[f][c]:
                    # 失败：显示所有雷
                    if not gano and self.junta[f][c] == -1 and not self.visible[f][c]:
                        btn.config(text="X", bg="red", relief="sunken")
                
if __name__ == "__main__":
    root = tk.Tk()
    app = JuegoBuscaMina(root)
    root.resizable(False, False)  # 不允许拉伸窗口
    root.mainloop()

