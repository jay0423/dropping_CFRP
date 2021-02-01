# dropping_CFRP

熱溶解積層法3Dプリンターにおいて，CFRPとエポキシ樹脂を埋め込む際の穴座標を検出，算出し，gcodeファイルに自動的に書き込むソフト．  
なお，gcodeのスライサーはUltimaker Cura 3.4.1に対応しており，それ以外のスライサーには非対応．  
*gcode内に";LAYAR:"という表記があれば対応可能．  

## SetUp
本ソフトウェアの活用に必要なソフトウェア，およびライブラリ一覧
- iPython　`sudo apt install ipython`
- numpy `pip install numpy`
- pandas `pip install pandas`
- matplotlib `pip install matplotlib`
- mpl_toolkits `pip install mpl_toolkits`

なおnumpyとpandasについてはipythonをインストール際にパックでインストールされるためpipでインストールする必要はない．  
*ipythonは[anaconda](https://www.anaconda.com/products/individual)からのインストールを推奨．


## ディレクトリ構成
- gcode：変更前のgcodeを格納するディレクトリ
- new_gcode：書き変えられたgcodeを出力するディレクトリ
- dropping_CFRP.py：pythonプログラム
- dropping_CFRP.csv：埋め込むgcode（カスタマイズ可）


## 使用方法

1. 「gcode」ディレクトリに穴座標を知りたいgcodeファイルを格納．
2. 1のファイルの拡張子を.gcodeから.csvへ変更させる．
3. 以下のコマンドを入力．
```
cd ~/dropping_CFRP
ipython dropping_CFRP.py
```
4. コマンドの手順に従ってファイル名とアニメーションの有無、プロットマーカーの有無、CFRPとエポキシ樹脂を埋め込みたい層の指定、穴の数を入力．
5. matplotlibによって指定された断面の図が描画されるため、穴の4点をダブルクリックすることで穴の四点を指定．
6. "5"を穴の数だけ繰り返す．
7. 穴の指定が終わった後、dropping_CFRP>new_gcodeのディレクトリ内に頭に「new_」とついたcsvファイルが出力される
8. 拡張子を.csvから.gcodeへ変更する．

## Author
Jumpei Kajimoto
