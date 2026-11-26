#!/usr/bin/env python3
import argparse
import bluebridge_updater
import collections
import datetime
import platform
import base64
import hashlib
import json
import os
import signal
import shutil
import struct
import subprocess
import sys
import time
import threading
import fcntl
import glob
import select
import termios
import urllib.parse
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import urllib.error
import urllib.request

DAEMON_VERSION = "1.2.0"

LOGO_PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAUAAAABQCAYAAABoMayFAAAACXBIWXMAAAsTAAALEwEAmpwYAAAX50lEQVR4nO2dX2wcRZ7Hv9Xjf3FMMuMkOIkB2Q5GF3GwgA92V1oOBF7Q7aJk98HZg717grWlBQEroTMSf24f0F4s7Wn34diLEwmxf3g4IsgC5rS6WEgHL+iIb489InA2cUhEDgy2Zxz/mX+eqXto17inXT1dVV3d047rI7XkGXfXn57qb/+qflW/IpRSGAwGw2bEqncBDAaDoV4YATQYDJsWI4AGg2HTEqkA/uTJJx8ghJwnhCxHmS8ArOZ7Pup8DQZDfGmIMrMtra2LhJCuejheCCFdkWdqMBhiTaQC+PHHH19VL6+z8XYbDAY3kXSBOzs7L1qWRb/x9a+/mUmnQSmFZVnUsqxQVenUBx/ssiyLEkJoem4OmXQahBBqWRb9yZNPHgwzb4PBEH8isQDLpVITpRRbt27F9mQSQDQWWVtb2wLLJ5lKVb6nlOLc1FQy9AIYDIZYE5oFODAw0EEIoYQQevbs2Y5MOo3W1lYQQkAIQSadRnpuDuycd95553pdebM0jx07ls2k01heWqrkSylFJp3Gd7/znZcJIbS9vX1GV74Gg2FjEZoFuGPHjhL7m1IKSikIUBEhdmD1O90QQmBZ1lrejjyc31mWVaqRjEGOQQCjEudPAdgXMD9m2g87/q7F067Px1fLYdiEaBfABx54YOzs2bPXtLe3zzGB6+joQKlUwvDdD2H5xXfRsn0ndvb2VgQKlOKFF174+0cfffTA9PT0nrm5ud0qee/fv/+PCwsLV7E0333vPVzf24vFpSUs/ct/VqzAHTt2YHh4GOVSCRT4v66urk8aGxuLd9xxxwOvvPLKBa03ZI0eAOc0pPNXACYUrjsFoC9g3uMAvh0wDScqwjPgOFQ4zPmcBtDu+n6Yc25cmIDdDgwB0S6AmUym5cyZM1/r7e3FwuXLsCwLxWIRmUwGhVIRl7NLAIC5uTkAwNLiIlZWVkAIeX5ycjLQ2ODk5OQtlFIU8nlks1nk83nMzc2BUoqF3NrUw7m5OSQSCczPz6OpqemWCxdszdu/f3+YA5Mi1okIfZAXwD4EF7960w9bkMKoh67fJirS9S7AlYI2AfzewYO7Z2dncfWuXbPd3d3o3LsXMzMzsCwLpZLdy1zO57CUzyJhJSrXpdNpFAoFNDU3o7u7G8VCAX995527ZYVwenqadnd3I5fL4YvpaawUi1heXhO9pXy26vzM/DxmZ2dBCMF1112HRCKBmZmZ5J3f+lZh3/XXZ15++eVcgNvBQ9dD1qNwTb+mvP0sNtk6ilqAUVhjPaguj8p9jgrTZdeFczwuyNHT3X2WEEKzS0s0k07TqXPnKADKHBJ+x+uvv04z6TRdKRaFr3EeAGgmnabZ5WWpfNva2ujy0hKdz2ToLbfcQgkh9O677rpb131xHINUD6cU8p7TlPeoTz7DmtNTSVOVPle+oxHlq8Jhqr99bspDmwVYLpctStesNva38zs/Ieb9LQtzdajkyz6XSiX9Xhm9XWC3tVILp6MgKLotD7/0+hDdOFwPqocW4twtNl1gTQQWwFXrC5RSLC0uIl8oAAB27tyJxYUF4XRKpRIopVhcXJS6zsnKygpy+bz09YXVMr/37rsghODRxx57hxCCXbt2zX755Zc7lQoTLgMARgTPHQ6zIC5GIF4uEaJ0Qri7vHEWQIMmtFiAbIrJyspK5TtKadVnGVSvC3o9G6sEtafINDQ0FAIVpBqdY0qiAtivOd8oLY8U1McupwAcXT14ZU7BtowZAzACuCmJdC3wJkfnA8W8un7e4CitP92oit9RAEM+56RR/QLhvUxUppmchHy5h2CXOWxYW0ihdrtw3ps0oimbm37Y7Zs3t3MfNA7FGAGMDt0WRT9qC2A/9Hl/GX4N7xzkLM5a89lU75d7onPcCdOjOwzb0pX5TVKoHnoYhT1ZnB0iyM55ZS8tNuaru916oiSAw8PDN+ZzuUQun7f+7oc/BCEExYLO3mJ9+cY3v4lyuYzmlpb/euLxx2/OFwqJI0eO/DFgsrqnVfh1g0WtvzTq192r9fBvloH+MOqpe9oQm3g+AVuoVCbii+Txagjp1oSoeFy7urr+cPHixfsppZjPZAJ5bePM9mTSuZwuqGd4DmJCcxziqxy8VoWIvoGPY82rHCQ/hqwFWKu7moJ9z2QR6QKHhcpqm3boE8Ee2CIS9qT3Q6htDcr+dlMQbzdau8AmJH40pCBuZYl2MwDvroKo9Sc7vqPbWvGzAFXGnwZRB0tiFRVLWtc97YOe5Y4ivIpqJ5Ib2TrJvDS19qSMAEaD6IMxBXu9rSg8S9Ht4dSVlwiyAuD3oIwInMNjALY1GtlYkiK6LJkUbFGKcihjFBt/eaURwIgQfWtNwX7gRYWpD+sbvYj4AWrWlZ8Y6RbAKagHX+iB7ZWViU4TFN31F2UUcpZRGrazqB322gECe3hDtk3UI1iEsQA3IDICCMhZZm4rR0QAVbuXurvAIukxT7Fq3oOwrUHV6DEy1EMAZSPjTMAeR3Nb18zBIeNFZ9NVNixGAKNBpgsMyI0DOhug6MTn44iHl1W0C8hEULXLzpwDUXcT/dDxG8haYYd88h2BXNecJ75BrTTmyCKcQ+u8RCOA0SD60LGGOQXxqQZOC1DUEnAKrC5BCFtYWHc4yDy/AdjeyTCsQZWHPqgAyq70OQoxcZN50ei0AKdgv+iimhxuBDAiVB4OUSuQjQOKOj8mUN3AZcXZCxUBVHECjMB+SII4EF5FPIKd6hBAGXQ7vQB9Y3LsBRfGHENPYrkShG2ctLqLW81zGxsb0bp1KwBgPpMJuWTKyI4BAvLjgKICpPpmjUOXmcHGsUYh7vRxMwz75aErwnU9psDICmAY04N4bVtFFIdQhziHsbMA29raKqHr29rafM8/c+ZM5fwYI9og3IPSog2iD2LdujTC6f4C8o1eh6AOwRYw1bT6YXuKdRD12GIK8XBA6Pgd3b2SyNAmgDqDFDp3cPM7rESiIn668g8B1W6maDd4AGLWgDs6Sj0dArosynHY1qCM48gJC7UflKjHAOPizNFhtdVF/ABNXWBKKR5/4gnosMFatmyp/D00NLQWosqDy5cvV/5+4oknNJQAeOSRR3DzzTdrSQtyD4a7MYmOh4jmEWRgOYwxQF2kYXs3ZXelYwzDfgjr9iBuYLyWYspQtxD/2sYA33jjDSwoBjL14uVf/1r4XEIIfvu732nJ9+DBg1rSWSXIIPE49AUrGMf6hiaTbpwFkHEU9gN5SuHafgQTwKicQEGI6zjRxhdARmdnp2c3MpvNIp2u/RxRStHZ2QkAuHTpEgghSKVSsKzq3nomk0GpVEJrayuSySQIIbh06ZJv+a655hqUy2Xu/7766isUi0XfNCRRcYAw2KoQHdM2eNafTtGKgwACtgCOQD4WYtBlc1HXn60aist9dxLW5lja0S6Af56crITFd/Paa6/hkR/9yDeN0x99BABIpuz7+E8/+xk6r7mm8n/LsjA4OIhLly7hwIED+Ndf/Qqtra1obmnxTfvixYtcbzEhBHfdfTc+/PBD3zQkCTrNZALBBXAK6mNkYREnr7IO6iFEU5BzhAS1ckWJoyhzidQLXC6XPR0NOhwQtdII0cHhR1AB1NFgvcb+dK6r1OUF7oPtmR1WSJOVQ+WFEdQKqcdEaNmXWlRzHzeMBSglgGwryQsXLtyvktlDDz2EXDbLFaKxsTHkslnkc2rb8S4tLVXS5u30ll1eRi6bRcanC85j1SvNttKckbw8SBcYsC3AIJND6xXWXJUJrHlmzwGgsB0bw+CHSGcMrP5fNiahM98g1EMAZX/XqEJmxXlP5Sqku8BB5tsVi0UUi0VuV7VQKCCnKH6sXLlcztPKy+VygeYLOqbayHp6dDSGcag32lrrfmXe1H5vaZ2N3h0g0znZOQwrRsdLoh7dPrZ/h8x4JxNB5vU+jtq/rTtttoFUe41rNkwXWEgADxw48G8AcGZyksLhSSoUi0rdysWFBUx+8knVd62trZ7n/+KXv0SrY3oMAMzM8A2xYrGI06dPo7GhumoqwscrJ6X0P9j9ePPNN38gkExQCxAIZp1EZf2FKYBhoxp3kCET8FY3I+DvaucH2zNG5YXi1/W+sgRwbGzsEAD89je/0ZJpqVTC1VdfLXz+5OSk8Lnlchmde/eqFGsdHuUcHBsbY8LvJ4C6HgzV6TDjqC2e9VwJUosox4SOIvhexqr3UYcjiM2BPBmgHLL4vZCv3C6wF7feeisopZiensbK6uTlnTvl9xRPJBKYnp6u+u5re3qxtam62/zfl84gt5JHPp/HzMwMSqUSOjo6lMr+1VdfwbIs3HTTTdi2bRu2rq4t1oBMt7XWw6A6HSaqN7XuBh+Vh3gEenaRU62/rnqycGFR7AcC1HbMbRjrD9C4Mfobv/89AODW227Dp59+it7eXpz64APPOXdebNmyBb033FBJFwB+8d3H0dPeWZXfPccew7m5Szhx4gROnDgBSqmSg6OpqamS3//+6U+49tprpdOogU5hkJ0OIzKutVkFcAK28OmaEhIHi4eFktK9I5ybNKLrVYSOkADKjPMtLy1V1vO2tLRIC2CioWFdfglYaEysFdW59tdJi8A8QDeNjY2Vv/2W3TEk7ofOB0P2YRXp1sk01lp12SgCeBS2VVzvvVDCZAR2PQchvyewCH73Lg4vA2F8t8UkhNDL8/MAICRmbMXG7OwsunvU7sXbb79d9fnIkSN46623qr577bXXqgSvpaUF9957r3ReW7duxezMDAqFgrBYszpu275dx3aZBm/6sH6FhmjkmwmsDQHULdpITHB6cgcg3k12B1ANOlYaO4QsQBkrjp3LhFXW++o1YdmZDqUUpVKp6rzyqtUpCyEE5XJZqY4xD8F1JRB0DqTBZsTj702PkAWoMrZGKUU+n/c9Z8/evSCE4B9/+lP85Y03AljflV1ZWcHKykrVd83NzesEKJfLoSGRwPe+/30QQvDoj3+MZ5991resKl1nAEi1t6NcLhsVNBg2KKFFhGZjgLVwiq8FbyFqaGhAQ4N/UVtaWtDU1FT53NzcrCxuBoPhyqfuIfH/9gf2VLpEIoEvp6dBKUXH7t1V56TTaRRdARZ2XX11lQVICMH0F1/AsiwcGhiAZVnoUhyDNBgMm4PQusCisPxffPFFPPf886CUYmxsrOqc0dHRqu8opXj11VerVo80NzfjvvvuA6UUuWwW2Ww29DE60wU2GDY2QhYgW4a2nM1qL8DWVRFjkWIAW8yc8BwjiUSi6rzm5ua161taYBGCUrnsOw6pArsfdYouYzAYNOErgJRSQgihAJQmGvukjabVMTrH8rJ1lttLL72Ep556qvI5kUjgwQcfxGeffbYuPef1Dz/8MP755z/XWmYAlTKbKTAGw8ZGyAIMuytJCEGhUMB8JlPZFc7JSrGIxcXFymfLsuxt4l1TY+YzmYpVSAhBcvv20MprrD+DYeNTdyeIm3w+j9EjR6oEZnp6Gh+dPl35TCnFM888UyWAy8vLkZbTsKkYgNw2pYYNQuwEsFgs4tChQ1Xf/cPwMI4dO1b5TCnFpc8+0xm0oN6wKMY9UFtKdBy1oz57pc0e6loxA50cxvpVBLo2tB7F+vK5Ny3n5a8CWxkiujrk8Oq5QxJ58Mo6IpEnow/r1/byfm9efqKbvutqI1HXOTBCArhjx45pALAsa124Fdm1vm7a2tqQSCTWbXrkpLGxEdu2bat89luz29raisbGxqp1vqpwyvU/O3bs2AM9O2z1wP6hg+75wWtgImmzZWaHsbaGtFYj5y1NG4X4g+YFW7fqBy9/FfphLw87DlvUatWZracdhH2PZDar5y3j+zbkVrekOOnwfm+Ve6O7jURd58D4ToOpOtkOCV/5zMbdgoyHiS6Zc+dR63zVZXhutieT6wSQUvoppbQ7UMI2OqN2PI3qJU6qabPYcl6N7ST4D9khqG+6lIIdxp4XUMD9A3rlH4QJ2A+o10PtDLF/FOJWoFdZ05AThP7VtJy4f2+v/Go9AGG0kajrHBipPUEsyyoTQspUowdANEw9O0/k/CCh72ukWSaElC3LCmby2owivJBFQdJOwW54ItaYk8NQj4hSa5+PKOB1txjujZkGEbwLzu5xFHH7vIi6jcShzlykxgBLpVICAPbt2/fv58+f/5twihQ/KKUol8sJTckdhnfjOQ61AACsWyaadgpr4z68RjkK+60tatU5u4gy9EB+/143st1v1v11wuvepjjnAfY9DtrlZ4Ig2zXUQb3aSD3r7ImSE6RUKkW6neYVBO/hA+xG9DSCORNU0h5ZvY7ngBjFWih+EdiYmkwdRiXO9UJ2bIjVyW0B9aG67IPgW6ZsL42gY1JMEPYhugjY9W4j9ahzTYyQRQuv8R2FPaYS1JOqmvY47EjC7rdyCvLdHJlu1QD0j+eJwrNAnA+3l/XHULVa3b8DE4SohgDq0UbqXeeaGAGMDp6HbAJyUyvCSpsNbLvfyrIPuqioyYqlbnhdOhHrj8GsQFl495htBB+2INSrjdSzzr4YAYwO3gOjy6ulI+0prJ9nxZuO4MbduEW6tbxQ7TonGbOxRd5xEnzxHXdcKyLOKgLu5XGOQhDq1UbqWWdfjABGB2+Cs+rUkbDS9usa8nA/RH6ODZ7A8B6sILA8eIeXELAH1Kub6BboPsh7y4H6CUI920hsRVBJAEulUiKKtbAsEGqto9YEah1orGeYwQl1pc0bmPZrnLyJsbWmtvAsJx1bU6rCHADAmjfbzQj41pLqWKCfIIRBPdsIUJ86+yKlHmwe3MSpUzcsXL6MhcuXQw0K0HbVVb7H4JCOITQ+85kMWD0JIXR1HuRFxeTC9HrVM+001guY1xhfP9avOhiHPktYlqdhj1ExeILGvKNHsd768RJMEZgguOmDHu+4mzi0v6jr7Ius+UQAkHK5fF2pVBLeRjII7gnQvCNMXPUkAFQrzes6BF0CpzttXvdQZGyO10Uc5KTHa+RhbNLDNpLnHWwz9HZX3v1YL2buvZV5lmqQidxeTohB6BeEercRZzmiqrMvouGwTgLAn8+coZZlkTD32WhtbcVf7N8PAEgmk3u6u7trKtydd965dFtf3/zi4iLOTE6GVq5PPv4YjY2NyOZy17P7QSmVmRDLa4CD0GP96EibN6WBCYkIQ1jflTkMe/oEsH5VBWCLSxhrPL0sjVrwrD/n2CCwJqJOEVCdBM5gAut++Nlvocs6jkMbYURVZ19EBbAfAHbt2hVuaWAHHzh//jwAoFwuf+F3/vvvv99y/vz50OPz7V7bp2RFMR7gOOw3pVME2MTUoFaQjrRHsd6SkWmIPHHow9oEaS+BiQO8aS1u648xwjl3GP6BJGpRSxB0LR+LQxtxEkWdfYmNF7itrQ3bk0kkGhqwe/fuT/fs2XNe5LpEIkE6OjouNDY1LW5PJrE9mYxzsFJeF4p5J4N6wlTT7oFtubm7Q2nIC5RXF5FXhqArX3QiYv0xeGG0ZCeN8/AKtKBTDOLQRpxEUeeaxCYe4MjICJ597jm2/4dwtJXbb789+/nnn3cBgGVZlFKKfC6HbAj7l2iAxTRzPyzDsBvXcah1CVm8Npm02fytAfAbv4pATXDKkAL/wdEe200R3uTtKdR+sIdgR4lxEtQKBLytIl3EoY24CbvONRESwCgsqhhbbVVosDCfhv2Gc7/lnJN3VdJkg/s60j4KdYEagfcD4zwnFmtBwfdW+1k1zCvsFvrDCL6y5yjU5xiKEIc2wksrzDp7ItQFppQSSilJplJIplJIh7hNZhwhhIDVnRCSZ/dDMbk0bMdAGBaQjrSHEOwh9rOe/P4fJV4rUkTuH68OvPRUGBIsgwpxaCNeaUbeK5AeAySEIEwvcBxxBVj9XFOyQ9ATBEFX2uOwo3ToaIS1uoL1nPTshmftiD7YXkIZNLyXsxxhCkK92wiP6EWQ7bkrcyQSiYsAqM7j1KlTe1XKwjt0l82+TXrK5nH0U0oPU0pPUjWGFdKeW/1umFLaI1hOXvm8zh3knHuyxvnDAmnL5O93yJaPd6SofR/d9Ggs6ygnHd7vHSQ/XW0k6joHPqRC4jO6urr+cPHixfulL6zB+Ph47z333HNWR1ru0P1BWb1ZZg9gg+EKIzbTYAwGgyFqlCxAg8FguBIwFqDBYNi0GAE0GAyblv8HfV9KGMi93IsAAAAASUVORK5CYII=")
BLUEBRIDGE_HTML = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#120f1c"><title>MC BlueBridge</title><style>
:root{--panel:#1b1628;--panel2:#241d35;--panel3:#2d2442;--text:#f4efff;--muted:#b7acca;--accent:#8b5cf6;--accent2:#a78bfa;--ok:#39d98a;--danger:#e16978;--border:#3b3055;--shadow:0 18px 50px rgba(0,0,0,.35)}*{box-sizing:border-box}html,body{margin:0;min-height:100%;background:radial-gradient(circle at top,#281d40,#120f1c 50%,#0b0911);color:var(--text);font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif}button,input,select{font:inherit}.shell{width:min(1180px,100%);margin:auto;padding:14px}.topbar{display:flex;align-items:center;justify-content:space-between;gap:12px;background:rgba(27,22,40,.96);border:1px solid var(--border);border-radius:18px;padding:11px 15px;box-shadow:var(--shadow)}.brand{display:flex;align-items:center;gap:11px}.brand img{width:58px}.brand h1{margin:0;font-size:1rem}.brand p{margin:3px 0 0;color:var(--muted);font-size:.76rem}.pill{display:inline-flex;align-items:center;gap:7px;padding:7px 10px;border:1px solid var(--border);border-radius:999px;background:var(--panel2);font-size:.78rem;font-weight:800}.dot{width:9px;height:9px;border-radius:50%;background:var(--danger)}.pill.ok .dot{background:var(--ok)}.nav{display:flex;gap:7px;margin:10px 0}.nav a{flex:1;text-align:center;text-decoration:none;color:var(--text);background:var(--panel);border:1px solid var(--border);border-radius:11px;padding:9px 5px;font-size:.8rem;font-weight:800}.nav a.active{background:var(--accent);border-color:var(--accent2)}.panel{background:rgba(27,22,40,.96);border:1px solid var(--border);border-radius:18px;box-shadow:var(--shadow);padding:15px;margin-bottom:12px}.btn{border:1px solid #5b4a7a;background:linear-gradient(180deg,#382c52,#251d37);color:var(--text);border-radius:10px;padding:9px 12px;font-weight:800;cursor:pointer;min-height:38px}.btn.primary{background:var(--accent);border-color:var(--accent2)}.btn.danger{background:#4a242e;border-color:#7c3b49}.btn.small{min-height:32px;padding:6px 9px;font-size:.74rem}.btn:disabled{opacity:.4;cursor:default}.subtle{color:var(--muted);font-size:.76rem;line-height:1.45}.controller-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}.controller-head h2{margin:3px 0 4px;font-size:1.3rem}.status-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:7px;margin-top:13px}.stat{background:#171222;border:1px solid var(--border);border-radius:10px;padding:9px}.stat span{display:block;color:var(--muted);font-size:.68rem}.stat strong{display:block;font-size:.8rem;margin-top:3px;word-break:break-word}.stat.action{cursor:pointer;transition:border-color .15s,background .15s}.stat.action:hover{border-color:var(--accent2);background:var(--panel2)}.under-card{display:flex;gap:8px;margin:-2px 0 12px}.under-card .btn{flex:1}.toolbar{display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap}.toolbar h2,.toolbar h3{margin:0}.profile-pills{display:flex;gap:7px;overflow:auto;padding:4px 0 9px}.profile-pill{border:1px solid var(--border);background:var(--panel2);color:var(--text);border-radius:999px;padding:8px 12px;white-space:nowrap;cursor:pointer}.profile-pill.active{background:var(--accent);border-color:var(--accent2)}.editor-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin:10px 0}.editor-head h2{margin:0}.actions{display:flex;gap:7px;flex-wrap:wrap}.tabs{display:flex;gap:6px;border-bottom:1px solid var(--border);padding-bottom:9px;margin-bottom:13px;overflow:auto}.tab{border:0;background:transparent;color:var(--muted);padding:8px 11px;border-radius:9px;font-weight:800;cursor:pointer;white-space:nowrap}.tab.active{background:var(--panel3);color:var(--text)}.tabpage{display:none}.tabpage.active{display:block}.surface{background:var(--panel2);border:1px solid var(--border);border-radius:14px;padding:14px;margin-bottom:10px}.surface h3{margin:0 0 5px}.notice{padding:11px 12px;background:#171222;border:1px solid var(--border);border-radius:11px;color:var(--muted);font-size:.76rem;line-height:1.45;margin-bottom:10px}.map-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.map-item{display:grid;grid-template-columns:minmax(95px,.8fr) minmax(130px,1.2fr) auto;align-items:center;gap:8px;padding:9px;background:#171222;border-radius:10px;border:1px solid transparent}.map-item.hit{border-color:var(--accent2)}select,input[type=text],input[type=number]{width:100%;background:#100d18;color:var(--text);border:1px solid var(--border);border-radius:10px;padding:9px}.form-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.form-group label{display:block;font-size:.76rem;font-weight:800;margin-bottom:5px}.switch-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:11px 12px;background:#171222;border-radius:10px;margin-bottom:10px}.switch{position:relative;width:46px;height:26px;flex:none}.switch input{opacity:0;width:0;height:0}.slider{position:absolute;inset:0;background:#4b405c;border-radius:999px}.slider:before{content:"";position:absolute;width:20px;height:20px;left:3px;top:3px;border-radius:50%;background:#fff;transition:.15s}.switch input:checked+.slider{background:var(--accent)}.switch input:checked+.slider:before{transform:translateX(20px)}.button-checks{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px}.check{display:flex;gap:6px;align-items:center;background:#171222;border-radius:9px;padding:8px;font-size:.75rem}.macro-card{background:#171222;border:1px solid var(--border);border-radius:12px;padding:12px;margin-bottom:9px}.macro-head{display:flex;justify-content:space-between;gap:10px;align-items:center}.macro-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px}.macro-output{margin-top:10px}.capture-select{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:7px}.paired-list{display:grid;gap:8px;margin-top:12px}.paired-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;align-items:center;background:var(--panel2);border:1px solid var(--border);border-radius:13px;padding:12px}.paired-row.connected{border-color:var(--accent2)}.paired-row h3{margin:0 0 4px;font-size:.92rem}.firmware-update{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;align-items:end;margin-top:12px}
.firmware-update .form-group{min-width:0}
.firmware-update #manualFirmwarePreview{grid-column:1/-1;margin:0;overflow-wrap:anywhere}
@media(max-width:560px){.firmware-update{grid-template-columns:minmax(0,1fr)}.firmware-update #firmwareUpdateBtn{justify-self:start}}.firmware-update input[type=file]{width:100%;background:#100d18;color:var(--text);border:1px solid var(--border);border-radius:10px;padding:8px}.firmware-status{margin-top:9px}.firmware-status.busy{color:var(--accent2)}.firmware-status.error{color:var(--danger)}.firmware-status.warning{color:#e7bd63}.maintenance-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}.maintenance-actions .btn{flex:1;min-width:180px}.search{margin-top:10px}.tester-buttons{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px}.test-key{padding:10px;background:#171222;border:1px solid var(--border);border-radius:10px;text-align:center;font-size:.75rem}.test-key.on{background:var(--accent);border-color:var(--accent2)}.analog-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:10px}.analog{background:#171222;border-radius:10px;padding:10px}.analog strong{display:block}.tester-banner{background:#2b2045;border:1px solid var(--accent2);border-radius:11px;padding:10px;margin-bottom:10px}.page{display:none}.page.active{display:block}.modal{display:none;position:fixed;inset:0;background:rgba(8,6,13,.82);z-index:100;align-items:center;justify-content:center;padding:20px}.modal.show{display:flex}.modal-card{width:min(430px,100%);background:var(--panel);border:1px solid var(--accent2);border-radius:18px;padding:20px;box-shadow:var(--shadow);text-align:center}.modal-card h3{margin-top:0}.footer{text-align:center;color:var(--muted);font-size:.72rem;padding:8px}.hidden{display:none!important}@media(max-width:800px){.status-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.map-grid,.form-grid,.macro-grid{grid-template-columns:1fr}.button-checks,.tester-buttons{grid-template-columns:repeat(2,minmax(0,1fr))}.analog-grid{grid-template-columns:1fr}.map-item{grid-template-columns:90px minmax(0,1fr)}.map-item .listen{grid-column:2}.controller-head,.editor-head{align-items:stretch;flex-direction:column}.controller-head .btn{width:100%}.nav a{font-size:.7rem;padding:8px 2px}.brand img{width:45px}.brand p{display:none}}
.btn.back{background:#493268;border-color:#c4a7ff;color:#fff;flex-shrink:0}.btn.back:hover{background:#5a3e80}.btn.back:focus-visible{outline:2px solid #fff;outline-offset:3px}.adapter-name{margin-top:15px;padding-top:15px;border-top:1px solid var(--border)}.diagnostics-panel summary{cursor:pointer;font-weight:700;padding:4px 0}.diagnostics-panel .diagnostics-controls{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}.diagnostics-panel pre{max-height:220px;overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere;font-size:.78rem}.diagnostics-panel .btn{min-height:36px;padding:7px 12px}.diagnostics-panel .diagnostics-details{margin-top:12px}</style></head><body><div class="shell"><header class="topbar"><div class="brand"><img src="/assets/logo.png" alt="MiSTer Companion"><div><h1>MC BlueBridge for Batocera</h1><p>Batocera v1.2.0</p></div></div><div id="connection" class="pill"><i class="dot"></i><span>Not detected</span></div></header>
<section id="adapterSelection" class="panel hidden"><label for="adapterSelector">Adapter to manage</label><select id="adapterSelector" onchange="selectAdapter(this.value)"></select></section><main id="overviewPage" class="page active"><section id="controllerModePanel" class="panel hidden"><label for="controllerMode">Controller mode</label><select id="controllerMode" onchange="controllerModeChanged()"><option value="0">Single controller</option><option value="1">Multi-controller (MiSTer only)</option></select><p class="subtle">Multi mode supports up to two controllers with profiles, mappings and rumble. Turbo and macros are disabled. May increase input latency. Changing mode restarts the adapter.</p><div id="multiControllerSelection" class="hidden"><label for="liveController">Connected controllers</label><select id="liveController" onchange="selectLiveController(this.value)"></select></div></section><section id="controllerCard" class="panel"><div class="controller-head"><div><div class="subtle">Current controller</div><h2 id="currentController">No controller connected</h2><div id="currentState" class="subtle">Turn on a paired controller normally, or start pairing to add one.</div></div><button id="disconnectBtn" class="btn hidden" onclick="disconnectController()">Disconnect</button></div><div class="status-grid"><div class="stat action" onclick="openFirmware()" role="button" tabindex="0"><span>Adapter firmware</span><strong id="firmware">-</strong></div><div class="stat"><span>Bluetooth</span><strong id="bluetooth">-</strong></div><div class="stat"><span>USB output</span><strong id="usbReady">-</strong></div><div class="stat"><span>Battery</span><strong id="battery">-</strong></div><div class="stat"><span>Output</span><select id="outputMode" onchange="outputChanged()"><optgroup label="MiSTer"><option value="1">MiSTer</option></optgroup><optgroup label="Computer"><option value="2">X-Input (BlueBridge)</option><option value="7" disabled>X-Input (X360) (requires firmware v2.0.0+)</option><option value="3">Generic HID</option><option value="6" disabled>DualSense (requires firmware v1.1.0+)</option></optgroup><optgroup label="Console"><option value="4">Nintendo Switch</option><option value="5">Xbox 360</option></optgroup></select></div><div class="stat"><span>Active profile</span><strong id="activeProfile">-</strong></div></div></section><div class="under-card"><button id="pairBtn" class="btn" onclick="pair(true)">Start Pairing</button><button class="btn" onclick="openPaired()">Paired Controllers</button><button class="btn" onclick="openBlocked()">Blocked Devices</button><button id="testerBtn" class="btn hidden" onclick="openTester()">Controller Tester</button><button class="btn" onclick="openFirmware()">BlueBridge Firmware</button><button class="btn" onclick="openDaemonSettings()">Daemon Settings</button></div>

<section id="controllerManagement" class="panel"><div class="toolbar"><div><h2 id="manageTitle">Profiles</h2><div id="manageState" class="subtle">Select a paired controller to manage its profiles.</div></div><button id="closeControllerBtn" class="btn small hidden" onclick="closeManagedController()">Close Controller</button></div><div id="outputOverridePanel" class="surface hidden"><h3>Controller USB output override</h3><label for="controllerOutputOverride">USB output</label><div class="capture-select"><select id="controllerOutputOverride"></select><button id="controllerOutputSave" class="btn" onclick="saveControllerOutput()">Save override</button></div></div><div id="profilePills" class="profile-pills"></div><div id="newProfileRow" class="capture-select"><input id="newProfile" type="text" maxlength="23" placeholder="New profile name"><button class="btn" onclick="createProfile()">Create</button></div><div id="editor" class="hidden"><div class="editor-head"><div><div id="crumb" class="subtle"></div><h2 id="profileTitle"></h2></div><div class="actions"><button id="activateBtn" class="btn small" onclick="activateCurrent()">Activate</button><button class="btn small" onclick="duplicateCurrent()">Duplicate</button><button id="deleteBtn" class="btn small danger" onclick="deleteCurrent()">Delete</button><button class="btn primary" onclick="saveProfile()">Save</button></div></div><div class="tabs"><button class="tab active" data-tab="mapping">Mapping</button><button class="tab" data-tab="analog">Analog</button><button class="tab" data-tab="turbo">Turbo</button><button class="tab" data-tab="macros">Macros</button><button id="touchMouseTab" class="tab hidden" data-tab="touchMousePanel">Touchpad &amp; Gyro</button><button id="lightbarTab" class="tab hidden" data-tab="lightbarPanel">Lightbar</button><button class="tab" data-tab="advanced">Advanced</button></div>
<div id="mapping" class="tabpage active"><div class="surface"><div class="toolbar"><div><h3>Controller mapping</h3><div class="subtle">Choose mappings from the list, or use the controller while it is connected.</div></div><button class="btn small" onclick="resetMapping()">Reset mapping</button><button id="sourceListen" class="btn small" onclick="captureMappingSource()">Press controller button</button></div><div id="mapGrid" class="map-grid"></div></div></div>
<div id="analog" class="tabpage"><div class="surface"><h3>Analog controls</h3><div class="form-grid"><div class="form-group"><label>Left stick deadzone (%)</label><input id="dzL" type="number" min="0" max="50"></div><div class="form-group"><label>Right stick deadzone (%)</label><input id="dzR" type="number" min="0" max="50"></div><div class="form-group"><label>Trigger deadzone (%)</label><input id="dzT" type="number" min="0" max="50"></div></div><div id="invertRows"></div></div></div>
<div id="turbo" class="tabpage"><div class="surface"><div class="switch-row"><div><strong>Turbo</strong><div class="subtle">Turn Turbo on or off without losing its configuration.</div></div><label class="switch"><input id="turboEnabled" type="checkbox"><span class="slider"></span></label></div><div class="form-group"><label>How Turbo is controlled</label><select id="turboMode" onchange="renderTurboHelp()"><option value="0">Button shortcut (modifier + target)</option><option value="1">Dedicated button - press to toggle</option><option value="2">Dedicated button - hold while using Turbo</option></select></div><div id="turboShortcut"><div class="form-group"><label>Shortcut modifier</label><div class="capture-select"><select id="turboModifier"></select><button class="btn small live-only" onclick="captureSelect('turboModifier','Choose Turbo modifier')">Press button</button></div></div><div id="shortcutHelp" class="notice"></div></div><div id="turboDedicated" class="hidden"><div class="form-group"><label>Dedicated Turbo control</label><div class="capture-select"><select id="turboControl"></select><button class="btn small live-only" onclick="captureSelect('turboControl','Choose Turbo control')">Press button</button></div></div></div><div class="form-group"><label>Turbo rate (Hz)</label><input id="turboRate" type="number" min="1" max="30"></div><div class="form-group"><label>Buttons that use Turbo</label><div id="turboButtons" class="button-checks"></div></div></div></div>
<div id="macros" class="tabpage"><div class="surface"><h3>Macros</h3><p class="subtle">Name the macro, choose what it sends, and assign the physical controller button that activates it. Disabling a macro preserves everything.</p><div id="macroList"></div></div></div>
<div id="touchMousePanel" class="tabpage hidden"><div class="surface">
<h2>DualShock 4 Touchpad and Gyro</h2>
<label><input id="touchMouseEnabled" type="checkbox" onchange="touchMouseDirty=true"> Use DS4 touchpad as a USB mouse</label>
<p class="subtle">Slide and press the DS4 touchpad. Requires single-controller MiSTer output. Other gamepad controls remain available.</p>
<div id="ds4RightClickSection" class="hidden">
<label><input id="ds4RightClickEnabled" type="checkbox" onchange="ds4RightClickDirty=true"> Enable right-click on the right half of the DS4 touchpad</label>
<p class="subtle">Off: the whole pad clicks the left mouse button. On: left half = left-click; right half = right-click. A held click keeps its button until release. Mouse output must also be enabled.</p>
<button id="ds4RightClickSave" class="btn" onclick="saveDS4RightClick()" disabled>Save right-click option</button>
<p id="ds4RightClickStatus" class="subtle" role="status"></p>
</div><fieldset id="ds4GyroPanel" class="hidden" disabled style="border:1px solid var(--border);border-radius:12px;padding:16px;margin:16px 0">
<legend>DS4 gyro mouse (experimental)</legend>
<label><input id="ds4GyroEnabled" type="checkbox"> Enable DS4 gyro mouse</label>
<div class="form-group"><label for="ds4GyroSensitivity">Sensitivity (%)</label><input id="ds4GyroSensitivity" type="number" min="1" max="200" value="100"></div>
<div class="form-group"><label for="ds4GyroActivation">Move the pointer</label><select id="ds4GyroActivation"><option value="1">While touching the touchpad</option><option value="2">While holding L2</option><option value="0">Whenever gyro is enabled</option></select></div>
<label><input id="ds4GyroInvertX" type="checkbox"> Invert horizontal movement</label>
<label><input id="ds4GyroInvertY" type="checkbox"> Invert vertical movement</label>
<label><input id="ds4GyroFire" type="checkbox"> Use R2 for mouse left-click / fire</label>
<div class="form-group"><label for="ds4GyroPause">Hold to pause and reposition</label><select id="ds4GyroPause"></select></div>
<p class="subtle">Mouse output above must also be enabled. Touchpad movement remains available. To zero resting drift, hold the pause button with the controller still for at least half a second. The pause button is reserved while gyro is enabled; optional R2 fire replaces gamepad R2. Settings apply after restart.</p>
</fieldset><p id="touchMouseStatus" class="subtle" role="status"></p>
<button id="touchMouseSave" class="btn primary" onclick="saveTouchMouse()" disabled>Save mouse setting and restart</button>
<p class="subtle">This adapter-wide setting applies to supported controllers and is off by default. Leave Controller Tester before checking movement in a mouse-capable core. The tester captures input and suppresses USB output.</p></div></div>
<div id="lightbarPanel" class="tabpage hidden"><div class="surface">
<h2>DualShock 4 Light Bar</h2>
<p class="subtle">The default palette applies to the adapter. Controller colours apply to the selected DualShock 4.</p>
<fieldset id="lightbarDefaults" disabled style="border:0;padding:0;margin:0">
<div class="form-group"><label for="lightbarTheme">Colour theme</label><select id="lightbarTheme" onchange="lightbarThemeChanged()"><option value="2">Nintendo — P1 red, P2 green</option><option value="1">Sega — P1 blue, P2 yellow/orange</option><option value="0">Custom</option></select></div>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:12px">
<label>P1 colour <input id="lightbarP1" type="color" value="#400000" oninput="lightbarColourChanged(0)"></label>
<label>P2 colour <input id="lightbarP2" type="color" value="#004000" oninput="lightbarColourChanged(1)"></label>
<label>P3 colour <input id="lightbarP3" type="color" value="#004000" oninput="lightbarColourChanged(2)"></label>
<label>P4 colour <input id="lightbarP4" type="color" value="#200020" oninput="lightbarColourChanged(3)"></label></div>
<p class="subtle">Themes set P1/P2 and retain your P3/P4 choices. Auto follows BlueBridge connection slots, not MiSTer player assignment. Each adapter currently supports two connected controllers.</p>
<button id="lightbarSavePalette" class="btn primary" onclick="saveLightbarPalette()">Save theme and colours</button>
</fieldset>
<fieldset id="lightbarController" class="hidden" disabled style="border:1px solid var(--border);border-radius:12px;padding:16px;margin:16px 0">
<legend id="lightbarControllerName">Controller colour</legend>
<div class="form-group"><label for="lightbarPlayer">Preset</label><select id="lightbarPlayer" onchange="lightbarControllerDirty=true"><option value="0">Auto — BlueBridge slot</option><option value="1">P1 colour</option><option value="2">P2 colour</option><option value="3">P3 colour</option><option value="4">P4 colour</option></select></div>
<label><input id="lightbarCustom" type="checkbox" onchange="lightbarControllerDirty=true;renderLightbar()"> Override with a custom colour</label>
<label>Custom colour <input id="lightbarCustomColour" type="color" value="#400000" oninput="lightbarControllerDirty=true"></label>
<p id="lightbarControllerStatus" class="subtle"></p>
<button id="lightbarSaveController" class="btn" onclick="saveLightbarController()">Save controller colour</button>
</fieldset>
<p id="lightbarStatus" class="subtle" role="status">Connect an adapter to read colours.</p>
<p class="subtle">Connected DS4 light bars update without a restart. Other controllers are unaffected. Rumble retains the selected colour.</p></div></div>
<div id="advanced" class="tabpage"><div class="surface"><h3>Profile</h3><div class="form-group"><label>Profile name</label><input id="profileName" type="text" maxlength="23"></div><div class="notice">Profiles are output-independent. Mapping, analog, Turbo and macros stay with the profile when the global output changes.</div></div><div id="misterSettings" class="surface"><h3>MiSTer mapping</h3><p class="subtle">This identity is only used in MiSTer mode and remains saved when another output is selected.</p><div class="form-group"><label>Mapping identity</label><select id="misterMapping"></select></div><div id="advancedGrid" class="status-grid"></div></div></div>
</div></section></main>
<main id="daemonPage" class="page"><section class="panel"><div class="toolbar"><h2>Batocera Daemon</h2><button class="btn back" onclick="showPage('overview')">Back</button></div><p class="subtle">Updates the management service running on your Batocera device. BlueBridge adapter firmware is managed separately.</p><div class="status-grid"><div class="stat"><span>Installed daemon</span><strong id="daemonInstalled">v1.2.0</strong></div><div class="stat"><span>Latest daemon</span><strong id="daemonLatest">Not checked</strong></div></div><p id="daemonUpdateStatus" class="subtle" role="status">Ready to check for Batocera daemon updates.</p><div class="actions"><button id="daemonCheck" class="btn" onclick="checkDaemonRelease()">Check daemon updates</button><button id="daemonInstall" class="btn primary" onclick="installDaemonUpdate()" disabled>Update Batocera daemon</button></div><h3>Daemon release notes</h3><pre id="daemonReleaseNotes" class="subtle" style="white-space:pre-wrap;overflow-wrap:anywhere"></pre></section></main>
<main id="firmwarePage" class="page"><section class="panel"><div class="toolbar"><div><h2>BlueBridge Firmware</h2><div class="subtle">Updates the connected BlueBridge adapter. Adapter name and saved configuration.</div></div><button class="btn back" onclick="showPage('overview')">Back</button></div><div class="status-grid"><div class="stat"><span>Installed firmware</span><strong id="firmwareInstalled">-</strong></div><div class="stat"><span>Configuration schema</span><strong id="firmwareSchema">-</strong></div></div><div class="adapter-name"><div class="toolbar"><div><h3>Adapter name</h3><strong id="adapterName">MC BlueBridge adapter</strong><p id="adapterNameHelp" class="subtle"></p></div><div class="actions"><button id="adapterRenameBtn" class="btn" onclick="renameAdapter()">Rename</button><button id="adapterResetNameBtn" class="btn" onclick="renameAdapter(true)">Reset name</button></div></div></div></section><section class="panel"><h2>Online Adapter Firmware Update</h2><p id="githubVersion" class="subtle">Check GitHub for an available firmware update.</p><div class="actions"><button id="githubCheck" class="btn" onclick="checkFirmwareRelease()">Check adapter firmware</button><button id="githubDownload" class="btn primary" onclick="downloadFirmware()" disabled>Update adapter firmware</button></div></section><section class="panel"><div class="toolbar"><div><h2>Manual Adapter Firmware Update</h2><div class="subtle">Install MC BlueBridge firmware from a local UF2 file.</div></div></div><div class="firmware-update">
<div class="form-group"><label for="firmwareFile">Choose UF2 File</label><input id="firmwareFile" type="file" accept=".uf2,application/octet-stream"></div>
<button id="firmwareUpdateBtn" class="btn primary" onclick="updateFirmware()">Update adapter firmware</button>
<p id="manualFirmwarePreview" class="subtle" role="status">Choose a local UF2 file to inspect its version.</p>
</div></section><section class="panel"><h2>Update Options &amp; Status</h2><div class="form-group"><label for="firmwareConfig">Configuration after either update</label><select id="firmwareConfig"><option value="preserve">Preserve Configuration (recommended)</option><option value="reset">Reset Configuration</option></select></div><div id="firmwareUpdateStatus" class="subtle firmware-status">Preserve Configuration keeps BlueBridge controller records, profiles, mappings, macros and settings. Reset Configuration starts BlueBridge with default settings and clears paired controllers.</div></section><section class="panel"><div class="toolbar"><div><h2>Configuration</h2><div class="subtle">Back up, restore or reset the complete BlueBridge configuration.</div></div></div><div class="maintenance-actions"><button class="btn" onclick="exportConfig()">Export Configuration</button><button class="btn" onclick="document.getElementById('importFile').click()">Import Configuration</button><button class="btn danger" onclick="resetConfiguration()">Reset Configuration</button><input id="importFile" type="file" accept=".bbconfig,application/json" hidden></div></section><section class="panel diagnostics-panel"><details id="diagnosticsPanel" ontoggle="diagnosticsToggled()"><summary>Diagnostics <span id="diagnosticsBadge" class="subtle"></span></summary><p class="subtle">Capture connection history for troubleshooting. Extra polling runs only during capture. History stays in memory until a new capture or daemon restart.</p><div class="diagnostics-controls"><button id="diagnosticsStart" class="btn" onclick="setDiagnosticsCapture(true)">Start capture</button><button id="diagnosticsStop" class="btn" onclick="setDiagnosticsCapture(false)" disabled>Stop capture</button><button id="diagnosticsDownload" class="btn" onclick="downloadDiagnostics()">Download diagnostics</button></div><div id="diagnosticsState" class="subtle" role="status">Capture stopped</div><details class="diagnostics-details"><summary>Connection details</summary><pre id="diagnosticsDetails">No capture yet.</pre></details></details></section></main>
<main id="pairedPage" class="page"><section class="panel"><div class="toolbar"><div><h2>Paired Controllers</h2><div class="subtle">Manage paired controllers and their stored profiles, even while they are offline.</div></div><button class="btn back" onclick="showPage('overview')">Back</button></div><input id="controllerSearch" class="search" type="text" placeholder="Search paired controllers" oninput="renderPaired()"><div id="pairedCount" class="subtle" style="margin-top:9px"></div><div id="pairedList" class="paired-list"></div></section></main><main id="blockedPage" class="page"><section class="panel"><div class="toolbar"><div><h2>Blocked Devices</h2><div class="subtle">Blocked Bluetooth devices are rejected before they can pair, reconnect, or use a controller slot.</div></div><button class="btn back" onclick="showPage('overview')">Back</button></div><div id="blockedCount" class="subtle" style="margin-top:9px"></div><div id="blockedList" class="paired-list"></div></section></main>
<main id="testerPage" class="page"><section class="panel"><div class="toolbar"><div><h2>Controller Tester</h2><div id="testerName" class="subtle"></div><label for="testerView">View</label><select id="testerView" onchange="changeTesterView()"><option value="raw">Raw input</option><option value="output">Remapped output</option></select></div><button class="btn" onclick="closeTester()">Done</button></div><div class="tester-banner"><strong>Testing mode is active.</strong><div class="subtle">Controller input is captured by BlueBridge and is not sent to the current USB output.</div></div><div class="status-grid"><div class="stat"><span>Battery</span><strong id="testBattery">-</strong></div><div class="stat"><span>D-Pad</span><strong id="testDpad">Neutral</strong></div><div class="stat"><span>Left trigger</span><strong id="testLT">0</strong></div><div class="stat"><span>Right trigger</span><strong id="testRT">0</strong></div></div><div class="surface" style="margin-top:10px"><h3>Buttons</h3><div id="testerButtons" class="tester-buttons"></div></div><div class="analog-grid"><div class="analog"><span class="subtle">Left stick</span><strong id="testLeft">X 0 / Y 0</strong></div><div class="analog"><span class="subtle">Right stick</span><strong id="testRight">X 0 / Y 0</strong></div><div class="analog"><span class="subtle">Rumble</span><div style="display:flex;gap:7px;margin-top:6px"><select id="rumbleStrength"><option value="64">25%</option><option value="128" selected>50%</option><option value="192">75%</option><option value="255">100%</option></select><button id="rumbleBtn" class="btn small" onclick="testRumble()">Test Rumble</button></div><div id="rumbleStatus" class="subtle" style="margin-top:5px"></div></div></div></section></main>
<div id="captureModal" class="modal"><div class="modal-card"><h3 id="captureTitle">Waiting for controller input</h3><p class="subtle">Press the controller button you want to use. The captured press and release will not be sent to the USB output.</p><button class="btn" onclick="cancelCapture()">Cancel</button></div></div><div class="footer">MC BlueBridge is managed locally through Companion Remote.</div></div><script>
let daemonRelease=null,daemonUpdating=false,daemonCheckBusy=false,daemonPoll=null,daemonDisconnected=false;
function renderAdapterName() {
  const supported=!!statusData.capabilities?.adapter_rename;
  $('adapterName').textContent=statusData.adapter_name||'MC BlueBridge adapter';
  $('adapterRenameBtn').disabled=!statusData.detected||!supported;
  $('adapterResetNameBtn').disabled=!statusData.detected||!supported||!statusData.adapter_custom_name;
  $('adapterNameHelp').textContent=supported?'The name is saved on this adapter. Changing it reconnects USB.':'Adapter naming requires newer BlueBridge firmware.';
}
async function renameAdapter(reset=false) {
  if(!statusData.capabilities?.adapter_rename)return;
  const name=reset?'':prompt('Adapter name (clear to restore MC BlueBridge adapter)',statusData.adapter_custom_name||'');
  if(name===null)return;
  const clean=name.trim();
  if(new TextEncoder().encode(clean).length>31||/[|\r\n]/.test(clean)){toast('Adapter name must be 31 bytes or fewer and contain no line breaks or |',true);return;}
  try{await post('/api/bluebridge/adapter/rename',{name:clean});await refresh();if(typeof discoverAdapters==='function')await discoverAdapters();renderAdapterName();toast(reset?'Adapter name reset':'Adapter name saved');}catch(e){toast(e.message,true);}
}
let selectedAdapterId='',adapterGeneration=0,adapterBusy=0,adapterActions=0,adapterSwitching=false,adapterDiscovery=null;
const adapterFetch=window.fetch.bind(window);
window.fetch=async(input,options={})=>{
  const url=new URL(typeof input==='string'?input:input.url,location.href);
  if(url.origin!==location.origin||!url.pathname.startsWith('/api/bluebridge/')||url.pathname==='/api/bluebridge/adapters')return adapterFetch(input,options);
  if(!selectedAdapterId)throw new Error('Select an MC BlueBridge adapter');
  const id=selectedAdapterId,generation=adapterGeneration;
  const headers=new Headers(options.headers||(typeof input!=='string'?input.headers:undefined));headers.set('X-BlueBridge-Adapter',id);
  adapterBusy++;if($('adapterSelector'))$('adapterSelector').disabled=true;
  try{const result=await adapterFetch(input,{...options,headers});if(generation!==adapterGeneration)throw new Error('Selected adapter changed');return result;}
  finally{adapterBusy--;$('adapterSelector').disabled=adapterBusy>0||adapterActions>0||adapterSwitching||firmwareUpdating;}
};
async function discoverAdapters() {
  if(adapterDiscovery)return adapterDiscovery;
  adapterDiscovery=(async()=>{
    const response=await adapterFetch('/api/bluebridge/adapters'),data=await response.json();
    if(!response.ok||data.ok===false)throw new Error(data.message||'Unable to discover adapters');
    const adapters=data.adapters||[],selector=$('adapterSelector');
    $('adapterSelection').classList.toggle('hidden',adapters.length<=1&&(!selectedAdapterId||!adapters.length||adapters.some(a=>a.id===selectedAdapterId)));
    if(!selectedAdapterId&&adapters.length)selectedAdapterId=adapters[0].id;
    const seen=new Map();for(const a of adapters)seen.set(a.name,(seen.get(a.name)||0)+1);
    selector.replaceChildren();
    if(selectedAdapterId&&!adapters.some(a=>a.id===selectedAdapterId))selector.append(new Option('Selected adapter disconnected',selectedAdapterId));
    for(const a of adapters){const duplicate=(seen.get(a.name)||0)>1;selector.append(new Option((a.name||'MC BlueBridge adapter')+(duplicate?' · '+a.id.slice(-6):''),a.id));}
    selector.value=selectedAdapterId;selector.disabled=adapterBusy>0||adapterActions>0||adapterSwitching||firmwareUpdating;
    return adapters;
  })();
  try{return await adapterDiscovery;}finally{adapterDiscovery=null;}
}
async function selectAdapter(id) {
  resetFirmwareRelease();
  if(adapterBusy||adapterActions||adapterSwitching||firmwareUpdating){$('adapterSelector').value=selectedAdapterId;return;}
  if(!id||id===selectedAdapterId)return;
  adapterSwitching=true;$('adapterSelector').disabled=true;
  try {
    captureRun++;if(testerTimer){clearInterval(testerTimer);testerTimer=null;}
    $('captureModal').classList.remove('show');
    if(selectedAdapterId){try{await post('/api/bluebridge/capture/stop');}catch(_) {}}
    selectedAdapterId=id;adapterGeneration++;
    statusData={};controllersData={controllers:[]};profilesData=null;profileData=null;currentController=-1;currentProfile=-1;offlineManagement=false;
    $('controllerManagement').classList.add('hidden');$('testerBtn').classList.add('hidden');$('disconnectBtn').classList.add('hidden');$('currentController').textContent='No controller connected';
    showPage('overview');setConnection(false);await refresh();
  }finally{adapterSwitching=false;$('adapterSelector').disabled=adapterBusy>0||adapterActions>0||firmwareUpdating;}
}

function resetMapping(){if(!profileData)return;profileData.map=Array.from({length:26},(_,i)=>i<16?i:22);renderMapping();renderMacros();toast('Default mapping restored. Save to apply.')}async function renameController(index,reset=false){if(!statusData.capabilities?.controller_rename)return;const c=controllerByIndex(index);if(!c)return;const name=reset?'':prompt('Controller name (clear to restore detected name)',c.custom_name||c.name);if(name===null)return;if(new TextEncoder().encode(name.trim()).length>31){toast('Controller name must be 31 bytes or fewer',true);return}try{await post('/api/bluebridge/controllers/rename',{index,name:name.trim()});await refresh();renderPaired();toast(reset?'Controller name reset':'Controller name saved')}catch(e){toast(e.message,true)}}function changeTesterView(){buildTesterButtons();applyTesterCapabilities();updateTester()}function testerOutput(){return $('testerView')?.value==='output'}
const $=id=>document.getElementById(id);let statusData={},controllersData={controllers:[]},blockedDevicesData={blocked_devices:[]},profilesData=null,profileData=null,currentController=-1,currentProfile=-1,captureRun=0,testerTimer=null,firmwareUpdating=false,offlineManagement=false,editorDirty=false,profileSaving=false;const sleep=ms=>new Promise(r=>setTimeout(r,ms));async function api(path,opt){const r=await fetch(path,opt);let j;try{j=await r.json()}catch(_){throw new Error(await r.text()||'Invalid response')};if(!r.ok||j.ok===false)throw new Error(j.message||'Request failed');return j}async function post(path,data={}){return api(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})}function toast(t,bad=false){let e=document.querySelector('.toast');if(!e){e=document.createElement('div');e.className='notice toast';e.style.cssText='position:fixed;right:18px;bottom:18px;z-index:200;max-width:340px';document.body.append(e)}e.textContent=t;e.style.borderColor=bad?'var(--danger)':'var(--accent2)';clearTimeout(e._t);e._t=setTimeout(()=>e.remove(),2600)}function showPage(name){for(const p of document.querySelectorAll('.page'))p.classList.remove('active');$(name+'Page').classList.add('active')}function controllerByIndex(i){return (controllersData.controllers||[]).find(c=>Number(c.index)===Number(i))}function selectedController(){return controllerByIndex(currentController)}function isSelectedLive(){const c=selectedController();return !!(c&&c.connected)}function labels(){return profilesData&&profilesData.labels?profilesData.labels:Array.from({length:26},(_,i)=>'Button '+(i+1))}function label(i){return labels()[i]||('Button '+(i+1))}function outputLabels(){return labels().slice(0,16)}function capabilities(){return profilesData&&profilesData.capabilities?profilesData.capabilities:{buttons:67108863,dpad:true,left_stick:true,right_stick:true,left_trigger:true,right_trigger:true}}function sourceButtonMask(){let m=Number(capabilities().buttons??67108863);if(isSelectedLive()&&Number(statusData.button_capabilities||0))m&=Number(statusData.button_capabilities);return m}function physicalButtons(){const m=sourceButtonMask();return labels().map((n,i)=>({n,i})).filter(x=>!!(m&(1<<x.i)))}function batteryText(st=statusData){if(!st.battery_supported)return 'Unavailable';const pct=Number(st.battery_percent||0)+'%';if(Number(st.battery_state)===2)return pct+' • Charging';if(Number(st.battery_state)===3)return '100% • Full';return pct}function setConnection(ok){if(!ok){statusData.detected=false;setDS4TabVisible('touchMouse',false);setDS4TabVisible('lightbar',false);}$('connection').classList.toggle('ok',ok);$('connection').querySelector('span').textContent=ok?'BlueBridge connected':'Not detected'}
async function refresh(){if(daemonUpdating)return;try{await discoverAdapters();if(!selectedAdapterId){statusData={};setConnection(false);renderAdapterName();return;}statusData=(await api('/api/bluebridge/status')).status||{};setConnection(!!statusData.detected);renderAdapterName();if(!statusData.detected)return;controllersData=(await api('/api/bluebridge/controllers')).controllers||{controllers:[]};try{blockedDevicesData=(await api('/api/bluebridge/blocked-devices')).blocked_devices||{blocked_devices:[]}}catch(_){blockedDevicesData={blocked_devices:[]}};if(currentController<0||!controllerByIndex(currentController))currentController=Number(controllersData.active??controllersData.connected_index??0);await loadProfiles(false);renderAll()}catch(e){if(e.message==='Selected adapter changed')return;setConnection(false);toast(e.message,true)}}
async function loadProfiles(force=true){try{profilesData=(await api('/api/bluebridge/profiles')).profiles||null;if(profilesData){currentController=Number(profilesData.controller_index);if(currentProfile<0||!(profilesData.profiles||[]).some(p=>Number(p.index)===currentProfile))currentProfile=Number(profilesData.active||0);if(force||!profileData||Number(profileData.index)!==currentProfile)profileData=(await api('/api/bluebridge/profile?index='+currentProfile)).profile||null}}catch(e){profilesData=null;profileData=null}}
function renderControllerMode(){const supported=typeof statusData.multi_controller==='boolean',multi=!!statusData.multi_controller;$('controllerModePanel').classList.toggle('hidden',!supported);$('controllerMode').value=(statusData.multi_controller_enabled??multi)?'1':'0';$('multiControllerSelection').classList.toggle('hidden',!multi);const sel=$('liveController');sel.innerHTML='';for(const c of controllersData.controllers||[])if(c.connected)sel.append(new Option(c.name,c.index));sel.value=String(currentController);sel.disabled=!sel.options.length;$('outputMode').disabled=multi&&!statusData.capabilities?.controller_output_override;for(const key of ['turbo','macros']){document.querySelector('.tab[data-tab="'+key+'"]').classList.toggle('hidden',multi);$(key).classList.toggle('hidden',multi);}if(multi&&document.querySelector('.tab.active')?.dataset.tab.match(/^(turbo|macros)$/))document.querySelector('.tab[data-tab="mapping"]').click();$('misterSettings').classList.toggle('hidden',multi||Number(statusData.output_mode)!==1);$('pairBtn').classList.toggle('hidden',false);$('pairBtn').disabled=!statusData.pairing&&(controllersData.controllers||[]).filter(c=>c.connected).length>=Number(statusData.max_connected||1);$('pairBtn').textContent=statusData.pairing?'Stop Pairing':'Start Pairing';}
async function controllerModeChanged(){const enabled=$('controllerMode').value==='1';if(!confirm('Change controller mode? The adapter will restart and connected controllers will disconnect. Saved profiles are preserved.')){$('controllerMode').value=(statusData.multi_controller_enabled??statusData.multi_controller)?'1':'0';return;}try{await post('/api/bluebridge/mode',{multi_controller:enabled});profileData=null;currentProfile=-1;editorDirty=false;toast('Adapter restarting');setTimeout(refresh,2000);}catch(e){$('controllerMode').value=(statusData.multi_controller_enabled??statusData.multi_controller)?'1':'0';toast(e.message,true);}}
async function selectLiveController(value){if(profileSaving)return;try{await post('/api/bluebridge/controllers/select',{index:Number(value)});currentController=Number(value);currentProfile=-1;profileData=null;editorDirty=false;offlineManagement=false;await refresh();}catch(e){toast(e.message,true);}}
function renderAll(){renderDualSenseAvailability();renderOutputOverride();renderDS4RightClick();renderDS4Settings();renderControllerCard();renderFirmware();renderProfiles();renderPaired();renderBlocked();if(profileData&&!editorDirty&&!profileSaving)renderEditor();renderControllerMode()}
function openFirmware(){showPage('firmware');renderFirmware()}function renderFirmware(){if($('firmwareInstalled'))$('firmwareInstalled').textContent=statusData.firmware?'v'+statusData.firmware:'-';if($('firmwareSchema'))$('firmwareSchema').textContent=statusData.config_schema??'-'}
function supportsDualSense(firmware) {
  const version = /^v?(\d+)\.(\d+)\.(\d+)(-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$/.exec(String(firmware ?? '').trim());
  if (!version) return false;
  const [, major, minor, patch, prerelease] = version;
  return Number(major) > 1 || (Number(major) === 1 &&
    (Number(minor) > 1 || (Number(minor) === 1 && (Number(patch) > 0 || !prerelease))));
}
function renderDualSenseAvailability() {
  const option = $('outputMode').querySelector('option[value="6"]');
  option.disabled = !supportsDualSense(statusData.firmware);
  option.textContent = 'DualSense' + (option.disabled ? ' (requires firmware v1.1.0+)' : '');
  for(const mode of [7]){const native=$('outputMode').querySelector('option[value="'+mode+'"]');native.disabled=!statusData.capabilities?.native_xinput_modes;native.textContent=outputNames[mode]+(native.disabled?' (requires firmware v2.0.0+)':'');}
}
function renderControllerCard(){renderDualSenseAvailability();const connected=controllerByIndex(controllersData.connected_index),managed=offlineManagement?selectedController():null;$('controllerCard').classList.remove('hidden');$('controllerManagement').classList.toggle('hidden',!(connected||managed));$('currentController').textContent=connected?connected.name:'No controller connected';$('currentState').textContent=connected?'Connected and ready for profile management':'Turn on a paired controller normally, or start pairing to add one.';$('disconnectBtn').classList.toggle('hidden',!connected);$('testerBtn').classList.toggle('hidden',!connected);$('pairBtn').classList.toggle('hidden',!!connected);$('firmware').textContent=statusData.firmware||'-';$('bluetooth').textContent=statusData.pairing?'Pairing':(statusData.bt_ready?(connected?'Connected':'Ready'):'Not ready');$('usbReady').textContent=statusData.usb_ready?'Ready':'Not ready';$('battery').textContent=connected?batteryText():'-';$('outputMode').value=String([1,2,3,4,5,6,7].includes(Number(statusData.output_mode))?Number(statusData.output_mode):1);$('activeProfile').textContent=connected?statusData.profile||'-':'-';$('pairBtn').textContent=statusData.pairing?'Stop Pairing':'Start Pairing';$('pairBtn').disabled=!statusData.pairing&&controllersData.controllers.filter(c=>c.connected).length>=Number(statusData.max_connected||1);$('pairBtn').onclick=()=>pair(!statusData.pairing)}
function renderProfiles(){const c=selectedController();$('closeControllerBtn').classList.toggle('hidden',!(offlineManagement&&c&&!c.connected));$('manageTitle').textContent=c?c.name+' Profiles':'Profiles';$('manageState').textContent=c?(c.connected?'Connected controller':'Paired • Offline — stored settings remain editable'):'Select a paired controller to manage its profiles.';$('profilePills').innerHTML='';for(const p of (profilesData&&profilesData.profiles)||[]){const b=document.createElement('button');b.className='profile-pill'+(Number(p.index)===currentProfile?' active':'');b.textContent=p.name;b.onclick=async()=>{if(profileSaving)return;editorDirty=false;currentProfile=Number(p.index);profileData=(await api('/api/bluebridge/profile?index='+currentProfile)).profile;renderAll()};$('profilePills').append(b)}$('newProfileRow').classList.toggle('hidden',!c);$('editor').classList.toggle('hidden',!profileData)}
function targetOptions(sel,value){sel.innerHTML='';const group=document.createElement('optgroup');group.label='Controller buttons';outputLabels().forEach((n,i)=>{const o=new Option(n,i);group.append(o)});sel.append(group);const mg=document.createElement('optgroup');mg.label='Macros';for(let i=0;i<4;i++){const m=profileData.macros[i]||{};mg.append(new Option((m.name||'Unnamed macro')+(m.enabled?'':' (disabled)'),16+i))}if(!statusData.multi_controller)sel.append(mg);const sg=document.createElement('optgroup');sg.label='Special';if(!statusData.multi_controller)sg.append(new Option('Turbo control',Number(profileData.turbo_control_mode)===2?21:20));sg.append(new Option('Disabled',22));sel.append(sg);if(statusData.multi_controller&&Number(value)>=16&&Number(value)<=21)sg.append(new Option('Saved special mapping (inactive in multi mode)',value));sel.value=String(value)}function buttonSelect(sel,value,allowNone=false){sel.innerHTML='';if(allowNone)sel.append(new Option('Not assigned',255));physicalButtons().forEach(({n,i})=>sel.append(new Option(n,i)));sel.value=String(value)}
function renderEditor(){$('crumb').textContent=(selectedController()?.name||'Controller')+' > '+profileData.name;$('profileTitle').textContent=profileData.name;$('activateBtn').classList.toggle('hidden',!isSelectedLive());$('deleteBtn').disabled=currentProfile===0;for(const e of document.querySelectorAll('.live-only'))e.classList.toggle('hidden',!isSelectedLive());renderMapping();renderAnalog();renderTurbo();renderMacros();renderAdvanced()}
function renderMapping(){const g=$('mapGrid');g.innerHTML='';physicalButtons().forEach(({n,i})=>{const row=document.createElement('div');row.className='map-item';row.dataset.input=i;const l=document.createElement('strong');l.textContent=n;const sel=document.createElement('select');sel.dataset.input=i;targetOptions(sel,profileData.map[i]);sel.onchange=()=>{profileData.map[i]=Number(sel.value);renderMacros()};const listen=document.createElement('button');listen.className='btn small listen live-only';listen.textContent='Press button';listen.onclick=()=>captureMappingDestination(i);if(!isSelectedLive())listen.classList.add('hidden');row.append(l,sel,listen);g.append(row)});$('sourceListen').classList.toggle('hidden',!isSelectedLive())}
function renderAnalog(){$('dzL').value=profileData.deadzone_left;$('dzR').value=profileData.deadzone_right;$('dzT').value=profileData.trigger_deadzone;const caps=capabilities();const inv=$('invertRows');inv.innerHTML='';[['Invert left stick X','invert_x','left_stick'],['Invert left stick Y','invert_y','left_stick'],['Invert right stick X','invert_rx','right_stick'],['Invert right stick Y','invert_ry','right_stick']].filter(x=>caps[x[2]]).forEach(([name,key])=>{const r=document.createElement('div');r.className='switch-row';r.innerHTML='<div><strong>'+name+'</strong></div><label class="switch"><input type="checkbox" '+(profileData[key]?'checked':'')+'><span class="slider"></span></label>';r.querySelector('input').onchange=e=>profileData[key]=e.target.checked;inv.append(r)})}
function makeChecks(root,mask,onchange){root.innerHTML='';physicalButtons().forEach(({n,i})=>{const l=document.createElement('label');l.className='check';const cb=document.createElement('input');cb.type='checkbox';cb.checked=!!(mask&(1<<i));cb.onchange=()=>onchange(i,cb.checked);l.append(cb,document.createTextNode(n));root.append(l)})}function makeOutputChecks(root,mask,onchange){root.innerHTML='';outputLabels().forEach((n,i)=>{const l=document.createElement('label');l.className='check';const cb=document.createElement('input');cb.type='checkbox';cb.checked=!!(mask&(1<<i));cb.onchange=()=>onchange(i,cb.checked);l.append(cb,document.createTextNode(n));root.append(l)})}
function renderTurbo(){$('turboEnabled').checked=!!profileData.turbo_enabled;$('turboMode').value=String(profileData.turbo_control_mode||0);buttonSelect($('turboModifier'),profileData.turbo_modifier??8);buttonSelect($('turboControl'),profileData.turbo_control_button??13);$('turboRate').value=profileData.turbo_rate_hz||12;makeOutputChecks($('turboButtons'),Number(profileData.turbo_mask||0),(i,on)=>{if(on)profileData.turbo_mask|=(1<<i);else profileData.turbo_mask&=~(1<<i)});renderTurboHelp()}function renderTurboHelp(){const mode=Number($('turboMode').value);$('turboShortcut').classList.toggle('hidden',mode!==0);$('turboDedicated').classList.toggle('hidden',mode===0);if(mode===0){const mod=label(Number($('turboModifier').value));$('shortcutHelp').textContent=mod+' + a controller button toggles Turbo for that button. The shortcut itself is consumed and is not sent to the output.'}}
function macroAssignment(m){const target=16+m;for(let i=0;i<(profileData.map||[]).length;i++)if(Number(profileData.map[i])===target)return i;return 255}function renderMacros(){const root=$('macroList');root.innerHTML='';for(let m=0;m<4;m++){const data=profileData.macros[m]||{enabled:false,name:'',output_mask:0};const card=document.createElement('div');card.className='macro-card';card.innerHTML='<div class="macro-head"><input class="macro-name" type="text" maxlength="15" placeholder="Macro name"><label class="switch"><input class="macro-enable" type="checkbox"><span class="slider"></span></label></div><div class="macro-grid"><div class="form-group"><label>Assigned controller button</label><div class="capture-select"><select class="macro-assign"></select><button class="btn small macro-listen live-only">Press button</button></div></div><div class="form-group"><label>Status</label><div class="notice macro-status" style="margin:0"></div></div></div><div class="macro-output"><label class="subtle">Buttons sent by this macro</label><div class="button-checks macro-checks"></div></div>';const name=card.querySelector('.macro-name'),en=card.querySelector('.macro-enable'),assign=card.querySelector('.macro-assign'),listen=card.querySelector('.macro-listen');name.value=data.name||'';en.checked=!!data.enabled;buttonSelect(assign,macroAssignment(m),true);if(!isSelectedLive())listen.classList.add('hidden');name.oninput=()=>data.name=name.value;en.onchange=()=>{data.enabled=en.checked;renderMapping()};assign.onchange=()=>setMacroAssignment(m,Number(assign.value));listen.onclick=()=>captureButton('Assign '+(name.value||'macro'),i=>setMacroAssignment(m,i));card.querySelector('.macro-status').textContent=macroAssignment(m)===255?'Not assigned':('Activated by '+label(macroAssignment(m)));makeOutputChecks(card.querySelector('.macro-checks'),Number(data.output_mask||0),(i,on)=>{if(on)data.output_mask|=(1<<i);else data.output_mask&=~(1<<i)});root.append(card)}}function setMacroAssignment(m,input){for(let i=0;i<profileData.map.length;i++)if(Number(profileData.map[i])===16+m)profileData.map[i]=i<16?i:22;if(input!==255)profileData.map[input]=16+m;renderMapping();renderMacros()}
function renderAdvanced(){$('profileName').value=profileData.name||'';$('outputMode').value=String([1,2,3,4,5,6,7].includes(Number(statusData.output_mode))?Number(statusData.output_mode):1);const misterMode=Number($('outputMode').value)===1;$('misterSettings').classList.toggle('hidden',!misterMode);const sel=$('misterMapping');sel.innerHTML='';sel.append(new Option('Separate MiSTer mapping','separate'));for(const p of profilesData.profiles||[])if(Number(p.index)!==currentProfile)sel.append(new Option('Share MiSTer mapping with '+p.name,'share:'+p.index));sel.value=profileData.mapping_mode==='shared'?'share:'+profileData.shared_with:'separate';const items=[['Controller',selectedController()?.name||'-'],['Native VID','0x'+Number(selectedController()?.native_vid||0).toString(16).padStart(4,'0').toUpperCase()],['Native PID','0x'+Number(selectedController()?.native_pid||0).toString(16).padStart(4,'0').toUpperCase()]];if(misterMode)items.push(['MiSTer virtual PID','0x'+Number(profileData.mister_identity||0).toString(16).padStart(4,'0').toUpperCase()]);const g=$('advancedGrid');g.innerHTML='';items.forEach(([a,b])=>{const d=document.createElement('div');d.className='stat';d.innerHTML='<span>'+a+'</span><strong>'+b+'</strong>';g.append(d)})}async function outputChanged(){const mode=Number($('outputMode').value);const previous=Number(statusData.output_mode)||1;if(mode===previous)return;if(mode===6&&!supportsDualSense(statusData.firmware)){$('outputMode').value=String(previous);toast('DualSense requires BlueBridge firmware v1.1.0 or later.',true);return}if(mode===6&&!confirm('DualSense presents your paired controller as a wired DualSense for compatible computer games and apps. PS5 console support is unavailable. Continue?')){$('outputMode').value=String(previous);return}if([5,7].includes(mode)&&!confirm(managementWarning)){$('outputMode').value=String(previous);return}try{await post('/api/bluebridge/output',{mode});statusData.output_mode=mode;statusData.output=outputNames[mode];if(profileData)renderAdvanced();toast([5,7].includes(mode)?'Output changed. USB management may disconnect; hold BOOTSEL for 5 seconds to recover.':'Output changed')}catch(e){$('outputMode').value=String([1,2,3,4,5,6,7].includes(Number(statusData.output_mode))?Number(statusData.output_mode):1);toast(e.message,true)}}
function collectProfileDraft(){const draft=JSON.parse(JSON.stringify(profileData));draft.name=$('profileName').value.trim()||draft.name;for(const sel of $('mapGrid').querySelectorAll('select[data-input]'))draft.map[Number(sel.dataset.input)]=Number(sel.value);for(const [id,key] of [['dzL','deadzone_left'],['dzR','deadzone_right'],['dzT','trigger_deadzone'],['turboRate','turbo_rate_hz'],['turboMode','turbo_control_mode'],['turboControl','turbo_control_button'],['turboModifier','turbo_modifier']])draft[key]=Number($(id).value);draft.turbo_enabled=$('turboEnabled').checked;return draft}
$('editor').addEventListener('input',()=>{editorDirty=true});$('editor').addEventListener('change',()=>{editorDirty=true});
async function saveProfile(){if(profileSaving)return;const idx=currentProfile;const draft=collectProfileDraft();const mv=$('misterMapping').value;const oldName=profileData.name;profileSaving=true;const controls=Array.from($('editor').querySelectorAll('input,select,button')).map(e=>[e,e.disabled]);for(const [e] of controls)e.disabled=true;try{const newName=draft.name;if(newName&&newName!==oldName){await post('/api/bluebridge/profiles/rename',{index:idx,name:newName});draft.name=newName}for(let i=0;i<draft.map.length;i++)await post('/api/bluebridge/profile/map',{profile:idx,input:i,output:Number(draft.map[i])});await post('/api/bluebridge/profile/tuning',{profile:idx,invert_x:!!draft.invert_x,invert_y:!!draft.invert_y,invert_rx:!!draft.invert_rx,invert_ry:!!draft.invert_ry,deadzone_left:draft.deadzone_left,deadzone_right:draft.deadzone_right,trigger_deadzone:draft.trigger_deadzone,turbo_enabled:draft.turbo_enabled,turbo_control_mode:draft.turbo_control_mode,turbo_control_button:draft.turbo_control_button,turbo_rate_hz:draft.turbo_rate_hz,turbo_mask:Number(draft.turbo_mask||0),turbo_modifier:draft.turbo_modifier});if(!statusData.multi_controller)for(let m=0;m<4;m++){const d=draft.macros[m];await post('/api/bluebridge/profile/macro',{profile:idx,macro:m,enabled:!!d.enabled,name:d.name||'',output_mask:Number(d.output_mask||0)})}if(!statusData.multi_controller&&mv==='separate')await post('/api/bluebridge/profile/mister-mapping',{profile:idx,mode:'separate'});else if(!statusData.multi_controller)await post('/api/bluebridge/profile/mister-mapping',{profile:idx,mode:'share',target:Number(mv.split(':')[1])});profileData=(await api('/api/bluebridge/profile?index='+idx)).profile;editorDirty=false;toast('Profile saved')}catch(e){editorDirty=true;toast(e.message,true)}finally{profileSaving=false;for(const [e,disabled] of controls)e.disabled=disabled;renderAll()}}
async function captureButton(title,onButton){if(!isSelectedLive()){toast('Controller must be connected to listen for input',true);return}const token=++captureRun;$('captureTitle').textContent=title;$('captureModal').classList.add('show');try{await post('/api/bluebridge/capture/start',{mode:'ONCE'});const end=Date.now()+10000;while(token===captureRun&&Date.now()<end){const raw=(await api('/api/bluebridge/capture/status')).capture||{};const c=testerOutput()&&raw.output?{...raw,...raw.output,dpad:[0,1,9,8,10,2,6,4,5][Number(raw.output.hat)||0]||0}:raw;if(c.ready){const i=Number(c.button);await post('/api/bluebridge/capture/stop');$('captureModal').classList.remove('show');captureRun++;onButton(i);return}await sleep(80)}if(token===captureRun){await post('/api/bluebridge/capture/stop');$('captureModal').classList.remove('show');captureRun++;toast('No controller button detected',true)}}catch(e){$('captureModal').classList.remove('show');captureRun++;toast(e.message,true)}}async function cancelCapture(){captureRun++;$('captureModal').classList.remove('show');try{await post('/api/bluebridge/capture/stop')}catch(_){}}function captureMappingSource(){captureButton('Choose the physical button to remap',i=>{const row=document.querySelector('.map-item[data-input="'+i+'"]');if(row){document.querySelectorAll('.map-item').forEach(r=>r.classList.remove('hit'));row.classList.add('hit');row.scrollIntoView({behavior:'smooth',block:'center'});row.querySelector('select').focus()}})}function captureMappingDestination(i){captureButton('Choose output for '+label(i),b=>{if(b>=16){toast('That control is an extended input and cannot be used as a direct output',true);return}profileData.map[i]=b;renderMapping();toast(label(i)+' → '+label(b))})}function captureSelect(id,title){captureButton(title,i=>{$(id).value=i;if(id==='turboModifier')renderTurboHelp();toast(label(i)+' selected')})}
async function pair(start){if(start&&statusData.pairing)start=false;try{await post('/api/bluebridge/pair',{start});toast(start?'Pairing started':'Pairing stopped');setTimeout(refresh,250)}catch(e){toast(e.message,true)}}async function disconnectController(){if(!confirm('Disconnect this controller? Pairing and profiles will be preserved.'))return;try{await post('/api/bluebridge/controllers/disconnect');offlineManagement=false;$('controllerManagement').classList.add('hidden');$('testerBtn').classList.add('hidden');$('disconnectBtn').classList.add('hidden');$('currentController').textContent='No controller connected';$('currentState').textContent='Turn on a paired controller normally, or start pairing to add one.';toast('Controller disconnected');setTimeout(refresh,450)}catch(e){toast(e.message,true)}}async function createProfile(){const name=$('newProfile').value.trim();if(!name)return;try{await post('/api/bluebridge/profiles/create',{name});$('newProfile').value='';profileData=null;await refresh()}catch(e){toast(e.message,true)}}async function activateCurrent(){try{await post('/api/bluebridge/profiles/select',{index:currentProfile});toast('Profile activated');setTimeout(refresh,300)}catch(e){toast(e.message,true)}}async function duplicateCurrent(){const name=prompt('Name for duplicated profile',(profileData?.name||'Profile')+' Copy');if(!name)return;try{await post('/api/bluebridge/profiles/duplicate',{index:currentProfile,name});profileData=null;await refresh()}catch(e){toast(e.message,true)}}async function deleteCurrent(){if(currentProfile===0||!confirm('Delete this profile?'))return;try{await post('/api/bluebridge/profiles/delete',{index:currentProfile});currentProfile=0;profileData=null;await refresh()}catch(e){toast(e.message,true)}}
async function closeManagedController(){if(profileSaving)return;editorDirty=false;if(!offlineManagement||isSelectedLive())return;try{controllersData=(await api('/api/bluebridge/controllers')).controllers||{controllers:[]};if(isSelectedLive()){renderAll();return}offlineManagement=false;currentController=-1;currentProfile=-1;profilesData=null;profileData=null;$('controllerManagement').classList.add('hidden');const connected=controllerByIndex(controllersData.connected_index);if(connected){await post('/api/bluebridge/controllers/select',{index:connected.index});currentController=Number(connected.index)}await refresh()}catch(e){toast(e.message,true)}}
function openPaired(){showPage('paired');renderPaired()}function openBlocked(){if(!statusData.capabilities?.device_blacklist){toast('Blocked device management requires newer BlueBridge firmware',true);return}showPage('blocked');renderBlocked()}function renderPaired(){const root=$('pairedList');if(!root)return;root.innerHTML='';const q=($('controllerSearch')?.value||'').toLowerCase();const list=(controllersData.controllers||[]).filter(c=>!q||String(c.name).toLowerCase().includes(q)||String(c.bluetooth_id||'').toLowerCase().includes(q));$('pairedCount').textContent=list.length+' paired controller'+(list.length===1?'':'s');for(const c of list){const r=document.createElement('div');r.className='paired-row'+(c.connected?' connected':'');r.innerHTML='<div><h3></h3><div class="subtle"></div></div><div class="actions"><button class="btn small manage">Manage</button><button class="btn small rename">Rename</button><button class="btn small reset-name">Reset name</button><button class="btn small danger block">Block</button><button class="btn small danger forget">Forget</button></div>';r.querySelector('h3').textContent=c.name;r.querySelector('.subtle').textContent=(c.connected?'Connected':'Offline')+' • '+c.profiles+' profile'+(c.profiles===1?'':'s')+' • Bluetooth ID: '+(c.bluetooth_id||'-');r.querySelector('.manage').onclick=()=>manageController(c.index);const rename=r.querySelector('.rename'),reset=r.querySelector('.reset-name'),block=r.querySelector('.block');rename.disabled=!statusData.capabilities?.controller_rename;rename.title=rename.disabled?'Update firmware to rename controllers':'';reset.disabled=rename.disabled||!c.custom_name;reset.title=rename.title;block.disabled=!statusData.capabilities?.device_blacklist||!c.bluetooth_id;block.onclick=()=>blockController(c);r.querySelector('.forget').onclick=()=>forgetController(c.index,c.name);root.append(r)}}function renderBlocked(){const root=$('blockedList');if(!root)return;root.innerHTML='';const list=(blockedDevicesData&&blockedDevicesData.blocked_devices)||[];$('blockedCount').textContent=list.length+' blocked device'+(list.length===1?'':'s');if(!list.length){const empty=document.createElement('div');empty.className='subtle';empty.textContent='No Bluetooth devices are blocked.';root.append(empty);return}for(const d of list){const r=document.createElement('div');r.className='paired-row';r.innerHTML='<div><h3></h3><div class="subtle"></div></div><div class="actions"><button class="btn small">Unblock</button></div>';r.querySelector('h3').textContent=d.name||'Bluetooth Device';r.querySelector('.subtle').textContent='Bluetooth ID: '+(d.id||'-');r.querySelector('button').onclick=()=>unblockDevice(d);root.append(r)}}async function blockController(c){if(!confirm('Block '+c.name+'?\n\nThe controller will be forgotten and this Bluetooth ID will remain blocked until you explicitly unblock it.'))return;try{await post('/api/bluebridge/blocked-devices/block',{id:c.bluetooth_id,name:c.name});if(currentController===Number(c.index)){currentController=-1;profileData=null}await refresh();renderPaired();renderBlocked();toast('Device blocked')}catch(e){toast(e.message,true)}}async function unblockDevice(d){if(!confirm('Unblock '+(d.name||d.id)+'? This device will be allowed to pair again.'))return;try{await post('/api/bluebridge/blocked-devices/unblock',{id:d.id});blockedDevicesData=(await api('/api/bluebridge/blocked-devices')).blocked_devices||{blocked_devices:[]};renderBlocked();toast('Device unblocked')}catch(e){toast(e.message,true)}}async function manageController(index){if(profileSaving)return;editorDirty=false;try{const c=controllerByIndex(index);await post('/api/bluebridge/controllers/select',{index});currentController=Number(index);offlineManagement=!!(c&&!c.connected);currentProfile=-1;profileData=null;await loadProfiles(true);showPage('overview');renderAll()}catch(e){toast(e.message,true)}}async function forgetController(index,name){if(!confirm('Forget '+name+' and delete its BlueBridge profiles?'))return;try{await post('/api/bluebridge/controllers/forget',{index});if(currentController===Number(index)){currentController=-1;profileData=null}await refresh();renderPaired()}catch(e){toast(e.message,true)}}
function applyTesterCapabilities(){const c=testerOutput()?{dpad:true,left_trigger:true,right_trigger:true,left_stick:true,right_stick:true}:capabilities();$('testDpad').parentElement.classList.toggle('hidden',!c.dpad);$('testLT').parentElement.classList.toggle('hidden',!c.left_trigger);$('testRT').parentElement.classList.toggle('hidden',!c.right_trigger);$('testLeft').parentElement.classList.toggle('hidden',!c.left_stick);$('testRight').parentElement.classList.toggle('hidden',!c.right_stick)}async function openTester(){const connected=controllerByIndex(controllersData.connected_index);if(!connected)return;try{if(currentController!==Number(connected.index)){await post('/api/bluebridge/controllers/select',{index:connected.index});currentController=Number(connected.index);await loadProfiles(true)}$('testerName').textContent=connected.name;$('testerView').value='raw';$('testerView').querySelector('[value=output]').disabled=!statusData.capabilities?.remapped_tester;$('testerView').title=statusData.capabilities?.remapped_tester?'':'Update firmware to test remapped output';buildTesterButtons();applyTesterCapabilities();showPage('tester');await post('/api/bluebridge/capture/start',{mode:'TESTER'});testerTimer=setInterval(updateTester,90);await updateTester()}catch(e){toast(e.message,true)}}function buildTesterButtons(){const root=$('testerButtons');root.innerHTML='';(testerOutput()?outputLabels().map((n,i)=>({n,i})):physicalButtons()).forEach(({n,i})=>{const d=document.createElement('div');d.className='test-key';d.dataset.button=i;d.textContent=n;root.append(d)})}async function updateTester(){try{const raw=(await api('/api/bluebridge/capture/status')).capture||{};const c=testerOutput()&&raw.output?{...raw,...raw.output,dpad:[0,1,9,8,10,2,6,4,5][Number(raw.output.hat)||0]||0}:raw;if(Number(c.mode||0)===0){clearInterval(testerTimer);testerTimer=null;showPage('overview');await refresh();toast('Controller disconnected');return}for(const e of $('testerButtons').children)e.classList.toggle('on',!!(Number(c.buttons)&(1<<Number(e.dataset.button))));const d=Number(c.dpad||0),ds=[];if(d&1)ds.push('Up');if(d&2)ds.push('Down');if(d&4)ds.push('Left');if(d&8)ds.push('Right');$('testDpad').textContent=ds.join(' + ')||'Neutral';$('testLT').textContent=String(c.lt??0);$('testRT').textContent=String(c.rt??0);$('testLeft').textContent='X '+(c.x??0)+' / Y '+(c.y??0);$('testRight').textContent='X '+(c.rx??0)+' / Y '+(c.ry??0);$('testBattery').textContent=c.battery_supported?(Number(c.battery_percent||0)+'%'):'Unavailable';$('rumbleBtn').disabled=!c.rumble_supported;$('rumbleStatus').textContent=c.rumble_supported?'Rumble supported':'Rumble is not available for this controller'}catch(e){clearInterval(testerTimer);testerTimer=null;toast(e.message,true)}}async function closeTester(){clearInterval(testerTimer);testerTimer=null;try{await post('/api/bluebridge/capture/stop')}catch(_){}showPage('overview');refresh()}async function testRumble(){try{await post('/api/bluebridge/rumble',{strength:Number($('rumbleStrength').value),duration:500});toast('Rumble test started')}catch(e){toast(e.message,true)}}
let releaseCheckBusy=false,firmwareRelease=null;
function resetFirmwareRelease(){firmwareRelease=null;$('githubVersion').textContent='Check GitHub for an available firmware update.';$('githubDownload').disabled=true;}
async function checkFirmwareRelease(){
  if(releaseCheckBusy||firmwareUpdating)return;
  releaseCheckBusy=true;$('githubCheck').disabled=true;$('githubDownload').disabled=true;
  $('githubVersion').textContent='Checking for updates…';
  try{
    const j=await api('/api/bluebridge/firmware/releases?force=1'),r=j.release||{};
    firmwareRelease=r;
    $('githubVersion').textContent=r.available?(r.update_available?'Update available: v':'Up to date. Latest available firmware: v')+r.version:(r.message||'Online firmware is not available yet. You can install a local UF2 file below.');
    $('githubDownload').disabled=!(r.available&&r.update_available);
  }catch(e){firmwareRelease=null;$('githubVersion').textContent='Unable to check for updates. Please try again later.';}
  finally{releaseCheckBusy=false;$('githubCheck').disabled=false;}
}
async function downloadFirmware(){
  if(firmwareUpdating||!firmwareRelease||!firmwareRelease.update_available)return;
  firmwareUpdating=true;$('githubCheck').disabled=true;$('githubDownload').disabled=true;$('firmwareUpdateBtn').disabled=true;
  const status=$('firmwareUpdateStatus');
  try{
    status.className='subtle firmware-status busy';status.textContent='Downloading and validating firmware…';
    const j=await post('/api/bluebridge/firmware/download'),info=j.firmware;
    const configuration=$('firmwareConfig').value,label=configuration==='preserve'?'Preserve Configuration':'Reset Configuration';
    if(!confirm('Install MC BlueBridge firmware?\n\nInstalled: v'+info.current_version+'\nNew: v'+info.version+'\nConfiguration: '+label+'\n\nBlueBridge will disconnect and restart.'+(info.relation==='same'?'\nThis version is already installed.':info.relation==='older'?'\nWarning: this is older firmware and may be incompatible with newer settings.':''))){await post('/api/bluebridge/firmware/cancel');status.className='subtle firmware-status';status.textContent='Firmware update cancelled.';return;}
    status.textContent='Installing firmware… BlueBridge will disconnect and restart.';
    const result=await post('/api/bluebridge/firmware/install',{configuration}),installed=result.firmware||{};
    status.className='subtle firmware-status'+(installed.state==='success'?'':' warning');
    status.textContent=installed.message||'Firmware installed';toast(status.textContent);
    profileData=null;resetFirmwareRelease();await refresh();renderFirmware();
  }catch(e){status.className='subtle firmware-status error';status.textContent=e.message;toast(e.message,true);}
  finally{firmwareUpdating=false;$('githubCheck').disabled=false;$('firmwareUpdateBtn').disabled=false;$('githubDownload').disabled=!(firmwareRelease&&firmwareRelease.update_available);}
}
async function inspectManualFirmware(){
  if(firmwareUpdating||releaseCheckBusy)return;
  const file=$('firmwareFile').files[0],preview=$('manualFirmwarePreview');
  if(!file){preview.textContent='Choose a local UF2 file to inspect its version.';return;}
  if(!/\.uf2$/i.test(file.name)){preview.textContent='Choose a .uf2 firmware file.';return;}
  firmwareUpdating=true;$('firmwareUpdateBtn').disabled=true;$('githubCheck').disabled=true;$('githubDownload').disabled=true;
  preview.textContent='Validating selected firmware…';
  try{
    const r=await fetch('/api/bluebridge/firmware/inspect',{method:'POST',headers:{'Content-Type':'application/octet-stream'},body:file}),j=await r.json();
    if(!r.ok||j.ok===false)throw new Error(j.message||'Firmware validation failed');
    const info=j.firmware;
    preview.textContent='Selected: v'+info.version+' · Installed: v'+info.current_version+(info.relation==='same'?' · This version is already installed.':info.relation==='older'?' · Warning: older firmware; newer settings may be incompatible.':'');
  }catch(e){preview.textContent=e.message;}
  finally{firmwareUpdating=false;$('firmwareUpdateBtn').disabled=false;$('githubCheck').disabled=false;$('githubDownload').disabled=!(firmwareRelease&&firmwareRelease.update_available);}
}
$('firmwareFile').onchange=guardAdapterAction(inspectManualFirmware);
async function updateFirmware(){if(firmwareUpdating||releaseCheckBusy)return;const input=$('firmwareFile'),file=input.files[0],button=$('firmwareUpdateBtn'),status=$('firmwareUpdateStatus');if(!file){toast('Choose an MC BlueBridge UF2 file first',true);return}if(!/\.uf2$/i.test(file.name)){toast('Choose a .uf2 firmware file',true);return}button.disabled=true;firmwareUpdating=true;status.className='subtle firmware-status busy';status.textContent='Validating firmware…';try{const r=await fetch('/api/bluebridge/firmware/inspect',{method:'POST',headers:{'Content-Type':'application/octet-stream'},body:file}),j=await r.json();if(!r.ok||j.ok===false)throw new Error(j.message||'Firmware validation failed');const info=j.firmware||{};if(info.relation==='same'){if(!confirm('Same firmware version detected.\n\nInstalled: v'+info.current_version+'\nUploaded: v'+info.version+'\n\nThis firmware version is already installed. Reinstall it anyway?')){status.className='subtle firmware-status';status.textContent='Firmware update cancelled.';return}}else if(info.relation==='older'){if(!confirm('Older firmware detected.\n\nInstalled: v'+info.current_version+'\nUploaded: v'+info.version+'\n\nSettings created by newer firmware may not be compatible with this version. Install the older version anyway?')){status.className='subtle firmware-status';status.textContent='Firmware update cancelled.';return}}const configuration=$('firmwareConfig').value,label=configuration==='preserve'?'Preserve Configuration':'Reset Configuration';if(!confirm('Ready to update MC BlueBridge.\n\nCurrent firmware: v'+info.current_version+'\nNew firmware: v'+info.version+'\nConfiguration: '+label+'\n\nBlueBridge will restart during the update. Continue?')){status.className='subtle firmware-status';status.textContent='Firmware update cancelled.';return}status.textContent='Installing firmware… BlueBridge will disconnect and restart.';const result=await post('/api/bluebridge/firmware/install',{configuration}),installed=result.firmware||{},state=installed.state||'success';input.value='';$('manualFirmwarePreview').textContent='Choose a local UF2 file to inspect its version.';resetFirmwareRelease();profileData=null;if(state==='success'){status.className='subtle firmware-status';status.textContent='Firmware updated successfully: v'+(installed.previous_version||info.current_version)+' → v'+(installed.version||info.version)+'.';toast('MC BlueBridge firmware updated')}else{status.className='subtle firmware-status warning';status.textContent=installed.message||'Firmware was installed, but post-update verification needs attention.';toast('Firmware installed with a warning')}await refresh();renderFirmware()}catch(e){status.className='subtle firmware-status error';status.textContent=e.message;toast(e.message,true)}finally{button.disabled=false;firmwareUpdating=false}}
async function exportConfig(){try{const r=await fetch('/api/bluebridge/config/export');if(!r.ok)throw new Error(await r.text());const b=await r.blob(),a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='MC-BlueBridge-Backup.bbconfig';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}catch(e){toast(e.message,true)}}async function resetConfiguration(){if(!confirm('Reset MC BlueBridge configuration?\n\nThis restores default settings and forgets all paired controllers. This cannot be undone unless you exported a backup.'))return;try{await post('/api/bluebridge/config/reset');profileData=null;currentController=-1;currentProfile=-1;toast('BlueBridge configuration reset');await refresh();renderFirmware()}catch(e){toast(e.message,true)}}$('importFile').onchange=async e=>{const f=e.target.files[0];if(!f)return;try{const r=await fetch('/api/bluebridge/config/import',{method:'POST',headers:{'Content-Type':'application/json'},body:await f.text()}),j=await r.json();if(!r.ok||j.ok===false)throw new Error(j.message||'Import failed');toast('Configuration imported');profileData=null;await refresh()}catch(e){toast(e.message,true)}finally{e.target.value=''}};document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.tabpage').forEach(x=>x.classList.remove('active'));b.classList.add('active');$(b.dataset.tab).classList.add('active')});window.addEventListener('beforeunload',()=>{if(testerTimer)navigator.sendBeacon('/api/bluebridge/capture/stop?adapter_id='+encodeURIComponent(selectedAdapterId),'{}')});function guardAdapterAction(work){return async function(...args){if(daemonUpdating){toast("Batocera daemon update is running. Please wait.",true);return;}adapterActions++;$('adapterSelector').disabled=true;try{return await work.apply(this,args);}finally{adapterActions--;$('adapterSelector').disabled=adapterBusy>0||adapterActions>0||adapterSwitching||firmwareUpdating;}};}
for(const name of ['renameAdapter','renameController','saveProfile','outputChanged','pair','disconnectController','closeManagedController','createProfile','activateCurrent','duplicateCurrent','deleteCurrent','manageController','forgetController','openTester','closeTester','testRumble','captureButton','updateFirmware','downloadFirmware','checkFirmwareRelease','exportConfig','resetConfiguration','setDiagnosticsCapture','downloadDiagnostics'])window[name]=guardAdapterAction(window[name]);
$('importFile').onchange=guardAdapterAction($('importFile').onchange);
let diagnosticsBusy=false,diagnosticsRefreshing=false,diagnosticsTimer=null;
function renderDiagnostics(data){
  const active=!!data.capturing;
  $('diagnosticsStart').disabled=active||diagnosticsBusy||!selectedAdapterId;
  $('diagnosticsStop').disabled=!active||diagnosticsBusy;
  $('diagnosticsDownload').disabled=diagnosticsBusy||!selectedAdapterId;
  $('diagnosticsBadge').textContent=active?'— Capturing':'';
  $('diagnosticsState').textContent=(active?'Capturing':'Capture stopped')+' · '+(data.event_count||0)+' events'+(data.error?' · '+data.error:'');
  $('diagnosticsDetails').textContent=JSON.stringify({connections:data.connections||[],last_failure:data.last_failure||null},null,2);
}
async function refreshDiagnostics(){
  if(diagnosticsBusy||diagnosticsRefreshing||!selectedAdapterId||!$('diagnosticsPanel').open)return;
  diagnosticsRefreshing=true;
  const adapter=selectedAdapterId;
  try{const result=await api('/api/bluebridge/diagnostics');if(selectedAdapterId===adapter){renderDiagnostics(result.diagnostics||{});}}
  catch(e){if(selectedAdapterId===adapter)$('diagnosticsState').textContent=e.message;}
  finally{diagnosticsRefreshing=false;}
}
function diagnosticsToggled(){
  if(diagnosticsTimer){clearInterval(diagnosticsTimer);diagnosticsTimer=null;}
  if($('diagnosticsPanel').open){refreshDiagnostics();diagnosticsTimer=setInterval(()=>{if(document.visibilityState==='visible')refreshDiagnostics();},2000);}
}
async function setDiagnosticsCapture(start){
  if(diagnosticsBusy||!selectedAdapterId)return;
  diagnosticsBusy=true;
  $('diagnosticsStart').disabled=$('diagnosticsStop').disabled=$('diagnosticsDownload').disabled=true;
  try{const result=await post('/api/bluebridge/diagnostics/'+(start?'start':'stop'));renderDiagnostics(result.diagnostics||{});}
  catch(e){toast(e.message,true);}
  finally{diagnosticsBusy=false;await refreshDiagnostics();}
}
async function downloadDiagnostics(){
  if(diagnosticsBusy||!selectedAdapterId)return;
  diagnosticsBusy=true;
  $('diagnosticsDownload').disabled=true;
  $('diagnosticsState').textContent='Preparing diagnostic download…';
  try{
    const result=await api('/api/bluebridge/diagnostics/report');
    const url=URL.createObjectURL(new Blob([JSON.stringify(result.report,null,2)],{type:'application/json'}));
    const a=document.createElement('a');a.href=url;a.download='BlueBridge-Diagnostics-'+new Date().toISOString().replace(/[:.]/g,'-')+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }catch(e){toast(e.message,true);}
  finally{diagnosticsBusy=false;await refreshDiagnostics();}
}
refresh();setInterval(()=>{if(document.visibilityState==='visible'&&!profileSaving&&!testerTimer&&!firmwareUpdating&&!$('captureModal').classList.contains('show'))refresh()},4000);
// BLUEBRIDGE_TOUCH_MOUSE
function setDS4TabVisible(name, visible){
  const tab=$(name+'Tab');
  if(!visible&&tab.classList.contains('active'))document.querySelector('.tab[data-tab="mapping"]').click();
  tab.classList.toggle('hidden',!visible);
  $(name+'Panel').classList.toggle('hidden',!visible);
}
function selectedDS4(){
  if(!statusData.detected)return null;
  const selected=selectedController();
  const controller=(offlineManagement||selected?.connected) ? selected : controllerByIndex(controllersData.connected_index);
  return Number(controller?.kind)===4?controller:null;
}
let ds4Selection='',touchMouseSaving=false,touchMouseDirty=false;
function renderDS4Settings(){
  const controller=selectedDS4();
  const key=controller?JSON.stringify([selectedAdapterId,controller.index,controller.id]):'';
  if(key!==ds4Selection){
    ds4Selection=key;
    touchMouseDirty=lightbarPaletteDirty=lightbarControllerDirty=false;
  }
  renderLightbar();
  renderTouchMouse();
}
function renderTouchMouse(){
  const supported=!!selectedDS4()&&!!statusData.capabilities?.touch_mouse;
  setDS4TabVisible('touchMouse',supported);
  renderDS4Gyro();
  const data=statusData.touch_mouse;
  $('touchMouseSave').disabled=!supported||!data||touchMouseSaving||(statusData.capabilities?.ds4_gyro&&!statusData.ds4_aim);
  if(!supported)return;
  if(!data){$('touchMouseEnabled').disabled=true;$('touchMouseStatus').textContent='Unable to read mouse settings. Refresh to retry.';return;}
  if(!touchMouseSaving&&!touchMouseDirty) $('touchMouseEnabled').checked=!!data.enabled;
  const eligible=!statusData.multi_controller&&Number(statusData.output_mode)===1&&data.available;
  $('touchMouseEnabled').disabled=touchMouseSaving;
  $('touchMouseStatus').textContent=!eligible
    ? 'Mouse output requires single-controller MiSTer mode. Your saved choice is retained.'
    : data.enabled!==data.active
      ? 'Setting saved. Waiting for the adapter to restart.'
      : data.active?'Mouse output is active. Exit Controller Tester to use it.':'Mouse output is off.';
}
async function saveTouchMouse(){
  if(touchMouseSaving||!selectedDS4()||!statusData.touch_mouse)return;
  touchMouseSaving=true;
  $('touchMouseSave').disabled=true;
  $('touchMouseEnabled').disabled=true;
  try{
    const payload=pointerPayload();
    const result=await post('/api/bluebridge/touch-mouse',payload);
    if(payload.ds4_aim)statusData.ds4_aim=payload.ds4_aim;
    touchMouseDirty=false;
    if(statusData.touch_mouse)statusData.touch_mouse.enabled=payload.enabled;
    toast(result.mouse?.restart_required?'Mouse setting saved. Adapter restarting…':'Mouse setting saved.');
    setTimeout(()=>refresh(),1500);
  }catch(e){toast(e.message,true);}
  finally{touchMouseSaving=false;renderTouchMouse();}
}
saveTouchMouse=guardAdapterAction(saveTouchMouse);

// BLUEBRIDGE_DS4_GYRO
function renderDS4Gyro(){
  const supported=!!selectedDS4()&&!!statusData.capabilities?.ds4_gyro,aim=statusData.ds4_aim;
  $('ds4GyroPanel').classList.toggle('hidden',!supported);
  $('ds4GyroPanel').disabled=!supported||!aim||touchMouseSaving;
  if(!supported||!aim||touchMouseDirty||touchMouseSaving)return;
  $('ds4GyroEnabled').checked=!!aim.enabled;$('ds4GyroSensitivity').value=String(aim.sensitivity);
  $('ds4GyroActivation').value=String(aim.activation);
  $('ds4GyroInvertX').checked=!!(aim.flags&1);$('ds4GyroInvertY').checked=!!(aim.flags&2);$('ds4GyroFire').checked=!!(aim.flags&4);
  const labels=['Cross','Circle','Square','Triangle','L1','R1','L2','R2','Share','Options','L3','R3','PS','Touchpad click'];
  $('ds4GyroPause').replaceChildren(new Option('None',255),...labels.map((name,i)=>new Option(name,i)));
  $('ds4GyroPause').value=String(aim.pause_button);
}
function pointerPayload(){
  const payload={enabled:$('touchMouseEnabled').checked};
  if(statusData.capabilities?.ds4_gyro){
    if(!statusData.ds4_aim)throw Error('Unable to read DS4 gyro settings. Refresh before saving.');
    const sensitivity=Number($('ds4GyroSensitivity').value);
    if(!Number.isInteger(sensitivity)||sensitivity<1||sensitivity>200)throw Error('Choose a whole-number sensitivity from 1 to 200%.');
    payload.ds4_aim={enabled:$('ds4GyroEnabled').checked,sensitivity,
      activation:Number($('ds4GyroActivation').value),pause_button:Number($('ds4GyroPause').value),
      flags:($('ds4GyroInvertX').checked?1:0)|($('ds4GyroInvertY').checked?2:0)|($('ds4GyroFire').checked?4:0)};
  }
  return payload;
}
$('ds4GyroPanel').addEventListener('input',()=>touchMouseDirty=true);
$('ds4GyroPanel').addEventListener('change',()=>touchMouseDirty=true);

// BLUEBRIDGE_DS4_LIGHTBAR
let lightbarSaving=false,lightbarPaletteDirty=false,lightbarControllerDirty=false,lightbarAdapter='',lightbarControllerId='';
function lightbarHex(rgb){return '#'+rgb.map(v=>Number(v).toString(16).padStart(2,'0')).join('');}
function lightbarRGB(hex){if(!/^#[0-9a-f]{6}$/i.test(hex))throw Error('Choose a valid colour.');return [1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));}
function lightbarThemeChanged(){
  const theme=Number($('lightbarTheme').value),colours={1:['#000040','#402000'],2:['#400000','#004000']}[theme];
  if(colours){$('lightbarP1').value=colours[0];$('lightbarP2').value=colours[1];}
  lightbarPaletteDirty=true;
}
function lightbarColourChanged(player){if(player<2)$('lightbarTheme').value='0';lightbarPaletteDirty=true;}
function renderLightbar(){
  if(lightbarAdapter!==selectedAdapterId){lightbarAdapter=selectedAdapterId;lightbarPaletteDirty=lightbarControllerDirty=false;lightbarControllerId='';}
  const supported=!!selectedDS4()&&!!statusData.capabilities?.ds4_lightbar,data=statusData.lightbar;
  setDS4TabVisible('lightbar',supported);
  $('lightbarDefaults').disabled=!supported||!data||lightbarSaving;
  if(!supported)return;
  if(!data){$('lightbarStatus').textContent='Unable to read light-bar settings. Refresh to retry.';$('lightbarController').classList.add('hidden');return;}
  if(!lightbarPaletteDirty&&!lightbarSaving){$('lightbarTheme').value=String(data.theme);data.players.forEach((rgb,i)=>$('lightbarP'+(i+1)).value=lightbarHex(rgb));}
  const c=selectedDS4(),choice=c&&data.controllers.find(x=>Number(x.index)===Number(c.index)&&Number(x.id)===Number(c.id));
  const key=c?String(c.id)+':'+c.index:'';
  if(key!==lightbarControllerId){lightbarControllerId=key;lightbarControllerDirty=false;}
  const ds4=Number(c?.kind)===4;
  $('lightbarController').classList.toggle('hidden',!ds4||!choice);
  $('lightbarController').disabled=lightbarSaving||!choice;
  if(ds4&&choice){
    $('lightbarControllerName').textContent=c.name+' colour';
    if(!lightbarControllerDirty&&!lightbarSaving){$('lightbarPlayer').value=String(choice.player);$('lightbarCustom').checked=!!choice.custom_enabled;$('lightbarCustomColour').value=lightbarHex(choice.rgb);}
    $('lightbarCustomColour').disabled=!$('lightbarCustom').checked||lightbarSaving;
    $('lightbarPlayer').disabled=$('lightbarCustom').checked||lightbarSaving;
    $('lightbarControllerStatus').textContent=c.connected?'Connected on BlueBridge slot '+(Number(c.slot)+1)+'.':'Saved choice will apply when this DS4 connects.';
  }
  $('lightbarStatus').textContent=lightbarPaletteDirty||lightbarControllerDirty?'Unsaved colour changes.':'Colours are saved on the adapter.';
}
async function saveLightbarPalette(){
  if(lightbarSaving||!selectedDS4())return;lightbarSaving=true;renderLightbar();
  try{
    const result=await post('/api/bluebridge/lightbar/palette',{theme:Number($('lightbarTheme').value),players:[1,2,3,4].map(i=>lightbarRGB($('lightbarP'+i).value))});
    statusData.lightbar=result.lightbar;lightbarPaletteDirty=false;toast('Theme and colours saved.');
  }catch(e){toast(e.message,true);}finally{lightbarSaving=false;renderLightbar();}
}
async function saveLightbarController(){
  if(lightbarSaving)return;const c=selectedDS4();if(!c)return;
  lightbarSaving=true;renderLightbar();
  try{
    const result=await post('/api/bluebridge/lightbar/controller',{index:Number(c.index),id:Number(c.id),player:Number($('lightbarPlayer').value),custom_enabled:$('lightbarCustom').checked,rgb:lightbarRGB($('lightbarCustomColour').value)});
    statusData.lightbar=result.lightbar;lightbarControllerDirty=false;toast('Controller colour saved.');
  }catch(e){toast(e.message,true);}finally{lightbarSaving=false;renderLightbar();}
}
saveLightbarPalette=guardAdapterAction(saveLightbarPalette);
saveLightbarController=guardAdapterAction(saveLightbarController);
const outputNames={1:'MiSTer',2:'X-Input (BlueBridge)',3:'Generic HID',4:'Nintendo Switch',5:'Xbox 360',6:'DualSense',7:'X-Input (X360)'};
const managementWarning='On some devices, this mode may lose the USB serial connection, so BlueBridge management will be unavailable. Hold BOOTSEL for 5 seconds to disconnect all controllers and return to MiSTer mode. Saved output overrides are preserved and apply again when the controller reconnects. Continue?';
let outputOverrideTarget='',outputOverrideSaved=0,outputOverrideSaving=false;
function renderOutputOverride(){
  const c=selectedController(),supported=!!statusData.capabilities?.controller_output_override;
  $('outputOverridePanel').classList.toggle('hidden',!supported||!c);
  if(!supported||!c){outputOverrideTarget='';return;}
  const target=JSON.stringify([selectedAdapterId,c.index,c.id]),saved=Number(c.output_override||0),select=$('controllerOutputOverride');
  if(!select.options.length){select.append(new Option('Default (adapter output)',0));for(const group of $('outputMode').querySelectorAll('optgroup'))select.append(group.cloneNode(true));}
  if(target!==outputOverrideTarget||Number(select.value)===outputOverrideSaved)select.value=String(saved);
  outputOverrideTarget=target;outputOverrideSaved=saved;
  for(const option of select.options){const mode=Number(option.value);if(!mode)continue;const source=$('outputMode').querySelector('option[value="'+mode+'"]');option.disabled=source.disabled;option.textContent=source.textContent;}
  select.disabled=outputOverrideSaving;$('controllerOutputSave').disabled=outputOverrideSaving;
}
async function saveControllerOutput(){
  const c=selectedController();if(!c||outputOverrideSaving||!statusData.capabilities?.controller_output_override)return;
  const target=JSON.stringify([selectedAdapterId,c.index,c.id]);if(target!==outputOverrideTarget)return;
  const mode=Number($('controllerOutputOverride').value);
  if([5,7].includes(mode)&&!confirm('This override applies on the next controller connection. '+managementWarning))return;
  outputOverrideSaving=true;renderOutputOverride();
  try{await post('/api/bluebridge/controllers/output',{index:c.index,id:c.id,mode});
    if(target!==outputOverrideTarget)return;c.output_override=mode;outputOverrideSaved=mode;
    toast('Output override saved. It applies when the controller reconnects.');
  }catch(e){toast(e.message,true);}finally{outputOverrideSaving=false;renderOutputOverride();}
}

let ds4RightClickDirty=false,ds4RightClickSaving=false,ds4RightClickSelection='';
function renderDS4RightClick(){
  const controller=selectedDS4();
  const key=JSON.stringify([selectedAdapterId,controller?.index,controller?.id]);
  if(key!==ds4RightClickSelection){ds4RightClickSelection=key;ds4RightClickDirty=false;}
  const supported=!!controller&&!!statusData.capabilities?.ds4_right_click;
  const data=statusData.ds4_mouse;
  $('ds4RightClickSection').classList.toggle('hidden',!supported);
  $('ds4RightClickEnabled').disabled=!supported||!data||ds4RightClickSaving;
  $('ds4RightClickSave').disabled=!supported||!data||ds4RightClickSaving;
  if(!supported)return;
  if(!data){$('ds4RightClickStatus').textContent='Unable to read right-click setting. Refresh to retry.';return;}
  if(!ds4RightClickDirty&&!ds4RightClickSaving)$('ds4RightClickEnabled').checked=!!data.right_click;
  $('ds4RightClickStatus').textContent=data.right_click?'Right-click is enabled.':'Right-click is off; the whole touchpad clicks left.';
}
async function saveDS4RightClick(){
  if(ds4RightClickSaving||!selectedDS4()||!statusData.ds4_mouse)return;
  const adapter=selectedAdapterId;
  ds4RightClickSaving=true;renderDS4RightClick();
  try{
    const result=await post('/api/bluebridge/ds4-mouse',{right_click:$('ds4RightClickEnabled').checked});
    if(selectedAdapterId!==adapter)return;
    statusData.ds4_mouse=result.settings;ds4RightClickDirty=false;
    toast('Right-click option saved. Release any held click to use the new setting.');
  }catch(e){toast(e.message,true);}finally{ds4RightClickSaving=false;renderDS4RightClick();}
}
saveDS4RightClick=guardAdapterAction(saveDS4RightClick);

saveControllerOutput=guardAdapterAction(saveControllerOutput);


function renderDaemonButtons(){
  $('daemonCheck').disabled=daemonUpdating||daemonCheckBusy||firmwareUpdating;
  $('daemonInstall').disabled=daemonUpdating||daemonCheckBusy||firmwareUpdating||!daemonRelease?.update_available;
}
async function openDaemonSettings(){showPage('daemon');await pollDaemonUpdate();}
async function checkDaemonRelease(){
  if(daemonUpdating||daemonCheckBusy||firmwareUpdating)return;
  daemonCheckBusy=true;renderDaemonButtons();$('daemonUpdateStatus').textContent='Checking Batocera daemon releases…';
  try{daemonRelease=(await api('/api/daemon/releases')).release;
    $('daemonLatest').textContent='v'+daemonRelease.version;
    $('daemonReleaseNotes').textContent=daemonRelease.notes||'No release notes provided.';
    $('daemonUpdateStatus').textContent=daemonRelease.update_available?'A Batocera daemon update is available.':'Batocera daemon is up to date.';
  }catch(e){daemonRelease=null;$('daemonUpdateStatus').textContent='Unable to check daemon updates: '+e.message;}
  finally{daemonCheckBusy=false;renderDaemonButtons();}
}
function scheduleDaemonPoll(){clearTimeout(daemonPoll);daemonPoll=setTimeout(pollDaemonUpdate,1500);}
async function pollDaemonUpdate(){
  try{const data=(await api('/api/daemon/status')).update;
    $('daemonInstalled').textContent='v'+data.installed;
    daemonUpdating=!!data.busy;
    $('daemonUpdateStatus').textContent=data.message+(data.state==='downloading'&&data.percent!=null?' '+data.percent+'%':'');
    $('daemonUpdateStatus').classList.toggle('error',data.state==='error');
    if(!daemonUpdating&&data.state==='success'){
      daemonRelease=null;
      if(data.installed!=='1.2.0'){location.reload();return;}
    }
    if(daemonUpdating)scheduleDaemonPoll();
    else if(daemonDisconnected){daemonDisconnected=false;await refresh();}
  }catch(e){
    if(daemonUpdating){daemonDisconnected=true;$('daemonUpdateStatus').textContent='Waiting for the Batocera daemon to reconnect…';scheduleDaemonPoll();}
    else $('daemonUpdateStatus').textContent='Unable to read daemon update status: '+e.message;
  }
  renderDaemonButtons();
}
async function installDaemonUpdate(){
  if(daemonUpdating||firmwareUpdating||!daemonRelease?.update_available)return;
  if(!confirm('Install Batocera daemon v'+daemonRelease.version+'? Management will briefly disconnect while the service restarts. Saved settings are preserved. Adapter firmware will not be changed.'))return;
  daemonUpdating=true;renderDaemonButtons();
  $('daemonUpdateStatus').textContent='Starting Batocera daemon update…';
  try{await post('/api/daemon/update',{version:daemonRelease.version});scheduleDaemonPoll();}
  catch(e){
    // A service restart can close this request after the update has started.
    try{const data=(await api('/api/daemon/status')).update;daemonUpdating=!!data.busy;
      $('daemonUpdateStatus').textContent=data.busy?data.message:e.message;
      if(daemonUpdating)scheduleDaemonPoll();
    }catch(_){daemonDisconnected=true;scheduleDaemonPoll();}
    renderDaemonButtons();
  }
}
pollDaemonUpdate();

</script></body></html>'''.encode("utf-8")


def send_http(sock, status, content_type, body, extra_headers=None):
    if isinstance(body, str):
        body = body.encode('utf-8')
    try:
        sock.settimeout(None)
    except Exception:
        pass
    headers = ['HTTP/1.1 %s' % status, 'Content-Type: %s' % content_type, 'Content-Length: %d' % len(body), 'Cache-Control: no-store', 'X-Content-Type-Options: nosniff', 'Connection: close']
    if extra_headers:
        headers.extend(extra_headers)
    sock.sendall(('\r\n'.join(headers) + '\r\n\r\n').encode('ascii'))
    view = memoryview(body)
    offset = 0
    chunk_size = 64 * 1024
    while offset < len(view):
        end = min(offset + chunk_size, len(view))
        sock.sendall(view[offset:end])
        offset = end

class BlueBridgeDiagnostics:
    def __init__(self, adapter_id):
        self.lock = threading.RLock()
        self.adapter_id = adapter_id
        self.active = False
        self.started = None
        self.sequence = 0
        self.events = collections.deque(maxlen=1500)
        self.connections = {}
        self.failures = {}
        self.current = None
        self.last_failure = None
        self.error = ""
        self.thread = None
        self.stop = threading.Event()

    def record(self, kind, value):
        with self.lock:
            if not self.active:
                return
            self.sequence += 1
            self.events.append({"sequence": self.sequence, "time": datetime.datetime.now().astimezone().isoformat(timespec="milliseconds"), "adapter": self.adapter_id, "kind": kind, "value": value})

    def snapshot(self, value, selected=False):
        with self.lock:
            key = str(value.get("slot", 0))
            if self.connections.get(key) != value:
                self.record("bluetooth", value)
            self.connections[key] = dict(value)
            if selected:
                self.current = dict(value)
            if value.get("failed_stage") not in (None, "", "none") or value.get("status", -1) > 0:
                if self.failures.get(key) != value:
                    self.failures[key] = dict(value)
                    self.last_failure = dict(value)

    def summary(self):
        with self.lock:
            return {"capturing": self.active, "started": self.started, "event_count": len(self.events), "connections": list(self.connections.values()), "last_failure": self.last_failure, "error": self.error}

    def report(self):
        with self.lock:
            return json.loads(json.dumps({"app": "MC BlueBridge Batocera " + DAEMON_VERSION, "host": platform.platform(), "adapter_id": self.adapter_id, "capturing": self.active, "started": self.started, "connections": list(self.connections.values()), "connection_failures": list(self.failures.values()), "current": self.current, "last_failure": self.last_failure, "events": list(self.events), "diagnostic_error": self.error}))

    def start(self, manager):
        with self.lock:
            if self.active:
                return
            if self.thread is not None and self.thread.is_alive():
                raise RuntimeError("Previous capture is stopping; try again shortly")
            self.events.clear()
            self.connections.clear()
            self.failures.clear()
            self.sequence = 0
            self.current = self.last_failure = None
            self.error = ""
            self.started = datetime.datetime.now().astimezone().isoformat(timespec="milliseconds")
            self.stop.clear()
            self.active = True
            self.thread = threading.Thread(target=self._worker, args=(manager,), daemon=True)
            self.thread.start()

    def finish(self):
        with self.lock:
            self.active = False
            self.stop.set()

    def _worker(self, manager):
        while not self.stop.is_set():
            if manager.lock.acquire(blocking=False):
                try:
                    manager.sample_diagnostics()
                    with self.lock:
                        self.error = ""
                except Exception as error:
                    with self.lock:
                        self.error = str(error)
                    self.record("diagnostic_error", str(error))
                finally:
                    manager.lock.release()
            self.stop.wait(2.0)


class BlueBridgeManager:
    def __init__(self, adapter_id=None):
        self.lock = threading.RLock()
        self.adapter_id = adapter_id
        self.adapter_name = "MC BlueBridge adapter"
        self.verified = False
        self.path = None
        self.fd = None
        self.rx = b""
        self.counter = 0
        self.info = {}
        self.diagnostics = BlueBridgeDiagnostics(adapter_id)

    def _read_text(self, path):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()
        except Exception:
            return ""

    def _usb_info(self, tty_path):
        name = os.path.basename(tty_path)
        node = os.path.realpath("/sys/class/tty/%s/device" % name)
        info = {"path": tty_path, "product": "", "manufacturer": "", "serial": "", "vendor": "", "product_id": ""}
        seen = set()
        while node and node not in seen and node != "/":
            seen.add(node)
            if not info["product"]:
                info["product"] = self._read_text(os.path.join(node, "product"))
            if not info["manufacturer"]:
                info["manufacturer"] = self._read_text(os.path.join(node, "manufacturer"))
            if not info["serial"]:
                info["serial"] = self._read_text(os.path.join(node, "serial"))
            if not info["vendor"]:
                info["vendor"] = self._read_text(os.path.join(node, "idVendor"))
                if info["vendor"]:
                    info["usb_path"] = node
            if not info["product_id"]:
                info["product_id"] = self._read_text(os.path.join(node, "idProduct"))
            node = os.path.dirname(node)
        return info

    @staticmethod
    def identity(info):
        return info.get("serial") or "usb:" + os.path.basename(info.get("usb_path", info["path"]))

    def discover_all(self):
        found = []
        candidates = sorted(glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*"))
        for path in candidates:
            info = self._usb_info(path)
            try:
                vid = int(info.get("vendor", ""), 16)
                pid = int(info.get("product_id", ""), 16)
            except ValueError:
                continue
            if (vid == 0x2e8a and (pid in (0x10b1, 0x10b2, 0x10b3, 0x10c6) or 0xb000 <= pid <= 0xbfff)) or (vid, pid) in ((0x0f0d, 0x0092), (0x054c, 0x0ce6), (0x045e, 0x028e)):
                found.append((path, info))
        return found

    def discover(self):
        for path, info in self.discover_all():
            if self.adapter_id is None or self.identity(info) == self.adapter_id:
                return path, info
        return None, {}

    @property
    def firmware_upload(self):
        suffix = hashlib.sha256(str(self.adapter_id).encode("utf-8")).hexdigest()[:16]
        return BLUEBRIDGE_FIRMWARE_UPLOAD.replace(".uf2", "-" + suffix + ".uf2")

    @property
    def pre_update_backup(self):
        suffix = hashlib.sha256(str(self.adapter_id).encode("utf-8")).hexdigest()[:16]
        return BLUEBRIDGE_PRE_UPDATE_BACKUP.replace(".bbconfig", "-" + suffix + ".bbconfig")

    def _configure(self, fd):
        attrs = termios.tcgetattr(fd)
        attrs[0] = 0
        attrs[1] = 0
        attrs[2] = termios.CLOCAL | termios.CREAD | termios.CS8
        attrs[3] = 0
        attrs[4] = termios.B115200
        attrs[5] = termios.B115200
        attrs[6][termios.VMIN] = 0
        attrs[6][termios.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSANOW, attrs)
        termios.tcflush(fd, termios.TCIOFLUSH)

    def close(self):
        if self.fd is not None:
            try:
                os.close(self.fd)
            except Exception:
                pass
        self.fd = None
        self.path = None
        self.rx = b""
        self.info = {}

    def connect(self):
        path, info = self.discover()
        if not path:
            self.close()
            raise RuntimeError("MC BlueBridge not detected")
        if self.fd is not None and self.path == path:
            return
        self.close()
        fd = os.open(path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        self._configure(fd)
        self.fd = fd
        self.path = path
        self.info = info
        self.rx = b""
        time.sleep(0.05)
        try:
            hello = self.request_json("HELLO")
            if hello.get("protocol") != 2 or hello.get("hardware") != "Pico 2 W" or not str(hello.get("firmware_id", "")).startswith("MCBLUEBRIDGE|"):
                raise RuntimeError("The selected device is not an MC BlueBridge adapter")
            if hello.get("adapter_id") and hello["adapter_id"] != self.adapter_id:
                raise RuntimeError("BlueBridge adapter identity changed")
            self.verified = True
            self.adapter_name = hello.get("adapter_name") or "MC BlueBridge adapter"
        except Exception:
            self.close()
            raise

    def _next_id(self):
        self.counter = (self.counter + 1) & 0x7fffffff
        if self.counter == 0:
            self.counter = 1
        return str(self.counter)

    def _write(self, data):
        raw = data.encode("utf-8")
        offset = 0
        while offset < len(raw):
            try:
                n = os.write(self.fd, raw[offset:])
            except BlockingIOError:
                n = 0
            if n:
                offset += n
            else:
                select.select([], [self.fd], [], 0.1)

    def _readline(self, timeout):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            pos = self.rx.find(b"\n")
            if pos >= 0:
                raw = self.rx[:pos]
                self.rx = self.rx[pos + 1:]
                return raw.decode("utf-8", errors="replace").rstrip("\r")
            remaining = max(0.0, end - time.monotonic())
            ready, _, _ = select.select([self.fd], [], [], min(0.15, remaining))
            if not ready:
                continue
            try:
                chunk = os.read(self.fd, 4096)
            except BlockingIOError:
                chunk = b""
            if chunk:
                self.rx += chunk
            else:
                time.sleep(0.01)
        raise TimeoutError("BlueBridge did not respond")

    def _send(self, command, *args):
        self.connect()
        request_id = self._next_id()
        fields = ["BB1", request_id, command]
        fields.extend(str(x).replace("\r", " ").replace("\n", " ") for x in args)
        if command in ("HELLO", "STATUS", "MODE_GET", "BT_DIAGNOSTICS", "HID_DIAGNOSTICS", "CONTROLLERS", "BLOCKED_DEVICES"):
            self.diagnostics.record("tx", "|".join(fields))
        self._write("|".join(fields) + "\n")
        return request_id

    def _parse_line(self, line):
        parts = line.split("|", 3)
        if len(parts) < 3 or parts[0] != "BB1":
            return None
        return parts[1], parts[2], parts[3] if len(parts) > 3 else ""

    def request(self, command, *args, timeout=2.5):
        with self.lock:
            try:
                request_id = self._send(command, *args)
                end = time.monotonic() + timeout
                while time.monotonic() < end:
                    line = self._readline(max(0.05, end - time.monotonic()))
                    if command in ("HELLO", "STATUS", "MODE_GET", "BT_DIAGNOSTICS", "HID_DIAGNOSTICS", "CONTROLLERS", "BLOCKED_DEVICES"):
                        self.diagnostics.record("rx", line)
                    parsed = self._parse_line(line)
                    if not parsed or parsed[0] != request_id:
                        continue
                    _, status, payload = parsed
                    if status == "ERR":
                        raise RuntimeError(payload or "BlueBridge command failed")
                    if status != "OK":
                        raise RuntimeError("Unexpected BlueBridge response")
                    return payload
                raise TimeoutError("BlueBridge did not respond")
            except Exception:
                self.close()
                raise

    def request_json(self, command, *args, timeout=2.5):
        payload = self.request(command, *args, timeout=timeout)
        if not payload:
            return {}
        try:
            return json.loads(payload)
        except Exception:
            return {"value": payload}

    def sample_diagnostics(self):
        hello = self.request_json("HELLO")
        mode = self.request_json("MODE_GET") if hello.get("capabilities", {}).get("multi_controller_mode") else {"multi_controller": False, "max_connected": 1}
        selected = self.request_json("BT_DIAGNOSTICS")
        self.diagnostics.snapshot(selected, selected=True)
        connections = [selected]
        all_available = bool(hello.get("capabilities", {}).get("multi_controller_diagnostics")) or not mode.get("multi_controller")
        if mode.get("multi_controller") and all_available:
            connections = []
            for slot in range(max(1, min(int(mode.get("max_connected", 4)), 4))):
                value = self.request_json("BT_DIAGNOSTICS", slot)
                self.diagnostics.snapshot(value)
                connections.append(value)
        return {"mode": mode, "connections": connections, "all_connections_available": all_available}

    def diagnostic_report(self):
        extra = {}
        for key, work in (("adapter_status", self.status), ("connection_capture", self.sample_diagnostics), ("controllers", self.controllers), ("blocked_devices", self.blocked_devices)):
            try:
                extra[key] = work()
            except Exception as error:
                extra[key + "_error"] = str(error)
        if extra.get("adapter_status", {}).get("controller_connected"):
            try:
                hid = self.request_json("HID_DIAGNOSTICS", 0)
                total = int(hid.get("descriptor_length", 0))
                if not 0 <= total <= 8192:
                    raise ValueError("Invalid HID descriptor length")
                chunks = [hid.get("descriptor_hex", "")]
                for offset in range(128, total, 128):
                    chunk = self.request_json("HID_DIAGNOSTICS", offset)
                    if int(chunk.get("offset", -1)) != offset or int(chunk.get("descriptor_length", -1)) != total:
                        raise RuntimeError("HID descriptor changed while reading")
                    chunks.append(chunk.get("descriptor_hex", ""))
                hid["full_descriptor_hex"] = "".join(chunks)
                if len(bytes.fromhex(hid["full_descriptor_hex"])) != total:
                    raise RuntimeError("Incomplete HID descriptor")
                extra["hid"] = hid
            except Exception as error:
                extra["hid_error"] = str(error)
        return dict(self.diagnostics.report(), **extra)

    def status(self):
        try:
            hello = self.request_json("HELLO")
            status = self.request_json("STATUS")
            status["detected"] = True
            status["port"] = self.path
            status["serial"] = self.info.get("serial", "")
            status["usb_product"] = self.info.get("product", "")
            status["protocol"] = hello.get("protocol", status.get("protocol"))
            status["config_schema"] = hello.get("config_schema")
            status["capabilities"] = hello.get("capabilities", {})
            for capability, key, command in (
                ("touch_mouse", "touch_mouse", "TOUCH_MOUSE_GET"),
                ("ds4_right_click", "ds4_mouse", "DS4_MOUSE_GET"),
                ("ds4_gyro", "ds4_aim", "DS4_AIM_GET"),
                ("ds4_lightbar", "lightbar", "LIGHTBAR_GET"),
            ):
                if status["capabilities"].get(capability):
                    try:
                        status[key] = self.request_json(command)
                    except Exception as error:
                        status[key + "_error"] = str(error)
            self.adapter_name = hello.get("adapter_name") or "MC BlueBridge adapter"
            status["adapter_id"] = self.adapter_id
            status["adapter_name"] = self.adapter_name
            status["adapter_custom_name"] = hello.get("adapter_custom_name", "")
            return status
        except Exception as e:
            return {"detected": False, "connected": False, "message": str(e)}

    def controllers(self):
        return self.request_json("CONTROLLERS")

    def blocked_devices(self):
        return self.request_json("BLOCKED_DEVICES")

    def profiles(self):
        return self.request_json("PROFILES")

    def profile(self, index):
        return self.request_json("PROFILE_GET", int(index))

    def export_config(self):
        with self.lock:
            try:
                request_id = self._send("CONFIG_EXPORT")
                schema = None
                size = None
                checksum = None
                chunks = {}
                end = time.monotonic() + 8.0
                while time.monotonic() < end:
                    parsed = self._parse_line(self._readline(max(0.05, end - time.monotonic())))
                    if not parsed or parsed[0] != request_id:
                        continue
                    _, status, payload = parsed
                    if status == "ERR":
                        raise RuntimeError(payload or "BlueBridge export failed")
                    if status == "DATA_BEGIN":
                        fields = payload.split("|")
                        if len(fields) != 3:
                            raise RuntimeError("Invalid BlueBridge export header")
                        schema = int(fields[0])
                        size = int(fields[1])
                        checksum = int(fields[2])
                    elif status == "DATA":
                        fields = payload.split("|", 1)
                        if len(fields) != 2:
                            raise RuntimeError("Invalid BlueBridge export chunk")
                        chunks[int(fields[0])] = fields[1]
                    elif status == "DATA_END":
                        break
                if schema is None or size is None or checksum is None:
                    raise RuntimeError("Incomplete BlueBridge export")
                data = bytearray(size)
                written = 0
                for offset in sorted(chunks):
                    raw = bytes.fromhex(chunks[offset])
                    end_offset = offset + len(raw)
                    if offset != written or end_offset > size:
                        raise RuntimeError("Invalid BlueBridge export data")
                    data[offset:end_offset] = raw
                    written = end_offset
                if written != size:
                    raise RuntimeError("Incomplete BlueBridge export data")
                return {
                    "format": "MC-BLUEBRIDGE-CONFIG-1",
                    "schema": schema,
                    "size": size,
                    "checksum": checksum,
                    "data": base64.b64encode(bytes(data)).decode("ascii"),
                }
            except Exception:
                self.close()
                raise

    def import_config(self, package):
        if str(package.get("format", "")) != "MC-BLUEBRIDGE-CONFIG-1":
            raise ValueError("Unsupported BlueBridge configuration file")
        schema = int(package.get("schema", 0))
        size = int(package.get("size", 0))
        checksum = int(package.get("checksum", 0))
        try:
            data = base64.b64decode(str(package.get("data", "")), validate=True)
        except Exception:
            raise ValueError("Invalid BlueBridge configuration data")
        if len(data) != size:
            raise ValueError("BlueBridge configuration size does not match")
        self.request("CONFIG_IMPORT_BEGIN", schema, size, checksum, timeout=3.0)
        chunk_size = 128
        for offset in range(0, len(data), chunk_size):
            self.request("CONFIG_IMPORT_CHUNK", offset, data[offset:offset + chunk_size].hex().upper(), timeout=3.0)
        self.request("CONFIG_IMPORT_COMMIT", timeout=4.0)
        return True


class BlueBridgeRegistry:
    def __init__(self):
        self.lock = threading.RLock()
        self.managers = {}
        self.scanner = BlueBridgeManager()

    def inventory(self):
        with self.lock:
            present = {}
            for path, info in self.scanner.discover_all():
                adapter_id = BlueBridgeManager.identity(info)
                if adapter_id in present:
                    continue
                manager = self.managers.get(adapter_id)
                if manager is None:
                    manager = BlueBridgeManager(adapter_id)
                    self.managers[adapter_id] = manager
                if not manager.verified and not manager.status().get("detected"):
                    continue
                present[adapter_id] = (manager, info)
            return present

    def adapters(self):
        return [{"id": key, "name": manager.adapter_name, "serial": info.get("serial", ""), "port": info["path"]} for key, (manager, info) in self.inventory().items()]

    def resolve(self, adapter_id):
        present = self.inventory()
        with self.lock:
            if adapter_id:
                manager = self.managers.get(adapter_id)
                if manager is None or not manager.verified:
                    raise RuntimeError("Selected MC BlueBridge adapter is not available")
                return manager
            if len(present) != 1:
                raise RuntimeError("Select an MC BlueBridge adapter" if present else "MC BlueBridge not detected")
            return next(iter(present.values()))[0]

    def close(self):
        with self.lock:
            for manager in self.managers.values():
                manager.diagnostics.finish()
                with manager.lock:
                    manager.close()


bluebridge_registry = BlueBridgeRegistry()

BLUEBRIDGE_UF2_FAMILIES = {0xE48BFF57, 0xE48BFF59, 0xE48BFF5B}
BLUEBRIDGE_UF2_CODE_FAMILIES = {0xE48BFF59, 0xE48BFF5B}

BLUEBRIDGE_RELEASE_URL = "https://api.github.com/repos/Anime0t4ku/MC-BlueBridge/releases"

def version_key(value):
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?", str(value).strip())
    if not match:
        raise ValueError("Invalid firmware version: " + str(value))
    pre = match.group(4)
    if pre:
        pre = re.sub(r"^(alpha|beta|rc)[.-]?(\d+)$", r"\1.\2", pre.lower(), flags=re.IGNORECASE)
    identifiers = tuple((0, int(p)) if p.isdigit() else (1, p) for p in (pre or "").split("."))
    return tuple(int(match.group(i)) for i in (1, 2, 3)) + (1 if pre is None else 0, identifiers)

def _lookup_bluebridge_release(installed="", opener=None):
    opener = opener or urllib.request.urlopen
    candidates = []
    stable_only = bool(installed and version_key(installed)[3])
    try:
        for page in range(1, 21):
            request = urllib.request.Request(BLUEBRIDGE_RELEASE_URL + "?per_page=100&page=" + str(page), headers={"User-Agent": "MiSTer-Companion-BlueBridge", "Accept": "application/vnd.github+json"})
            with opener(request, timeout=15) as response:
                releases = json.load(response)
            if not isinstance(releases, list):
                return {"available": False, "state": "unavailable", "message": "Online firmware is not available yet. You can install a local UF2 file below."}
            for release in releases:
                if release.get("draft"):
                    continue
                try:
                    key = version_key(release.get("tag_name", ""))
                except ValueError:
                    continue
                if stable_only and (not key[3] or release.get("prerelease")):
                    continue
                for asset in release.get("assets", []):
                    url = asset.get("browser_download_url", "")
                    if asset.get("name") == "mc_bluebridge.uf2" and url.startswith("https://github.com/Anime0t4ku/MC-BlueBridge/releases/download/") and 0 < int(asset.get("size", 0)) <= 8 * 1024 * 1024:
                        candidates.append((key, release, asset))
                        break
            if len(releases) < 100:
                break
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {"available": False, "state": "unavailable", "message": "Online firmware is not available yet. You can install a local UF2 file below."}
        return {"available": False, "state": "error", "message": "Unable to check for updates. Please try again later."}
    except (OSError, ValueError, urllib.error.URLError):
        return {"available": False, "state": "error", "message": "Unable to check for updates. Please try again later."}
    if not candidates:
        return {"available": False, "state": "unavailable", "message": "Online firmware is not available yet. You can install a local UF2 file below."}
    stable = [c for c in candidates if c[0][3] and not c[1].get("prerelease")]
    key, release, asset = max((stable or candidates) if not installed else candidates, key=lambda c: c[0])
    return {"available": True, "version": release["tag_name"].lstrip("v"), "url": asset["browser_download_url"], "size": asset["size"], "update_available": not installed or key > version_key(installed)}

def download_bluebridge_release(info):
    if not info.get("available") or not info.get("url", "").startswith("https://github.com/Anime0t4ku/MC-BlueBridge/releases/download/"):
        raise ValueError("No firmware release available")
    request = urllib.request.Request(info["url"], headers={"User-Agent": "MiSTer-Companion-BlueBridge"})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read(8 * 1024 * 1024 + 1)
    if not data or len(data) > 8 * 1024 * 1024 or len(data) != info["size"]:
        raise ValueError("Incomplete or oversized firmware download")
    return data

_release_cache = {}
_release_cache_lock = threading.RLock()

def bluebridge_release(installed="", opener=None, force=False):
    if opener is not None:
        return _lookup_bluebridge_release(installed, opener)
    with _release_cache_lock:
        entry = _release_cache.get(installed)
        if not force and entry and time.monotonic() < entry[0]:
            return dict(entry[1])
        info = _lookup_bluebridge_release(installed)
        _release_cache[installed] = (time.monotonic() + (300 if info.get("available") else 60), info)
        return dict(info)

def supports_dualsense(firmware):
    try:
        return version_key(firmware) >= version_key('1.1.0')
    except ValueError:
        return False


def _version_tuple(value):
    return version_key(value)

def _uf2_info(data):
    if not data or len(data) % 512:
        raise ValueError("Invalid UF2 file size")
    chunks = []
    families = set()
    seen_blocks = set()
    block_groups = {}
    for offset in range(0, len(data), 512):
        block = data[offset:offset + 512]
        magic0, magic1, flags, target, payload_size, block_no, num_blocks, family = struct.unpack_from("<IIIIIIII", block, 0)
        magic_end = struct.unpack_from("<I", block, 508)[0]
        if magic0 != 0x0A324655 or magic1 != 0x9E5D5157 or magic_end != 0x0AB16F30:
            raise ValueError("Invalid UF2 block")
        if payload_size == 0 or payload_size > 476:
            raise ValueError("Invalid UF2 payload")
        family_id = family if flags & 0x00002000 else 0
        key = (family_id, num_blocks, block_no)
        if key in seen_blocks:
            raise ValueError("Duplicate UF2 block")
        seen_blocks.add(key)
        if not num_blocks or block_no >= num_blocks:
            raise ValueError("Invalid UF2 block sequence")
        compatibility_block = (
            offset == 0 and family_id == 0xE48BFF57 and
            flags in (0x00002000, 0x0000A000) and payload_size == 256 and
            block_no == 0 and num_blocks == 2 and
            0x10000000 <= target < 0x12000000 and target % 256 == 0 and
            block[32:288] == b'\xef' * 256 and
            (not flags & 0x00008000 or struct.unpack_from("<I", block, 288)[0] == 0x9957E304)
        )
        if compatibility_block:
            continue
        block_groups.setdefault((family_id, num_blocks), set()).add(block_no)
        if family_id:
            families.add(family_id)
            if family_id not in BLUEBRIDGE_UF2_FAMILIES:
                raise ValueError("This UF2 contains blocks for an unsupported device family")
        if family_id in BLUEBRIDGE_UF2_FAMILIES:
            chunks.append((target, block[32:32 + payload_size]))
    if not block_groups:
        raise ValueError("UF2 contains no firmware blocks")
    firmware_blocks = sum(len(numbers) for numbers in block_groups.values())
    complete_per_family = all(len(numbers) == count for (_, count), numbers in block_groups.items())
    counts = {count for _, count in block_groups}
    global_numbers = {number for numbers in block_groups.values() for number in numbers}
    complete_global = len(counts) == 1 and next(iter(counts)) == firmware_blocks and len(global_numbers) == firmware_blocks
    if not complete_per_family and not complete_global:
        raise ValueError("Incomplete UF2 block sequence")
    if not families.intersection(BLUEBRIDGE_UF2_CODE_FAMILIES):
        raise ValueError("This UF2 is not for MC BlueBridge on Raspberry Pi Pico 2 W")
    image = b"".join(payload for _, payload in sorted(chunks, key=lambda item: item[0]))
    match = re.search(rb"MCBLUEBRIDGE\|([0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?)\|PICO2W\|SCHEMA=([0-9]+)", image)
    version = None
    schema = None
    if match:
        version = match.group(1).decode("ascii")
        schema = int(match.group(2))
    elif b"MC BlueBridge" in image:
        versions = [x.decode("ascii") for x in re.findall(rb"(?<![0-9])[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?![0-9])", image)]
        if versions:
            version = max(versions, key=_version_tuple)
    if not version:
        raise ValueError("Unable to identify this file as MC BlueBridge firmware")
    return {"version": version, "config_schema": schema, "family": "RP2350", "size": len(data)}

def _inspect_bluebridge_firmware(data, bluebridge):
    info = _uf2_info(data)
    current = bluebridge.status()
    if not current.get("detected"):
        raise RuntimeError("MC BlueBridge not detected")
    current_version = str(current.get("firmware", "0.0.0"))
    a = _version_tuple(info["version"])
    b = _version_tuple(current_version)
    relation = "newer" if a > b else "same" if a == b else "older"
    info["current_version"] = current_version
    info["relation"] = relation
    return info

def _find_rp2350_device(usb_path):
    if not usb_path:
        raise RuntimeError("Unable to identify the selected adapter USB port")
    for node in sorted(glob.glob("/sys/class/block/*")):
        device_path = os.path.realpath(os.path.join(node, "device"))
        if not device_path.startswith(usb_path + "/"):
            continue
        device = "/dev/" + os.path.basename(node)
        try:
            label = subprocess.check_output(["blkid", "-s", "LABEL", "-o", "value", device], stderr=subprocess.DEVNULL, text=True).strip()
            if label == "RP2350":
                return device
        except Exception:
            pass
    return None

def _mounted_path(device):
    real = os.path.realpath(device)
    try:
        with open("/proc/mounts", "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                fields = line.split()
                if len(fields) >= 2 and os.path.realpath(fields[0]) == real:
                    return fields[1], False
    except Exception:
        pass
    mountpoint = "/tmp/mc_bluebridge_rp2350_" + os.path.basename(real)
    os.makedirs(mountpoint, exist_ok=True)
    result = subprocess.run(["mount", device, mountpoint], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or "Unable to mount RP2350 update volume").strip())
    return mountpoint, True

def _wait_for_bluebridge(bluebridge, timeout=60.0, stable_reads=3):
    end = time.monotonic() + timeout
    last = None
    stable = 0
    latest = None
    while time.monotonic() < end:
        try:
            status = bluebridge.status()
            if status.get("detected"):
                latest = status
                stable += 1
                if stable >= stable_reads:
                    return latest
            else:
                stable = 0
                last = status.get("message")
        except Exception as e:
            stable = 0
            last = str(e)
        time.sleep(0.75)
    return None

def _retry_bluebridge_action(bluebridge, action, timeout=15.0):
    end = time.monotonic() + timeout
    last = None
    while time.monotonic() < end:
        try:
            return action()
        except Exception as e:
            last = str(e)
            bluebridge.close()
            time.sleep(1.0)
    raise RuntimeError(last or "BlueBridge did not respond")

def _reset_bluebridge_configuration(bluebridge):
    _retry_bluebridge_action(bluebridge, lambda: bluebridge.request("FORGET_ALL", timeout=4.0))
    try:
        bluebridge.request("CONFIG_RESET", timeout=2.0)
    except Exception:
        pass
    try:
        bluebridge.request("PAIR_STOP", timeout=2.0)
    except Exception:
        pass
    bluebridge.close()
    status = _wait_for_bluebridge(bluebridge, timeout=30.0, stable_reads=2)
    if status is None:
        raise RuntimeError("BlueBridge did not return after configuration reset")
    controllers = _retry_bluebridge_action(bluebridge, lambda: bluebridge.controllers(), timeout=10.0)
    if controllers.get("controllers"):
        raise RuntimeError("BlueBridge returned, but stored controllers are still present")
    return status

def _install_bluebridge_firmware(bluebridge, settings_mode):
    if settings_mode not in ("preserve", "reset"):
        raise ValueError("Invalid configuration option")
    with open(bluebridge.firmware_upload, "rb") as f:
        data = f.read()
    info = _inspect_bluebridge_firmware(data, bluebridge)
    if settings_mode == "preserve":
        backup = bluebridge.export_config()
        os.makedirs(os.path.dirname(bluebridge.pre_update_backup), exist_ok=True)
        with open(bluebridge.pre_update_backup, "w", encoding="utf-8") as f:
            json.dump(backup, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
    usb_path = bluebridge.info.get("usb_path")
    if not usb_path:
        raise RuntimeError("Unable to identify the selected adapter USB port")
    bluebridge.request("REBOOT_BOOTSEL", timeout=3.0)
    bluebridge.close()
    device = None
    end = time.monotonic() + 12.0
    while time.monotonic() < end and not device:
        device = _find_rp2350_device(usb_path)
        if not device:
            time.sleep(0.25)
    if not device:
        raise RuntimeError("RP2350 update mode was not detected")
    mountpoint, mounted_here = _mounted_path(device)
    try:
        target = os.path.join(mountpoint, "MC-BlueBridge.uf2")
        with open(bluebridge.firmware_upload, "rb") as src, open(target, "wb", buffering=0) as dst:
            shutil.copyfileobj(src, dst, 65536)
            os.fsync(dst.fileno())
        try:
            os.sync()
        except Exception:
            pass
    finally:
        if mounted_here:
            time.sleep(0.5)
            subprocess.run(["umount", mountpoint], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    status = _wait_for_bluebridge(bluebridge)
    result = {"version": info["version"], "previous_version": info["current_version"], "configuration": settings_mode, "state": "success", "message": "Firmware updated successfully"}
    if status is None:
        result["state"] = "verification_timeout"
        result["message"] = "Firmware was transferred successfully, but BlueBridge did not return in time for verification. Refresh this page after BlueBridge reconnects."
    elif _version_tuple(status.get("firmware", "0.0.0")) != _version_tuple(info["version"]):
        result["state"] = "verification_warning"
        result["message"] = "Firmware was transferred, but BlueBridge reported v%s instead of v%s." % (status.get("firmware", "unknown"), info["version"])
    else:
        if settings_mode == "reset":
            try:
                _reset_bluebridge_configuration(bluebridge)
                result["message"] = "Firmware updated successfully and configuration reset"
            except Exception as e:
                result["state"] = "configuration_warning"
                result["message"] = "Firmware v%s is installed, but the requested configuration step could not be confirmed: %s" % (info["version"], str(e))
    try:
        os.unlink(bluebridge.firmware_upload)
    except Exception:
        pass
    return result

def response(ok=True, response_type="result", message="", version=DAEMON_VERSION, **extra):
    result = {
        "ok": ok,
        "type": response_type,
        "message": message,
        "version": version,
    }
    result.update(extra)
    return result

def save_pointer_settings(bluebridge,payload):
    aim=payload.get("ds4_aim")
    if aim is None:return bluebridge.request_json("TOUCH_MOUSE_SET",int(payload["enabled"]))
    if not bluebridge.request_json("HELLO").get("capabilities",{}).get("ds4_gyro"):
        raise ValueError("This firmware does not advertise DS4 gyro support")
    if not isinstance(aim,dict) or type(aim.get("enabled")) is not bool:
        raise ValueError("Invalid DS4 gyro settings")
    for name,low,high in [("sensitivity",1,200),("activation",0,2),("flags",0,7),("pause_button",0,255)]:
        value=aim.get(name)
        if type(value) is not int or value<low or value>high:raise ValueError("Invalid DS4 gyro "+name)
    if aim["pause_button"]>13 and aim["pause_button"]!=255:raise ValueError("Invalid DS4 pause button")
    return bluebridge.request_json("DS4_AIM_SET",int(aim["enabled"]),aim["sensitivity"],aim["activation"],aim["flags"],aim["pause_button"],int(payload["enabled"]))

# BLUEBRIDGE_DS4_LIGHTBAR
def lightbar_rgb(value):
    if not isinstance(value,list) or len(value)!=3 or any(type(v) is not int or v<0 or v>255 for v in value):
        raise ValueError("A colour must contain three whole numbers from 0 to 255")
    return value
def save_lightbar_palette(bluebridge,payload):
    if not isinstance(payload,dict):raise ValueError("Invalid colour settings")
    theme=payload.get("theme");players=payload.get("players")
    if type(theme) is not int or theme<0 or theme>2:raise ValueError("Invalid colour theme")
    if not isinstance(players,list) or len(players)!=4:raise ValueError("Four player colours are required")
    colours=[lightbar_rgb(rgb) for rgb in players]
    expected={1:[[0,0,64],[64,32,0]],2:[[64,0,0],[0,64,0]]}
    if theme and colours[:2]!=expected[theme]:raise ValueError("Theme colours changed; select Custom")
    bluebridge.request("LIGHTBAR_PALETTE_SET",theme,*[v for rgb in colours for v in rgb])
    return bluebridge.request_json("LIGHTBAR_GET")
def save_lightbar_controller(bluebridge,payload):
    if not isinstance(payload,dict):raise ValueError("Invalid controller colour settings")
    for name,maximum in [("index",7),("id",4294967295),("player",4)]:
        value=payload.get(name)
        if type(value) is not int or value<0 or value>maximum:raise ValueError("Invalid controller "+name)
    if type(payload.get("custom_enabled")) is not bool:raise ValueError("Invalid custom colour choice")
    rgb=lightbar_rgb(payload.get("rgb"))
    bluebridge.request("LIGHTBAR_SET",payload["index"],payload["id"],payload["player"],int(payload["custom_enabled"]),*rgb)
    return bluebridge.request_json("LIGHTBAR_GET")

OUTPUT_NAMES = {
    1: 'MiSTer', 2: 'X-Input (BlueBridge)', 3: 'Generic HID',
    4: 'Nintendo Switch', 5: 'Xbox 360', 6: 'DualSense',
    7: 'X-Input (X360)',
}
USB_MANAGEMENT_WARNING = (
    'On some devices, this mode may lose the USB serial connection, so BlueBridge '
    'management will be unavailable. Hold BOOTSEL for 5 seconds to disconnect all '
    'controllers and return to MiSTer mode. Saved output overrides are preserved '
    'and apply again when the controller reconnects. Continue?'
)


def validate_output_mode(manager, mode):
    if type(mode) is not int or mode not in OUTPUT_NAMES:
        raise ValueError('Invalid output mode')
    hello = manager.request_json('HELLO')
    if mode == 7 and not hello.get('capabilities', {}).get('native_xinput_modes'):
        raise ValueError('X-Input (X360) requires BlueBridge firmware v2.0.0 or later.')
    if mode == 6 and not supports_dualsense(hello.get('firmware')):
        raise ValueError('DualSense requires BlueBridge firmware v1.1.0 or later.')
    return mode


def save_controller_output(manager, payload):
    if not isinstance(payload, dict):
        raise ValueError('Invalid controller output settings')
    for key, maximum in (('index', 7), ('id', 4294967295), ('mode', 7)):
        value = payload.get(key)
        if type(value) is not int or not 0 <= value <= maximum:
            raise ValueError('Invalid controller output ' + key)
    if not manager.request_json('HELLO').get('capabilities', {}).get('controller_output_override'):
        raise ValueError('Controller output overrides require BlueBridge firmware v2.0.0 or later.')
    if payload['mode']:
        validate_output_mode(manager, payload['mode'])
    return manager.request_json('CONTROLLER_OUTPUT_SET', payload['index'], payload['id'], payload['mode'])



def save_ds4_mouse_settings(bluebridge,payload):
    if not isinstance(payload,dict) or type(payload.get("right_click")) is not bool:
        raise ValueError("right_click must be a boolean")
    if not bluebridge.request_json("HELLO").get("capabilities",{}).get("ds4_right_click"):
        raise ValueError("This firmware does not support the right-click option")
    bluebridge.request("DS4_MOUSE_SET",int(payload["right_click"]))
    return bluebridge.request_json("DS4_MOUSE_GET")

UPDATE_OPERATION_LOCK = threading.Lock()


def dispatch(sock, method, target, headers, request_body):
    if method == 'POST':
        if not UPDATE_OPERATION_LOCK.acquire(blocking=False):
            _json_http(sock, response(False, 'error', 'Another operation is running. Please wait.'), '409 Conflict')
            return
        try:
            if bluebridge_updater.busy(DATA_ROOT):
                _json_http(sock, response(False, 'error', 'Batocera daemon update is running. Please wait.'), '409 Conflict')
                return
            return dispatch_request(sock, method, target, headers, request_body)
        finally:
            UPDATE_OPERATION_LOCK.release()
    return dispatch_request(sock, method, target, headers, request_body)


def dispatch_request(sock, method, target, headers, request_body):
    parsed = urllib.parse.urlsplit(target)
    request_path = parsed.path
    query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    if request_path == '/status':
        _json_http(sock, response(True, 'status', 'MC BlueBridge Batocera daemon is running'))
        return
    if request_path in ('/', '/index.html', '/bluebridge', '/bluebridge/'):
        send_http(sock, '200 OK', 'text/html; charset=utf-8', BLUEBRIDGE_HTML)
        return
    if request_path == '/assets/logo.png' or request_path == '/favicon.ico':
        send_http(sock, '200 OK', 'image/png', LOGO_PNG, ['Cache-Control: public, max-age=86400'])
        return
    if request_path.startswith('/api/daemon/'):
        try:
            if request_path == '/api/daemon/status' and method == 'GET':
                _json_http(sock, response(True, 'daemon', update=bluebridge_updater.status(DATA_ROOT, DAEMON_VERSION)))
            elif request_path == '/api/daemon/releases' and method == 'GET':
                _json_http(sock, response(True, 'daemon', release=bluebridge_updater.latest(DAEMON_VERSION)))
            elif request_path == '/api/daemon/update' and method == 'POST':
                payload = json.loads(request_body.decode('utf-8') or '{}')
                if not isinstance(payload, dict) or not isinstance(payload.get('version'), str):
                    raise ValueError('Choose a daemon release first')
                bluebridge_updater.start(APP_ROOT, DATA_ROOT, DAEMON_VERSION, payload['version'])
                _json_http(sock, response(True, 'daemon', 'Batocera daemon update started', update=bluebridge_updater.status(DATA_ROOT, DAEMON_VERSION)))
            else:
                _json_http(sock, response(False, 'error', 'Unknown daemon action or incorrect method'), '405 Method Not Allowed')
        except Exception as error:
            _json_http(sock, response(False, 'error', str(error)), '400 Bad Request')
        return
    if request_path == "/api/bluebridge/adapters":
        try:
            _json_http(sock, response(True, "bluebridge", "OK", adapters=bluebridge_registry.adapters()))
        except Exception as e:
            _json_http(sock, response(False, "error", str(e)), "503 Service Unavailable")
        return
    if request_path.startswith("/api/bluebridge/"):
        try:
            bluebridge = bluebridge_registry.resolve(headers.get("x-bluebridge-adapter", "") or query.get("adapter_id", [""])[0])
        except Exception as e:
            if request_path == "/api/bluebridge/status":
                _json_http(sock, response(True, "bluebridge", "OK", status={"detected": False, "connected": False, "message": str(e)}))
            else:
                _json_http(sock, response(False, "error", str(e)), "503 Service Unavailable")
            return
        with bluebridge.lock:
            if request_path in ("/api/bluebridge/diagnostics", "/api/bluebridge/diagnostics/start", "/api/bluebridge/diagnostics/stop", "/api/bluebridge/diagnostics/report"):
                required = "POST" if request_path.endswith(("/start", "/stop")) else "GET"
                if method != required:
                    _json_http(sock, response(False, "error", required + " required"), "405 Method Not Allowed")
                    return
                if request_path.endswith("/start"):
                    bluebridge.diagnostics.start(bluebridge)
                elif request_path.endswith("/stop"):
                    bluebridge.diagnostics.finish()
                if request_path.endswith("/report"):
                    _json_http(sock, response(True, "bluebridge", "OK", report=bluebridge.diagnostic_report()))
                else:
                    _json_http(sock, response(True, "bluebridge", "OK", diagnostics=bluebridge.diagnostics.summary()))
                return
            if request_path == "/api/bluebridge/adapter/rename":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    if not bluebridge.request_json("HELLO").get("capabilities", {}).get("adapter_rename"):
                        raise RuntimeError("Adapter naming requires newer BlueBridge firmware")
                    name = str(payload.get("name", "")).strip()
                    if len(name.encode("utf-8")) > 31 or any(c in name for c in ("|", "\r", "\n")):
                        raise ValueError("Adapter name must be 31 bytes or fewer and contain no line breaks or |")
                    bluebridge.request("ADAPTER_RENAME", name)
                    bluebridge.adapter_name = name or "MC BlueBridge adapter"
                    bluebridge.close()
                    _json_http(sock, response(True, "bluebridge", "Adapter name saved"))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/status":
                _json_http(sock, response(True, "bluebridge", "OK", status=bluebridge.status()))
                return
            if request_path == "/api/bluebridge/firmware/releases":
                try:
                    info = bluebridge_release(bluebridge.status().get("firmware", ""), force=query.get("force", [""])[0] == "1")
                    _json_http(sock, response(True, "bluebridge", "OK", release=info))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/firmware/download":
                try:
                    if method != "POST":
                        raise ValueError("POST required")
                    info = bluebridge_release(bluebridge.status().get("firmware", ""))
                    data = download_bluebridge_release(info)
                    firmware = _inspect_bluebridge_firmware(data, bluebridge)
                    if version_key(firmware["version"]) != version_key(info["version"]):
                        raise ValueError("Firmware does not match release tag")
                    os.makedirs(os.path.dirname(bluebridge.firmware_upload), exist_ok=True)
                    with open(bluebridge.firmware_upload, "wb") as f:
                        f.write(data)
                        f.flush()
                        os.fsync(f.fileno())
                    _json_http(sock, response(True, "bluebridge", "Firmware validated", firmware=firmware))
                except Exception as e:
                    try:
                        os.unlink(bluebridge.firmware_upload)
                    except OSError:
                        pass
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/firmware/inspect":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    if not request_body or len(request_body) > 8 * 1024 * 1024:
                        raise ValueError("Firmware file is empty or too large")
                    info = _inspect_bluebridge_firmware(request_body, bluebridge)
                    os.makedirs(os.path.dirname(bluebridge.firmware_upload), exist_ok=True)
                    with open(bluebridge.firmware_upload, "wb") as f:
                        f.write(request_body)
                        f.flush()
                        os.fsync(f.fileno())
                    _json_http(sock, response(True, "bluebridge", "Firmware validated", firmware=info))
                except Exception as e:
                    try:
                        os.unlink(bluebridge.firmware_upload)
                    except Exception:
                        pass
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/firmware/install":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    result = _install_bluebridge_firmware(bluebridge, str(payload.get("configuration", "preserve")))
                    _json_http(sock, response(True, "bluebridge", "Firmware updated", firmware=result))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/firmware/cancel":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    os.unlink(bluebridge.firmware_upload)
                except Exception:
                    pass
                _json_http(sock, response(True, "bluebridge", "Firmware update cancelled"))
                return
            if request_path == "/api/bluebridge/controllers":
                try:
                    _json_http(sock, response(True, "bluebridge", "OK", controllers=bluebridge.controllers()))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "503 Service Unavailable")
                return
            if request_path == "/api/bluebridge/controllers/rename":
                try:
                    if method != "POST":
                        raise ValueError("POST required")
                    if not bluebridge.request_json("HELLO").get("capabilities", {}).get("controller_rename"):
                        raise ValueError("Update firmware to rename controllers")
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    name = str(payload.get("name", "")).strip()
                    if len(name.encode("utf-8")) > 31:
                        raise ValueError("Controller name must be 31 bytes or fewer")
                    name = name.replace("|", " ").replace("\r", " ").replace("\n", " ")
                    bluebridge.request("CONTROLLER_RENAME", int(payload.get("index", -1)), name)
                    _json_http(sock, response(True, "bluebridge", "Controller renamed"))
                except Exception as e:
                    _json_http(sock, response(False, "bluebridge", str(e)), "400 Bad Request")
                return

            if request_path == "/api/bluebridge/controllers/select":
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    bluebridge.request("CONTROLLER_SELECT", int(payload.get("index", -1)))
                    _json_http(sock, response(True, "bluebridge", "Controller selected"))
                except Exception as e:
                    _json_http(sock, response(False, "bluebridge", str(e)), "400 Bad Request")
                return

            if request_path == "/api/bluebridge/capture/start":
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    mode = str(payload.get("mode", "ONCE")).upper()
                    bluebridge.request("CAPTURE_START", "TESTER" if mode == "TESTER" else "ONCE")
                    _json_http(sock, response(True, "bluebridge", "Capture started"))
                except Exception as e:
                    _json_http(sock, response(False, "bluebridge", str(e)), "400 Bad Request")
                return

            if request_path == "/api/bluebridge/capture/status":
                try:
                    _json_http(sock, response(True, "bluebridge", "OK", capture=bluebridge.request_json("CAPTURE_STATUS")))
                except Exception as e:
                    _json_http(sock, response(False, "bluebridge", str(e)), "400 Bad Request")
                return

            if request_path == "/api/bluebridge/capture/stop":
                try:
                    bluebridge.request("CAPTURE_STOP")
                    _json_http(sock, response(True, "bluebridge", "Capture stopped"))
                except Exception as e:
                    _json_http(sock, response(False, "bluebridge", str(e)), "400 Bad Request")
                return

            if request_path == "/api/bluebridge/rumble":
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    strength = max(0, min(255, int(payload.get("strength", 128))))
                    duration = max(50, min(3000, int(payload.get("duration", 500))))
                    bluebridge.request("CONTROLLER_RUMBLE", strength, duration)
                    _json_http(sock, response(True, "bluebridge", "Rumble started"))
                except Exception as e:
                    _json_http(sock, response(False, "bluebridge", str(e)), "400 Bad Request")
                return

            if request_path == "/api/bluebridge/controllers/disconnect":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    bluebridge.request("CONTROLLER_DISCONNECT")
                    _json_http(sock, response(True, "bluebridge", "Controller disconnect requested"))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/controllers/forget":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    bluebridge.request("CONTROLLER_FORGET", int(payload.get("index", -1)))
                    _json_http(sock, response(True, "bluebridge", "Controller forgotten"))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/blocked-devices":
                try:
                    _json_http(sock, response(True, "bluebridge", "OK", blocked_devices=bluebridge.blocked_devices()))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "503 Service Unavailable")
                return
            if request_path == "/api/bluebridge/blocked-devices/block":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    bluebridge.request("DEVICE_BLOCK", str(payload.get("id", "")), str(payload.get("name", "Bluetooth Device")).replace("|", " ").replace("\r", " ").replace("\n", " ")[:31])
                    _json_http(sock, response(True, "bluebridge", "Device blocked"))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/blocked-devices/unblock":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    bluebridge.request("DEVICE_UNBLOCK", str(payload.get("id", "")))
                    _json_http(sock, response(True, "bluebridge", "Device unblocked"))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/profiles":
                try:
                    _json_http(sock, response(True, "bluebridge", "OK", profiles=bluebridge.profiles()))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "503 Service Unavailable")
                return
            if request_path == "/api/bluebridge/profile":
                try:
                    index = int(query.get("index", ["0"])[0])
                    _json_http(sock, response(True, "bluebridge", "OK", profile=bluebridge.profile(index)))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/pair":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    bluebridge.request("PAIR_START" if payload.get("start", True) else "PAIR_STOP")
                    _json_http(sock, response(True, "bluebridge", "OK", status=bluebridge.status()))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "503 Service Unavailable")
                return
            if request_path == "/api/bluebridge/forget":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    bluebridge.request("FORGET_ALL")
                    _json_http(sock, response(True, "bluebridge", "Paired controllers cleared"))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "503 Service Unavailable")
                return
            if request_path == "/api/bluebridge/profiles/create":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    name = str(payload.get("name", "")).strip()
                    if not re.fullmatch(r"[A-Za-z0-9 _.-]{1,23}", name):
                        raise ValueError("Invalid profile name")
                    result = bluebridge.request_json("PROFILE_CREATE", name)
                    _json_http(sock, response(True, "bluebridge", "Profile created", result=result))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/profiles/duplicate":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    name = str(payload.get("name", "Copy")).strip()
                    if not re.fullmatch(r"[A-Za-z0-9 _.-]{1,23}", name):
                        raise ValueError("Invalid profile name")
                    result = bluebridge.request_json("PROFILE_DUPLICATE", int(payload.get("index", -1)), name)
                    _json_http(sock, response(True, "bluebridge", "Profile duplicated", result=result))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/profiles/select":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    bluebridge.request("PROFILE_SELECT", int(payload.get("index", -1)))
                    bluebridge.close()
                    _json_http(sock, response(True, "bluebridge", "Profile activated"))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/profiles/delete":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    bluebridge.request("PROFILE_DELETE", int(payload.get("index", -1)))
                    _json_http(sock, response(True, "bluebridge", "Profile deleted"))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/profiles/rename":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    name = str(payload.get("name", "")).strip()
                    if not re.fullmatch(r"[A-Za-z0-9 _.-]{1,23}", name):
                        raise ValueError("Invalid profile name")
                    bluebridge.request("PROFILE_RENAME", int(payload.get("index", -1)), name)
                    _json_http(sock, response(True, "bluebridge", "Profile renamed"))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/profile/map":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    bluebridge.request("PROFILE_MAP", int(payload.get("profile", -1)), int(payload.get("input", -1)), int(payload.get("output", -1)))
                    _json_http(sock, response(True, "bluebridge", "Mapping updated"))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/profile/tuning":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    profile_index = int(payload.get("profile", -1))
                    bluebridge.request("PROFILE_TUNE", profile_index, int(bool(payload.get("invert_x"))), int(bool(payload.get("invert_y"))), int(bool(payload.get("invert_rx"))), int(bool(payload.get("invert_ry"))), int(payload.get("deadzone_left", 8)), int(payload.get("deadzone_right", 8)), int(payload.get("trigger_deadzone", 4)), int(payload.get("turbo_rate_hz", 12)), int(payload.get("turbo_mask", 0)))
                    if not bluebridge.request_json("STATUS").get("multi_controller", False):
                        bluebridge.request("PROFILE_TURBO_MODIFIER", profile_index, int(payload.get("turbo_modifier", 8)))
                        bluebridge.request("PROFILE_TURBO_CONTROL", profile_index, int(bool(payload.get("turbo_enabled"))), int(payload.get("turbo_control_mode", 0)), int(payload.get("turbo_control_button", 13)))
                    _json_http(sock, response(True, "bluebridge", "Profile tuning updated"))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/profile/macro":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    bluebridge.request("PROFILE_MACRO", int(payload.get("profile", -1)), int(payload.get("macro", -1)), int(bool(payload.get("enabled"))), str(payload.get("name", "")).replace("|", " ").replace("\r", " ").replace("\n", " ")[:15], int(payload.get("output_mask", 0)))
                    _json_http(sock, response(True, "bluebridge", "Macro updated"))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/profile/mister-mapping":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    profile = int(payload.get("profile", -1))
                    mode = str(payload.get("mode", "separate")).lower().strip()
                    if mode == "separate":
                        bluebridge.request("PROFILE_MAPPING_SEPARATE", profile)
                    elif mode == "share":
                        bluebridge.request("PROFILE_MAPPING_SHARE", profile, int(payload.get("target", -1)))
                    else:
                        raise ValueError("Invalid MiSTer mapping mode")
                    bluebridge.close()
                    _json_http(sock, response(True, "bluebridge", "MiSTer mapping updated"))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/profile/identity":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    profile = int(payload.get("profile", -1))
                    if payload.get("unique", True):
                        bluebridge.request("PROFILE_MAPPING_SEPARATE", profile)
                    else:
                        bluebridge.request("PROFILE_MAPPING_SHARE", profile, 0)
                    bluebridge.close()
                    _json_http(sock, response(True, "bluebridge", "MiSTer mapping updated"))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/mode":
                try:
                    if method == "POST":
                        payload = json.loads(request_body.decode("utf-8") or "{}")
                        enabled = payload.get("multi_controller")
                        if not isinstance(enabled, bool):
                            raise ValueError("multi_controller must be a boolean")
                        bluebridge.request("MODE_SET", int(enabled))
                        bluebridge.close()
                        _json_http(sock, response(True, "bluebridge", "Adapter restarting"))
                    elif method == "GET":
                        _json_http(sock, response(True, "bluebridge", "OK", mode=bluebridge.request_json("MODE_GET")))
                    else:
                        _json_http(sock, response(False, "error", "GET or POST required"), "405 Method Not Allowed")
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/ds4-mouse":
                if method != "POST":
                    _json_http(sock,response(False,"error","POST required"),"405 Method Not Allowed")
                    return
                try:
                    payload=json.loads(request_body.decode("utf-8") or "{}")
                    settings=save_ds4_mouse_settings(bluebridge,payload)
                    _json_http(sock,response(True,"bluebridge","Right-click option saved",settings=settings))
                except Exception as right_click_error:
                    _json_http(sock,response(False,"error",str(right_click_error)),"400 Bad Request")
                return
            if request_path == "/api/bluebridge/touch-mouse":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    if not bluebridge.request_json("HELLO").get("capabilities", {}).get("touch_mouse"):
                        raise ValueError("This firmware does not support touchpad mouse output")
                    payload = json.loads(request_body.decode("utf-8") or "{}")
                    if not isinstance(payload, dict) or type(payload.get("enabled")) is not bool:
                        raise ValueError("enabled must be a boolean")
                    result = save_pointer_settings(bluebridge, payload)
                    if result.get("restart_required"):
                        bluebridge.close()
                    _json_http(sock, response(True, "bluebridge", "Mouse setting saved", mouse=result))
                except Exception as mouse_error:
                    _json_http(sock, response(False, "error", str(mouse_error)), "400 Bad Request")
                return
            if request_path in ("/api/bluebridge/lightbar/palette","/api/bluebridge/lightbar/controller"):
                if method != "POST":
                    _json_http(sock,response(False,"error","POST required"),"405 Method Not Allowed")
                    return
                try:
                    if not bluebridge.request_json("HELLO").get("capabilities",{}).get("ds4_lightbar"):
                        raise ValueError("This firmware does not advertise DS4 light-bar support")
                    payload=json.loads(request_body.decode("utf-8") or "{}")
                    result=save_lightbar_palette(bluebridge,payload) if request_path.endswith("/palette") else save_lightbar_controller(bluebridge,payload)
                    _json_http(sock,response(True,"bluebridge","Colours saved",lightbar=result))
                except Exception as lightbar_error:
                    _json_http(sock,response(False,"error",str(lightbar_error)),"400 Bad Request")
                return
            if request_path == "/api/bluebridge/controllers/output":
                if method != "POST":
                    _json_http(sock,response(False,"error","POST required"),"405 Method Not Allowed")
                    return
                try:
                    payload=json.loads(request_body.decode("utf-8") or "{}")
                    settings=save_controller_output(bluebridge,payload)
                    _json_http(sock,response(True,"bluebridge","Output override saved",settings=settings))
                except Exception as output_error:
                    _json_http(sock,response(False,"error",str(output_error)),"400 Bad Request")
                return
            if request_path == "/api/bluebridge/output":
                try:
                    if method == "POST":
                        payload = json.loads(request_body.decode("utf-8") or "{}")
                        mode = validate_output_mode(bluebridge, payload.get("mode"))
                        bluebridge.request("OUTPUT_SET", mode)
                        bluebridge.close()
                        _json_http(sock, response(True, "bluebridge", "OK", output={"mode": mode, "name": OUTPUT_NAMES[mode]}))
                    else:
                        _json_http(sock, response(True, "bluebridge", "OK", output=bluebridge.request_json("OUTPUT_GET")))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
            if request_path == "/api/bluebridge/config/reset":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    _reset_bluebridge_configuration(bluebridge)
                    _json_http(sock, response(True, "bluebridge", "Configuration reset"))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "503 Service Unavailable")
                return
            if request_path == "/api/bluebridge/config/export":
                try:
                    package = bluebridge.export_config()
                    body = json.dumps(package, indent=2).encode("utf-8")
                    send_http(sock, "200 OK", "application/json; charset=utf-8", body, ["Content-Disposition: attachment; filename=MC-BlueBridge-Backup.bbconfig"])
                except Exception as e:
                    send_http(sock, "503 Service Unavailable", "text/plain; charset=utf-8", str(e).encode("utf-8"))
                return
            if request_path == "/api/bluebridge/config/import":
                if method != "POST":
                    _json_http(sock, response(False, "error", "POST required"), "405 Method Not Allowed")
                    return
                try:
                    package = json.loads(request_body.decode("utf-8") or "{}")
                    bluebridge.import_config(package)
                    _json_http(sock, response(True, "bluebridge", "Configuration imported"))
                except Exception as e:
                    _json_http(sock, response(False, "error", str(e)), "400 Bad Request")
                return
    send_http(sock, '404 Not Found', 'text/plain; charset=utf-8', b'Not found')


def _json_http(sock, payload, status='200 OK'):
    send_http(sock, status, 'application/json; charset=utf-8', json.dumps(payload).encode('utf-8'))

APP_ROOT = Path(__file__).resolve().parent
DATA_ROOT = Path(os.environ.get('BLUEBRIDGE_DATA_DIR', '/userdata/system/configs/bluebridge'))
BLUEBRIDGE_FIRMWARE_UPLOAD = str(DATA_ROOT / 'bluebridge_update.uf2')
BLUEBRIDGE_PRE_UPDATE_BACKUP = str(DATA_ROOT / 'MC-BlueBridge-Pre-Update.bbconfig')
PID_FILE = DATA_ROOT / 'daemon.pid'


def process_identity(pid):
    try:
        fields = Path('/proc/%d/stat' % pid).read_text().rsplit(')', 1)[1].split()
        return fields[19]
    except (OSError, IndexError):
        return None


def active_pid():
    try:
        record = json.loads(PID_FILE.read_text())
        pid = int(record['pid'])
        if record.get('boot') != Path('/proc/sys/kernel/random/boot_id').read_text().strip(): return None
        if pid <= 1 or process_identity(pid) != record['start']: return None
        arguments = Path('/proc/%d/cmdline' % pid).read_bytes().split(b'\0')
        if str(APP_ROOT / 'bluebridge_daemon.py').encode() not in arguments: return None
        return pid
    except (OSError, ValueError, KeyError, TypeError):
        return None


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def handle_request(self):
        self.close_connection = True
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 0 or length > 8 * 1024 * 1024:
                send_http(self.connection, '413 Content Too Large', 'text/plain', b'Request too large')
                return
            self.connection.settimeout(20)
            body = self.rfile.read(length)
            if len(body) != length: raise ValueError('Incomplete request')
            headers = {key.lower(): value for key, value in self.headers.items()}
            dispatch(self.connection, self.command, self.path, headers, body)
        except Exception as exc:
            try: _json_http(self.connection, response(False, 'error', str(exc)), '400 Bad Request')
            except OSError: pass

    def log_message(self, fmt, *args):
        print('%s %s' % (self.log_date_time_string(), fmt % args), flush=True)


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def serve():
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    with open(DATA_ROOT / 'running.lock', 'a') as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: raise RuntimeError('BlueBridge daemon already running')
        config_path = DATA_ROOT / 'config.json'
        config = json.loads(config_path.read_text()) if config_path.exists() else {}
        host = config.get('host', '0.0.0.0')
        port = int(config.get('port', 9191))
        if not 1 <= port <= 65535: raise ValueError('Invalid port')
        server = Server((host, port), Handler)
        pid = os.getpid()
        PID_FILE.write_text(json.dumps({'pid': pid, 'start': process_identity(pid), 'boot': Path('/proc/sys/kernel/random/boot_id').read_text().strip()}))
        def shutdown(_signum, _frame):
            threading.Thread(target=server.shutdown, daemon=True).start()
        signal.signal(signal.SIGTERM, shutdown)
        signal.signal(signal.SIGINT, shutdown)
        print('MC BlueBridge Batocera v%s listening on http://%s:%d' % (DAEMON_VERSION, host, port), flush=True)
        try: server.serve_forever()
        finally:
            server.server_close()
            bluebridge_registry.close()
            if active_pid() == pid: PID_FILE.unlink(missing_ok=True)


def control(action):
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    with open(DATA_ROOT / 'control.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        pid = active_pid()
        if action == 'status':
            print('Running (PID %d)' % pid if pid else 'Stopped')
            return 0 if pid else 1
        if action in ('stop', 'restart') and pid:
            os.kill(pid, signal.SIGTERM)
            deadline = time.monotonic() + 12
            while active_pid() == pid and time.monotonic() < deadline: time.sleep(0.1)
            if active_pid() == pid: raise RuntimeError('Daemon is still stopping; retry shortly')
            pid = None
        if action == 'stop': return 0
        if pid:
            print('Already running (PID %d)' % pid)
            return 0
        with open(DATA_ROOT / 'bluebridge.log', 'ab') as log:
            child = subprocess.Popen([sys.executable, str(APP_ROOT / 'bluebridge_daemon.py')], stdout=log, stderr=log, start_new_session=True)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if child.poll() is not None: raise RuntimeError('Daemon failed to start; see ' + str(DATA_ROOT / 'bluebridge.log'))
            if active_pid() == child.pid:
                print('Started (PID %d)' % child.pid)
                return 0
            time.sleep(0.1)
        raise RuntimeError('Daemon startup timed out; see ' + str(DATA_ROOT / 'bluebridge.log'))


def main():
    parser = argparse.ArgumentParser(description='MC BlueBridge web daemon for Batocera')
    parser.add_argument('--version', action='version', version=DAEMON_VERSION)
    parser.add_argument('--control', choices=('start', 'stop', 'restart', 'status'))
    args = parser.parse_args()
    try:
        if args.control: return control(args.control)
        serve()
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
