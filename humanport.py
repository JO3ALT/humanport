#!/usr/bin/env python3
"""Minimal in-memory HumanPort MCP server with a single Tkinter window."""
import json, queue, sys, threading, uuid, tkinter as tk
from tkinter import ttk, messagebox

tasks=queue.Queue(); pending={}; lock=threading.Lock()
TOOLS=["human.request","human.await","human.get","human.cancel","human.list","human.capabilities","human.answer"]

def request(a):
    t=dict(a.get("task",a)); tid=str(uuid.uuid4()); t.update(task_id=tid,status="pending");
    with lock: pending[tid]=t
    tasks.put(tid); return t
def get(tid):
    with lock:
        if tid not in pending: raise ValueError("TASK_NOT_FOUND")
        return pending[tid]
def answer(a,status="answered"):
    with lock:
        t=pending.get(a["task_id"])
        if not t: raise ValueError("TASK_NOT_FOUND")
        if t.get("status")!="pending": raise ValueError("ALREADY_COMPLETED")
        t.update(status=status,values=a.get("values",{}),actor=a.get("actor","human:local-user")); return t
def call(name,a):
    if name=="human.request": return request(a)
    if name=="human.get": return get(a["task_id"])
    if name=="human.answer": return answer(a)
    if name=="human.cancel": return answer(a,"cancelled")
    if name=="human.list": return list(pending.values())
    if name=="human.capabilities": return {"tools":TOOLS}
    if name=="human.await":
        t=get(a["task_id"])
        if t.get("status")=="pending": raise TimeoutError("WAIT_TIMEOUT")
        return t
    raise ValueError("METHOD_NOT_FOUND")
def mcp():
    for line in sys.stdin:
        try:
            r=json.loads(line); m=r.get("method"); rid=r.get("id")
            if m=="initialize": out={"protocolVersion":"2025-03-26","capabilities":{"tools":{}},"serverInfo":{"name":"HumanPort","version":"0.2.0"}}
            elif m=="notifications/initialized": continue
            elif m=="tools/list": out={"tools":[{"name":n,"description":n,"inputSchema":{"type":"object"}} for n in TOOLS]}
            elif m=="tools/call": out={"content":[{"type":"text","text":json.dumps(call(r["params"]["name"],r["params"].get("arguments",{})),ensure_ascii=False)}]}
            else: raise ValueError("METHOD_NOT_FOUND")
            print(json.dumps({"jsonrpc":"2.0","id":rid,"result":out},ensure_ascii=False),flush=True)
        except Exception as e: print(json.dumps({"jsonrpc":"2.0","id":r.get("id"),"error":{"code":-32000,"message":str(e)}},ensure_ascii=False),flush=True)
class App:
    def __init__(self,root):
        self.root=root; root.title("HumanPort"); root.geometry("520x320"); self.current=None; self.poll()
    def poll(self):
        if not self.current:
            try: self.current=get(tasks.get_nowait())
            except queue.Empty: pass
        if self.current: self.show(self.current)
        else: self.root.after(300,self.poll)
    def show(self,t):
        w=tk.Toplevel(self.root); w.title(t.get("title","HumanPort")); w.geometry("520x330"); w.update_idletasks(); w.geometry(f"520x330+{(w.winfo_screenwidth()-520)//2}+{(w.winfo_screenheight()-330)//2}"); ttk.Label(w,text=t.get("title",""),font=("TkDefaultFont",14,"bold")).pack(pady=10); ttk.Label(w,text=t.get("prompt",""),wraplength=470).pack(pady=8); v=tk.StringVar()
        if t.get("kind")=="input":
            box=tk.Text(w,height=8,width=58); box.pack(pady=8); box.focus_set(); ttk.Button(w,text="送信",command=lambda:self.submit(t,box.get("1.0","end-1c"),w)).pack(pady=8)
        else:
            for x in t.get("choices") or [{"value":"yes","label":"はい"},{"value":"no","label":"いいえ"}]: ttk.Radiobutton(w,text=x.get("label",x.get("value")),variable=v,value=x.get("value")).pack(anchor="w",padx=40)
            ttk.Button(w,text="送信",command=lambda:self.submit(t,v.get(),w)).pack(pady=8)
        self.window=w
    def submit(self,t,value,w):
        if not value.strip(): messagebox.showwarning("HumanPort","入力してください",parent=w); return
        answer({"task_id":t["task_id"],"values":{"text":value} if t.get("kind")=="input" else {"decision":value}}); w.destroy(); self.current=None; self.root.after(300,self.poll)
if __name__=="__main__": threading.Thread(target=mcp,daemon=True).start(); root=tk.Tk(); root.withdraw(); App(root); root.mainloop()
