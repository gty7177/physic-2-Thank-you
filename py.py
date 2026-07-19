
import math
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib

matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False
class PhysicsSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("물리 시뮬레이터")
        self.g = 9.8
        self.dt = 0.005

        frame = ttk.Frame(root,padding=10)
        frame.grid(row=0,column=0,sticky="ns")

        self.v0=self.slider(frame,"초기 속도(m/s)",5,50,20,0)
        self.ang=self.slider(frame,"발사각(°)",10,80,45,1)
        self.mass=self.slider(frame,"질량(kg)",0.1,5,1,2)
        self.drag=self.slider(frame,"공기저항 k",0,1,0.1,3)

        ttk.Button(frame,text="시뮬레이션",command=self.run).grid(row=4,column=0,columnspan=2,pady=8)

        self.fig,(self.ax1,self.ax2)=plt.subplots(1,2,figsize=(10,4))
        self.canvas=FigureCanvasTkAgg(self.fig,master=root)
        self.canvas.get_tk_widget().grid(row=0,column=1)
        self.run()

    def slider(self,parent,text,a,b,d,row):
        ttk.Label(parent,text=text).grid(row=row,column=0,sticky="w")
        var=tk.DoubleVar(value=d)
        ttk.Scale(parent,from_=a,to=b,variable=var,orient="horizontal").grid(row=row,column=1,sticky="ew")
        return var

    def run(self):
        v0=self.v0.get()
        ang=math.radians(self.ang.get())
        m=self.mass.get()
        k=self.drag.get()

        x=y=0
        vx=v0*math.cos(ang)
        vy=v0*math.sin(ang)

        xv=yv=0
        vxv=vx
        vyv=vy

        xs=[0]; ys=[0]
        xsv=[0]; ysv=[0]
        ts=[0]
        ke=[0.5*m*(vx*vx+vy*vy)]
        pe=[0]
        loss=[0]
        initial=ke[0]

        t=0
        while True:
            v=math.hypot(vx,vy)

            ax=-(k/m)*vx
            ay=-self.g-(k/m)*vy

            dx=vx*self.dt
            dy=vy*self.dt
            ds=math.hypot(dx,dy)

            drag_force=k*v
            loss.append(loss[-1]+drag_force*ds)

            x+=dx
            y+=dy

            vx+=ax*self.dt
            vy+=ay*self.dt

            t+=self.dt

            if y<0:
                y=0

            xs.append(x)
            ys.append(y)
            ts.append(t)
            ke.append(0.5*m*(vx*vx+vy*vy))
            pe.append(m*self.g*y)

            if yv>=0:
                xv+=vxv*self.dt
                yv+=vyv*self.dt
                vyv-=self.g*self.dt
                xsv.append(xv)
                ysv.append(max(0,yv))

            if y==0 and vy<0:
                break

        total=[ke[i]+pe[i]+loss[i] for i in range(len(ts))]

        self.ax1.clear()
        self.ax1.plot(xs,ys,label="공기저항")
        self.ax1.plot(xsv,ysv,"--",label="진공")
        self.ax1.set_xlabel("x(m)")
        self.ax1.set_ylabel("y(m)")
        self.ax1.grid()
        self.ax1.legend()

        self.ax2.clear()
        self.ax2.plot(ts,ke,label="운동E")
        self.ax2.plot(ts,pe,label="위치E")
        self.ax2.plot(ts,loss,label="손실E")
        self.ax2.plot(ts,total,"k--",label="총E")
        self.ax2.axhline(initial,linestyle=":",label="초기 총E")
        self.ax2.set_xlabel("시간(s)")
        self.ax2.set_ylabel("에너지(J)")
        self.ax2.grid()
        self.ax2.legend()

        self.fig.tight_layout()
        self.canvas.draw()

if __name__=="__main__":
    root=tk.Tk()
    PhysicsSimulator(root)
    root.mainloop()
