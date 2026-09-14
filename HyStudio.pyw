"""Double-clic : lance HyStudio sans fenetre de console."""
import os, runpy, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
os.chdir(here)
runpy.run_path(os.path.join(here, "hystudio.py"), run_name="__main__")
