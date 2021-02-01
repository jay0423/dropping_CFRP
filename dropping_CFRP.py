import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time


class GetHoleCoordinate:

    gcode = pd.DataFrame()
    closest_X = []
    closest_Y = []
    
    def __init__(self, csv_file_name=-1, animation=-1, plot_marker=-1, layer=-1, holes=-1):
        self.csv_file_name = csv_file_name
        self.animation = animation
        self.plot_marker = plot_marker
        self.layer = layer
        self.holes = holes
        # self.hole_count = []
        # self.plot_3d = False
        

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
        self.gcode = new_gcode


    def drop_E_zero(self, df):
        #フィラメントを押し出さない部分の削除
        new_df = df.copy()
        for i in range(len(df) - 1):
            if df.iloc[i + 1].E == 0:
                new_df.drop(df.iloc[i].name, inplace=True)
        return new_df
    

    def ok_or_not(self, df):
        #プロットしたい点に重複がないかの確認、okがTrueのときは重複がない
        ok = True
        for i in range(len(self.closest_X)):
            if self.closest_X[i] == float(df.iloc[0].X) and self.closest_Y[i] == float(df.iloc[0].Y):
                ok = False
                break
            else:
                ok = True
        return ok


    def find_hole(self, margin, df, x, y):
        search_gcode = df[(df.X < x + margin / 2) & (df.X > x - margin / 2) & (df.Y < y + margin / 2) & (df.Y > y - margin / 2)]
        if len(search_gcode) == 1: #クリック付近の点が1つのとき
            ok = self.ok_or_not(search_gcode)
        elif len(search_gcode) >= 2 and len(search_gcode) <= 4: #クリック付近の点が複数のとき
            search_gcode['distance'] = ((search_gcode.loc[:, 'X'] - x) ** 2 + (search_gcode.loc[:, 'Y'] - y) ** 2) ** 0.5 #距離の算出
            search_gcode = search_gcode.sort_values('distance')
            ok = self.ok_or_not(search_gcode)
        else: #クリック付近の点が5つ以上の時
            return
        if ok:
            self.closest_X.append(float(search_gcode.iloc[0].X))
            self.closest_Y.append(float(search_gcode.iloc[0].Y))
        else:
            return

    """
    #エポキシ樹脂の埋め込む量の算出
    def epoxy_volume(self, hole_X, hole_Y):
        layer = 0
        not_hole = True
        hole = False
        layer_thickness = 0.15
        from_layer = 0
        #穴の空いている層の検出
        while True:
            while True:
                print(layer)
                layer += 1
                gcode = self.gcode
                if len(gcode[(hole_X - 2 < gcode.X) & (gcode.X < hole_X + 2 ) & (hole_Y - 2 < gcode.Y) & (gcode.Y < hole_Y + 2 )]) > 0 and not_hole == True:
                    from_layer = layer
                    not_hole = False
                    print("not_hole")
                elif len(gcode[(hole_X - 2 < gcode.X) & (gcode.X < hole_X + 2 ) & (hole_Y - 2 < gcode.Y) & (gcode.Y < hole_Y + 2 )]) > 0 and hole == False:
                    to_layer = layer
                    hole = True
                    print("hole")
                if not_hole == False and hole == True:
                    break
                if not_hole == False and hole == False and 10 == layer - from_layer:
                    layer += 200
            #バグ回避用
            if to_layer - from_layer < 10:
                not_hole = True
                hole = False
            else:
                break
        return (to_layer - from_layer) * layer_thickness"""


    #書き込み
    def write_dropping_CFRP(self, gcode, hole_X, hole_Y):
        #CFRP落下のgcodeの取り込みと作成
        dropping_gcode = pd.read_csv('dropping_CFRP_gcode.csv', names=['a', 'b'])
        dropping_gcode.replace('G0 X9999', 'G0 X{}'.format(round(hole_X - 62, 3)), inplace=True)
        dropping_gcode.replace('G0 Y9999', 'G0 Y{}'.format(round(hole_Y - 32, 3)), inplace=True)
        dropping_gcode.replace('G1 X8888 Y8888 F2000', 'G1 X{} Y{} F2000'.format(round(hole_X - 35.3, 3), round(hole_X - 24.5, 3)), inplace=True)
        # dropping_gcode.replace('G1 E7777 F40', 'G1 E{} F40'.format(self.epoxy_volume(hole_X, hole_Y)), inplace=True)
        dropping_gcode.replace('G1 E7777 F40', 'G1 E{} F40'.format(10), inplace=True)
        #フルgcodeの取り込み
        if len(self.closest_X) == 4:
            printing_gcode = pd.read_csv('gcode/' + self.csv_file_name, names=['a', 'b'])
        else:
            printing_gcode = pd.read_csv('new_gcode/new_' + self.csv_file_name, names=['a', 'b'])
        insert_num = printing_gcode[printing_gcode == ';LAYER:{}'.format(self.layer)].dropna(how='all').index[0]
        df1 = printing_gcode[printing_gcode.index < insert_num]
        df2 = printing_gcode[printing_gcode.index >= insert_num]
        #printing_gcode内にdropping_gcodeを挿入
        new_printing_gcode = pd.concat([df1, dropping_gcode, df2])
        #最終版の書き出し
        for i in range(len(new_printing_gcode.dropna())):
            loc_num = new_printing_gcode.dropna().iloc[i].name
            new_printing_gcode.loc[loc_num].a = new_printing_gcode.dropna().iloc[i].a + ', ' + new_printing_gcode.dropna().iloc[i].b
        new_printing_gcode.drop('b', axis=1, inplace=True)
        new_printing_gcode.to_csv('new_gcode/new_' + self.csv_file_name, index=False, header=False)
    
    
    
    def onclick(self, event): #穴の検出
        plots_dot_num = self.holes * 4
        #ダブルクリックした時の処理
        if event.dblclick:
            #穴探し
            self.find_hole(margin=0.4, df=self.drop_E_zero(self.gcode), x=event.xdata, y=event.ydata)
            plt.plot(float(self.closest_X[-1]), float(self.closest_Y[-1]), marker='o', color='red')
            plt.draw()
            #4点が選択された後の処理（四角のみ対応）
            if len(self.closest_X) % 4 == 0 and len(self.closest_X) != 0 and len(self.closest_X) <= plots_dot_num:
                plt.fill(self.closest_X[len(self.closest_X) - 4: len(self.closest_X)], self.closest_Y[len(self.closest_X) - 4: len(self.closest_X)], color='red', alpha=0.5)
                hole_X = np.mean(self.closest_X[len(self.closest_X) - 4: len(self.closest_X)])
                hole_Y = np.mean(self.closest_Y[len(self.closest_X) - 4: len(self.closest_X)])
                plt.plot([hole_X - (max(self.closest_X[len(self.closest_X) - 4: len(self.closest_X)]) - min(self.closest_X[len(self.closest_X) - 4: len(self.closest_X)])) * 0.15, hole_X + (max(self.closest_X[len(self.closest_X) - 4: len(self.closest_X)]) - min(self.closest_X[len(self.closest_X) - 4: len(self.closest_X)])) * 0.15], [hole_Y, hole_Y], 'r-')
                plt.plot([hole_X, hole_X], [hole_Y - (max(self.closest_Y[len(self.closest_X) - 4: len(self.closest_X)]) - min(self.closest_Y[len(self.closest_X) - 4: len(self.closest_X)])) * 0.15, hole_Y + (max(self.closest_Y[len(self.closest_X) - 4: len(self.closest_X)]) - min(self.closest_Y[len(self.closest_X) - 4: len(self.closest_X)])) * 0.15], 'r-')
                self.write_dropping_CFRP(self.gcode, hole_X, hole_Y)

    
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
        fig.canvas.mpl_connect("button_press_event", self.onclick)
        plt.show()

    
    def inputs(self):
        if self.csv_file_name == -1:
            while True:
                input_ = input('gcodeをファイルを入力してください:')
                if input_ != "":
                    self.csv_file_name = input_
                    if not '.csv' in self.csv_file_name:
                        self.csv_file_name = self.csv_file_name + '.csv'
                    break
        if self.animation == -1:
            while True:
                self.animation = input('アニメーションとしますか？ y/n:')
                if self.animation == 'y':
                    self.animation = True
                    break
                elif self.animation == 'n':
                    self.animation = False
                    break
        if self.plot_marker == -1:
            while True:
                self.plot_marker = input('点の表示は入れますか？ y/n:')
                if self.plot_marker == 'y':
                    self.plot_marker = True
                    break
                elif self.plot_marker == 'n':
                    self.plot_marker = False
                    break
        if self.layer == -1:
            while True:
                try:
                    self.layer = int(input('何層目にCFRPを埋め込みますか？ layer='))
                    break
                except:
                    pass
        if self.holes == -1:
            while True:
                try:
                    self.holes = int(input('穴はいくつありますか？ holes='))
                    break
                except:
                    pass
        
        
    def main(self):
        self.inputs()
        self.make_original_gcode()
        self.plot_from_gcode()
        


if __name__ == "__main__":
    a = GetHoleCoordinate()
    a.main()