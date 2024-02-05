Run commands:
```
.\python_embeded\python.exe -s generate_portraits.py
.\python_embeded\python.exe -s generate_background.py
```
For systems without NVidia GPU (quite slow):
```
.\python_embeded\python.exe -s generate_portraits.py --cpu --windows-standalone-build
.\python_embeded\python.exe -s generate_background.py --cpu --windows-standalone-build
```

Outputs can be found in folder ./ComfyUI/output/

Look at the very end of generate_background.py and generate_portraits.py for details on how to change positive/negative prompts