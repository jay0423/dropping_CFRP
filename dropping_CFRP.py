import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time


class MAKE_POINT:
    def __init__(self, csv_file_name=-1, animation=-1, plot_marker=-1, layer=-1, holes=-1):
        self.csv_file_name = csv_file_name
        self.animation = animation
        self.plot_marker = plot_marker
        self.layer = layer
        self.holes = holes
        
        self.gcode = 0
        
        self.closest_X = []
        self.closest_Y = []
        self.hole_count = []
        self.plot_3d = False
        
    def read_csv(self):
        #gcodeの取り込み
        col_names = ['c{0:02d}'.format(i) for i in range(10)]
        return pd.read_csv('gcode/' + self.csv_file_name, sep='\s+', names=col_names)
    
    def cleaning_df(self, gcode):
        #指定layerの抽出
        num_first = gcode[gcode == ';LAYER:{}'.format(self.layer)].dropna(how='all').index[0]
        num_last = gcode[gcode == ';LAYER:{}'.format(self.layer + 1)].dropna(how='all').index[0]
        gcode = gcode[(gcode.index >= num_first) & (gcode.index < num_last)]
        #gcodeの整理
        gcode = gcode.replace('G0', 'G1')
        gcode = gcode[gcode.c00=='G1']
        gcode.dropna(axis=1, how='all', inplace=True)
        gcode.fillna(0, inplace=True)
        return gcode
    
    def make_original_gcode(self):
        """
        出力：座標のみを取得し，データフレームを作製
        """
        gcode = self.read_csv()
        gcode = self.cleaning_df(gcode)
        #X, Y, Z座標及び，Eをデータフレームに組み込む
        new_gcode = pd.DataFrame(np.zeros([len(gcode), 4]), index=gcode.index, columns=['X', 'Y', 'Z', 'E'])
        for i in range(len(gcode)):
            for j in range(4):
                if gcode['c0{}'.format(j + 1)].iloc[i] != 0:
                    new_gcode.iloc[i].loc[gcode['c0{}'.format(j + 1)].iloc[i][0]] = float(gcode['c0{}'.format(j + 1)].iloc[i][1:])
        #new_gcode = new_gcode[new_gcode.X != 0]
        self.gcode = new_gcode
       
    
    def plot_from_gcode(self):
        #表示範囲の確定
        xmin = min(self.gcode.X)
        xmax = max(self.gcode.X)
        ymin = min(self.gcode.Y)
        ymax = max(self.gcode.Y)
        fig = plt.figure(figsize=(6,6))
        plt.xlim(xmin - 1, xmax + 1)
        plt.ylim(ymin - 1, ymax + 1)
        #線のプロット
        for i in range(len(self.gcode) - 1):
            # 更新待機（秒）
            if self.animation:
                plt.pause(0.01)
            if self.gcode.E.iloc[i + 1] != 0:
                from_X = self.gcode.X.iloc[i]
                from_Y = self.gcode.Y.iloc[i]
                to_X = self.gcode.X.iloc[i + 1]
                to_Y = self.gcode.Y.iloc[i + 1]
                plt.plot([from_X, to_X], [from_Y, to_Y], 'b-', linewidth=10, alpha=1)
                if self.plot_marker:
                    plt.plot(from_X, from_Y, marker='o', color='deepskyblue', markersize=3)
                    plt.plot(to_X, to_Y, marker='o', color='deepskyblue', markersize=3)
        plt.xlim(xmin - 1, xmax + 1)
        plt.ylim(ymin - 1, ymax + 1)
        ln, = plt.plot([],[],'o', markersize=7, color='red')
        ln_v = plt.axvline(0)
        ln_h = plt.axhline(0)
        def motion(event):  
            x = event.xdata
            y = event.ydata
            ln.set_data(x,y)
            ln_v.set_xdata(x)
            ln_h.set_ydata(y)
            plt.draw()
        plt.connect('motion_notify_event', motion)
        #fig.canvas.mpl_connect("button_press_event", onclick)
        plt.show()

    
    
    
    def inputs(self):
#        while True:
        if self.csv_file_name == -1:
            self.csv_file_name = input('gcodeをファイルを入力してください:')
            if not '.csv' in self.csv_file_name:
                self.csv_file_name = self.csv_file_name + '.csv'
        if self.animation == -1:
            self.animation = input('アニメーションとしますか？ y/n:')
            if self.animation == 'y':
                self.animation = True
            elif self.animation == 'n':
                self.animation = False
            else:
                '始めからやり直してください'
                return 
        if self.plot_marker == -1:
            self.plot_marker = input('点の表示は入れますか？ y/n:')
            if self.plot_marker == 'y':
                self.plot_marker = True
            elif self.plot_marker == 'n':
                self.plot_marker = False
            else:
                '始めからやり直してください'
                return                 
        if self.layer == -1:
            try:
                self.layer = int(input('何層目にCFRPを埋め込みますか？ layer='))
            except:
                print('始めからやり直してください')
                return
        if self.holes == -1:
            try:
                self.holes = int(input('穴はいくつありますか？ holes='))
            except:
                print('始めからやり直してください')
                return
        
    def main(self):
        self.inputs()
        self.make_original_gcode()
        self.plot_from_gcode()
        
if __name__ == "__main__":
    a = MAKE_POINT()
    a.main()