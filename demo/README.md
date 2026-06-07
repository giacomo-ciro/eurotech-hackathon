Download the URDF and STL files from:
```
https://huggingface.co/haixuantao/dora-bambot/tree/main/URDF
```
and place in `dump/so101.urdf` and `demo/assets/*.stl`.

To run:
```
uv pip install -r requirements.txt
rerun &     # server in the background
python demo/rerun_demo.py
```
