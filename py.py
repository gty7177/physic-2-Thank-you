import math
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PhysicsSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("물리학 II: 공기 저항 포물선 및 에너지 시뮬레이터")
        
        # 입력 변수 기본값
        self.g = 9.8       # 중력 가속도
        self.dt = 0.01     # 시간 간격 (오일러 메서드)
        
        # UI 레이아웃 설정
        control_frame = ttk.Frame(root, padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # 입력 슬라이더 생성
        self.v0_var = self.create_slider(control_frame, "초기 속도 (m/s):", 5, 50, 20, 0)
        self.angle_var = self.create_slider(control_frame, "발사 각도 (도):", 10, 80, 45, 1)
        self.mass_var = self.create_slider(control_frame, "물체 질량 (kg):", 0.1, 5.0, 1.0, 2)
        self.drag_var = self.create_slider(control_frame, "공기 저항 계수 (k):", 0.0, 1.0, 0.1, 3)
        
        # 실행 버튼
        run_btn = ttk.Button(control_frame, text="시뮬레이션 시작", command=self.run_simulation)
        run_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        # 그래프 영역 설정
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().grid(row=0, column=1, padx=10, pady=10)
        
        self.run_simulation()

    def create_slider(self, parent, label, from_, to, default, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W)
        var = tk.DoubleVar(value=default)
        slider = ttk.Scale(parent, from_=from_, to=to, variable=var, orient=tk.HORIZONTAL)
        slider.grid(row=row, column=1, sticky=(tk.E, tk.W), padx=10)
        return var

    def run_simulation(self):
        # 입력값 가져오기
        v0 = self.v0_var.get()
        angle = math.radians(self.angle_var.get())
        m = self.mass_var.get()
        k = self.drag_var.get()
        
        # 초기화 (위치, 속도)
        x, y = 0.0, 0.0
        vx = v0 * math.cos(angle)
        vy = v0 * math.sin(angle)
        
        # 진공 상태 비교용 초기화
        x_vac, y_vac = 0.0, 0.0
        vx_vac = v0 * math.cos(angle)
        vy_vac = v0 * math.sin(angle)
        
        # 데이터 저장 리스트
        x_list, y_list = [x], [y]
        x_vac_list, y_vac_list = [x_vac], [y_vac]
        t_list = [0.0]
        
        ke_list = [0.5 * m * (vx**2 + vy**2)]
        pe_list = [m * self.g * y]
        loss_list = [0.0]  # 공기 마찰로 잃은 에너지
        total_energy = ke_list[0] + pe_list[0]
        
        t = 0.0
        # 오일러 메서드를 이용한 수치해석 시뮬레이션 루프
        while y >= 0:
            t += self.dt
            v = math.sqrt(vx**2 + vy**2)
            
            # 공기 저항력 반영 가속도 계산
            ax = -(k / m) * vx
            ay = -self.g - (k / m) * vy
            
            # 위치 및 속도 업데이트 (Euler Method)
            x += vx * self.dt
            y += vy * self.dt
            vx += ax * self.dt
            vy += ay * self.dt
            
            # 에너지 계산
            ke = 0.5 * m * (vx**2 + vy**2)
            pe = m * self.g * y
            # 손실 에너지(일) = 저항력 * 이동거리 근사
            work_done_loss = (k * v) * (v * self.dt)
            loss_list.append(loss_list[-1] + work_done_loss)
            
            x_list.append(x)
            y_list.append(y)
            ke_list.append(ke)
            pe_list.append(pe)
            t_list.append(t)
            
            # 진공 상태 (비교용) 업데이트
            if y_vac >= 0:
                x_vac += vx_vac * self.dt
                y_vac += vy_vac * self.dt
                vy_vac += -self.g * self.dt
                x_vac_list.append(x_vac)
                y_vac_list.append(y_vac)

        # 궤적 그래프 그리기 (왼쪽)
        self.ax1.clear()
        self.ax1.plot(x_list, y_list, 'b-', label='실제 환경 (공기저항 k)')
        self.ax1.plot(x_vac_list, y_vac_list, 'r--', label='진공 환경 (k=0)')
        self.ax1.set_title("궤적 비교 (공기저항 vs 진공)")
        self.ax1.set_xlabel("수평 거리 (m)")
        self.ax1.set_ylabel("높이 (m)")
        self.ax1.legend()
        self.ax1.grid(True)
        
        # 실시간 에너지 보존 그래프 그리기 (오른쪽)
        self.ax2.clear()
        self.ax2.plot(t_list, ke_list, 'g-', label='운동 에너지 (K)')
        self.ax2.plot(t_list, pe_list, 'y-', label='위치 에너지 (U)')
        self.ax2.plot(t_list, loss_list, 'r-', label='마찰 손실 열에너지 (W)')
        # 세 에너지의 합 (보존성 확인)
        total_list = [ke_list[i] + pe_list[i] + loss_list[i] for i in range(len(t_list))]
        self.ax2.plot(t_list, total_list, 'k--', label='총 에너지 합')
        
        self.ax2.set_title("시간별 에너지 보존 추적")
        self.ax2.set_xlabel("시간 (s)")
        self.ax2.set_ylabel("에너지 (J)")
        self.ax2.legend()
        self.ax2.grid(True)
        
        self.fig.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = PhysicsSimulator(root)
    root.mainloop()